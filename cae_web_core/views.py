"""
Views for CAE_Web Core App.
"""

import dateutil.parser
import json
import pytz
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import format_html

from . import models
from cae_home.models import Room


def index(request):
    """
    Root project url.
    """
    return TemplateResponse(request, 'cae_web_core/index.html', {})


#region Employee Views

@login_required
def my_hours(request):
    """
    Employee shift page for an individual.
    """
    shifts = models.EmployeeShift.objects.filter(employee=request.user)

    # Convert to json format for React.
    json_shifts = serializers.serialize(
        'json',
        shifts,
        fields=('clock_in', 'clock_out', 'date_created', 'date_modified',)
    )

    return TemplateResponse(request, 'cae_web_core/employee/my_hours.html', {
        'shifts': shifts,
        'json_shifts': json_shifts,
        'last_shift': shifts.first(),
    })

#endregion Employee Views


#region Calendar Views

def calendar_test(request):
    rooms = Room.objects.all().order_by('room_type', 'name').values_list(
        'pk', 'name', 'capacity',
    )
    now = timezone.now() # UTC
    now = pytz.timezone('America/Detroit').localize(now.replace(tzinfo=None)) # EST/EDT
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


@login_required
def api_room_schedule(request):
    """Get room events"""
    start = request.GET.get('startdate', None)
    end = request.GET.get('enddate', None)
    room = request.GET.get('room', None)

    events = models.RoomEvent.objects.all().order_by('room', 'start')

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
