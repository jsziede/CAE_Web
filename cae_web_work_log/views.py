"""
Views for CAE Work Log app.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone

from . import forms, models


def index(request):
    """
    Work log index view.
    """
    # Pull models from database.
    complex_query = (
        (
            Q(name="CAE Admin") | Q(name="CAE Programmer")
        )
    )
    groups = Group.objects.filter(complex_query)
    timeframes = models.TimeFrameType.objects.all()
    log_sets = models.WorkLogSet.objects.filter(group__in=groups)
    log_entries = models.WorkLogEntry.objects.filter(log_set__in=log_sets)

    # Get filter form.
    form = forms.LogFilterForm(
        groups=groups,
        timeframes=timeframes,
    )

    # Check if request is post.
    if request.method == 'POST':
        form = forms.LogFilterForm(request.POST, groups=groups, timeframes=timeframes)
        if form.is_valid():
            group_filter = form.cleaned_data['group']
            timeframe_filter = form.cleaned_data['timeframe']

            if group_filter == 'All':
                group_filter = groups
            else:
                group_filter = Group.objects.filter(name=group_filter)

            if timeframe_filter == 'All':
                timeframe_filter = timeframes
            else:
                timeframe_filter = models.TimeFrameType.objects.filter(
                    name=models.TimeFrameType.get_int_from_name(timeframe_filter)
                )

            # Update log display based on filters.
            log_sets = models.WorkLogSet.objects.filter(group__in=group_filter, timeframe_type__in=timeframe_filter)
            log_entries = models.WorkLogEntry.objects.filter(log_set__in=log_sets)

    # Handle for non-post request.
    return TemplateResponse(request, 'cae_web_work_log/index.html', {
        'form': form,
        'groups': groups,
        'timeframes': timeframes,
        'log_sets': log_sets,
        'log_entries': log_entries,
    })


@login_required
def create_entry(request):
    """
    Work log index view.
    """
    # Set initial form data.
    entry_date = timezone.now().date()
    user = request.user
    default_group = None
    log_set = None

    # Default to weekly timeframe.
    timeframe = models.TimeFrameType.objects.get(
        name=models.TimeFrameType.get_int_from_name('Weekly')
    )

    # Filter based on current user.
    for group in user.groups.all():
        if group.name == 'CAE Admin' or group.name == 'CAE Programmer':
            default_group = group

    # Get initial log set.
    if default_group is not None:
        log_set = models.WorkLogSet.objects.get(timeframe_type=timeframe, group=default_group)

    initial_data = {
        'user': user,
        'entry_date': entry_date,
        'log_set': log_set,
    }

    form = forms.LogEntryForm(initial=initial_data)

    # Limit visible log sets based on user group.
    if default_group is not None:
        visible_log_sets = models.WorkLogSet.objects.filter(group=default_group)
        form.fields['log_set'].queryset = visible_log_sets

    # Check if request is post.
    if request.method == 'POST':
        form = forms.LogEntryForm(request.POST, initial=initial_data)
        form.fields['log_set'].queryset = visible_log_sets

        if form.is_valid():
            # Check form is valid and 'hidden' fields were not changed.
            if 'user' in form.changed_data:
                messages.error(request, 'Invalid form submitted. Please try again.')

                # Reset form but save description input.
                initial_data['description'] = form.cleaned_data['description']
                form = forms.LogEntryForm(initial=initial_data)

            else:
                # Form is valid. Saving.
                entry = form.save()

                # Render response for user.
                messages.success(request, 'Successfully created log entry ({0}).'.format(entry))
                return HttpResponseRedirect(reverse('cae_web_work_log:index'))

        else:
            messages.error(request, 'Failed to create log entry.')

    # Handle for non-post request.
    return TemplateResponse(request, 'cae_web_work_log/log_entry_form.html', {
        'form': form,
    })
