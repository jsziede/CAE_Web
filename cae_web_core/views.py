"""
Views for CAE_Web Core App.
"""

# System Imports.
import datetime, dateutil.parser, json, pytz
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

# User Class Imports.
from . import forms, models
from cae_home import models as cae_home_models


#region Standard Methods

def populate_pay_periods():
    """
    Handles creation of pay periods. Should be called any time a pay period is accessed in a view, prior to view logic.

    This checks if a valid (pay_period + 1) is present for the current date.
        If so, it does nothing.
        If not, then it populates new pay periods from last one found, to one pay period past present date.

        On the chance that no pay periods are found, then populates starting from 05-25-2015 (the first known valid pay
        period in production data, as of writing this).

    Note: Checks for (pay_period + 1) to guarantee no errors, even on the unlikely case of a user loading a view just as
    the pay period changes over.
    """
    pay_period_found = True
    server_timezone = pytz.timezone('UTC')
    local_timezone = pytz.timezone('America/Detroit')
    current_time = timezone.now().astimezone(server_timezone)
    plus_1_time = current_time + timezone.timedelta(days=14)

    # Check for current pay period.
    try:
        models.PayPeriod.objects.get(date_start__lte=current_time, date_end__gte=current_time)

        # Check for current pay period + 1.
        try:
            models.PayPeriod.objects.get(date_start__lte=plus_1_time, date_end__gte=plus_1_time)
        except ObjectDoesNotExist:
            pay_period_found = False
    except ObjectDoesNotExist:
        pay_period_found = False

    # If both pay periods were not found, create new pay periods.
    if not pay_period_found:
        try:
            last_pay_period = models.PayPeriod.objects.latest('date_start')
        except models.PayPeriod.DoesNotExist:
            last_pay_period = None

        # If no pay periods found, manually create first one at 5-25-2015.
        if last_pay_period is None:
            # Get desired start date from string.
            unaware_date = datetime.datetime.strptime('2015 05 25 00 00 00', '%Y %m %d %H %M %S')
            local_date = local_timezone.localize(unaware_date)
            last_pay_period = models.PayPeriod.objects.create(date_start=local_date)

        # Continue until pay_period + 1 is created.
        while not ((last_pay_period.get_start_as_datetime() < plus_1_time) and (last_pay_period.get_end_as_datetime() > plus_1_time)):
            utc_date = last_pay_period.get_start_as_datetime().astimezone(server_timezone) + timezone.timedelta(14)
            local_date = utc_date.astimezone(local_timezone)
            last_pay_period = models.PayPeriod.objects.create(date_start=local_date)

#endregion Standard Methods


def index(request):
    """
    Root project url.
    Displays contact info of current CAE Director and Associated Building Coordinators.
    If user is logged in and admin or programmer, also shows contact info of other admins/programmers.
    """
    try:
        cae_phone_number = cae_home_models.PhoneNumber.objects.get(pk=1)
    except ObjectDoesNotExist:
        cae_phone_number = None
    cae_directors = cae_home_models.User.objects.filter(groups__name='CAE Director')
    cae_coordinators = cae_home_models.User.objects.filter(groups__name='CAE Building Coordinator')
    cae_attendants = None
    cae_admins = None
    cae_programmers = None

    if request.user.is_authenticated:
        if request.user.groups.filter(name='CAE Attendant') or request.user.groups.filter(name='CAE Admin') or request.user.groups.filter(name='CAE Programmer'):
            cae_attendants = cae_home_models.User.objects.filter(groups__name='CAE Attendant')
            cae_admins = cae_home_models.User.objects.filter(groups__name='CAE Admin')
            cae_programmers = cae_home_models.User.objects.filter(groups__name='CAE Programmer')

    return TemplateResponse(request, 'cae_web_core/index.html', {
        'cae_phone_number': cae_phone_number,
        'cae_directors': cae_directors,
        'cae_coordinators': cae_coordinators,
        'cae_attendants': cae_attendants,
        'cae_admins': cae_admins,
        'cae_programmers': cae_programmers,
    })


#region Employee Views

@login_required
def my_hours(request):
    """
    Employee shift page for an individual.
    """
    # Check for valid pay periods.
    populate_pay_periods()

    # Send to template for user display.
    return TemplateResponse(request, 'cae_web_core/employee/my_hours.html', {})


def shift_edit(request, pk):
    """
    Edit view for a single shift.
    :param request:
    :return:
    """
    # Pull models from database.
    shift = get_object_or_404(models.EmployeeShift, id=pk)
    form = forms.EmployeeShiftForm(instance=shift)

    # Check if request is post.
    if request.method == 'POST':
        form = forms.EmployeeShiftForm(instance=shift, data=request.POST)
        if form.is_valid():
            shift = form.save()

            # Render response for user.
            messages.success(request, 'Successfully updated shift ({0})'.format(shift))
            return HttpResponseRedirect(reverse('cae_web_core:shift_manager_redirect'))
        else:
            messages.warning(request, 'Failed to update shift.')

    # Handle for non-post request.
    return TemplateResponse(request, 'cae_web_core/employee/shift_edit.html', {
        'form': form,
        'shift': shift,
    })


@login_required
def shift_manager_redirect(request):
    """
    Redirects to shift of current date. Used in app nav.
    """
    # Check for valid pay periods.
    populate_pay_periods()

    pay_period_pk = models.PayPeriod.objects.all()[1].pk
    return redirect('cae_web_core:shift_manager', pk=pay_period_pk)


@login_required
def shift_manager(request, pk):
    """
    Page to view, manage, and print all shifts in a given pay period.
    """
    # Check for valid pay periods.
    populate_pay_periods()

    # Pull models from database.
    pay_period = get_object_or_404(models.PayPeriod, pk=pk)
    complex_query = (
        (
            Q(groups__name='CAE Attendant') | Q(groups__name='CAE Admin') | Q(groups__name='CAE Programmer')
        )
        & Q(is_active=True)
    )
    users = get_user_model().objects.filter(complex_query).order_by('last_name', 'first_name')
    shifts = models.EmployeeShift.objects.filter(pay_period=pay_period, employee__in=users)

    # Determine pay period pks. First/Last query calls are reverse due to ordering.
    first_valid_pk = models.PayPeriod.objects.last().pk
    last_valid_pk = models.PayPeriod.objects.first().pk
    curr_pay_period = models.PayPeriod.objects.all()[1].pk

    # Calculate previous pk (necessary if pay periods are ever deleted).
    prev_found = False
    prev_pay_period = int(pk)
    while not prev_found:
        prev_found = True
        prev_pay_period -= 1

        # Check edge case.
        if prev_pay_period < first_valid_pk:
            prev_pay_period = last_valid_pk

        # Check if pay period with pk exists. Necessary if pay periods are ever deleted.
        try:
            models.PayPeriod.objects.get(pk=prev_pay_period)
        except models.PayPeriod.DoesNotExist:
            prev_found = False

    # Calculate next pk.
    next_found = False
    next_pay_period = int(pk)
    while not next_found:
        next_found = True
        next_pay_period += 1

        # Check edge case.
        if next_pay_period > last_valid_pk:
            next_pay_period = first_valid_pk

        # Check if pay period with pk exists. Necessary if pay periods are ever deleted.
        try:
            models.PayPeriod.objects.get(pk=next_pay_period)
        except models.PayPeriod.DoesNotExist:
            next_found = False

    return TemplateResponse(request, 'cae_web_core/employee/shift_manager.html', {
        'users': users,
        'pay_period': pay_period,
        'shifts': shifts,
        'prev_pay_period': prev_pay_period,
        'curr_pay_period': curr_pay_period,
        'next_pay_period': next_pay_period,
    })

#endregion Employee Views


#region Calendar Views


def room_schedule(request):
    rooms = cae_home_models.Room.objects.all().order_by('room_type', 'name').values_list(
        'pk', 'name', 'capacity',
    )
    now = timezone.now() # UTC
    now = now.astimezone(pytz.timezone('America/Detroit')) # EST/EDT
    start = now.replace(hour=8, minute=0, second=0)
    end = now.replace(hour=22, minute=0, second=0)

    rooms_json = []
    for pk, name, capacity in rooms:
        rooms_json.append({
            'id': pk,
            'html': format_html('{}<br>{}'.format(name, capacity)),
        })

    return TemplateResponse(request, 'cae_web_core/room_schedule/room_schedule.html', {
        'rooms': rooms,
        'rooms_json': json.dumps(rooms_json),
        'start': start,
        'end': end,
    })

def calendar_test(request):
    rooms = cae_home_models.Room.objects.all().order_by('room_type', 'name').values_list(
        'pk', 'name', 'capacity',
    )
    now = timezone.now() # UTC
    now = now.astimezone(pytz.timezone('America/Detroit')) # EST/EDT
    start = now.replace(hour=8, minute=0, second=0)
    end = now.replace(hour=22, minute=0, second=0)

    rooms_json = []
    for pk, name, capacity in rooms:
        rooms_json.append({
            'id': pk,
            'html': format_html('{}<br>{}'.format(name, capacity)),
        })

    return TemplateResponse(request, 'cae_web_core/calendar_test.html', {
        'rooms': rooms,
        'rooms_json': json.dumps(rooms_json),
        'start': start,
        'end': end,
    })


def api_room_schedule(request):
    """Get room events"""
    start = request.GET.get('startdate', None)
    end = request.GET.get('enddate', None)
    room = request.GET.get('room', None)

    events = models.RoomEvent.objects.all().order_by('room', 'start_time')

    if room:
        events = events.filter(room_id=room)

    user_timezone = request.user.profile.user_timezone

    if start:
        start = dateutil.parser.parse(start)
        if start.tzinfo is None or start.utcoffset is None:
            start = start.replace(tzinfo=pytz.timezone(user_timezone))
        events = events.filter(start_time__gte=start)

    if end:
        end = dateutil.parser.parse(end)
        if end.tzinfo is None or end.utcoffset is None:
            end = end.replace(tzinfo=pytz.timezone(user_timezone))
        events = events.filter(end_time__lte=end)

    events = events.values_list(
        'pk', 'room_id', 'event_type', 'start_time', 'end_time', 'title',
        'description', 'rrule',
    )

    # Convert to format expected by schedule.js
    events = [{
        'id': pk,
        'resource': room_id,
        'start': start,
        'end': end,
        'title': title,
        'description': description
    } for pk, room_id, event_type, start, end, title, description, rrule in events]

    return JsonResponse({
        'start': start,
        'end': end,
        'events': events,
    })

#endregion Calendar Views
