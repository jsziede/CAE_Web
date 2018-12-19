"""
Views for CAE Work Log app.
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
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
    log_sets = models.WorkLogSet.objects.all()
    log_entries = models.WorkLogEntry.objects.all()

    # Send to template for user display.
    return render(request, 'cae_work_log/index.html', {
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

    for group in user.groups.all():
        if 'CAE Admin' == group.name or 'CAE Programmer' == group.name:
            default_group = group
    timeframe = models.TimeFrameType.objects.filter(id=2)

    if default_group is not None:
        log_set = models.WorkLogSet.objects.get(timeframe_type=timeframe, group=default_group)

    form = forms.LogEntryForm(
        initial={
            'user': user,
            'entry_date': entry_date,
            'log_set': log_set,
        }
    )

    # Check if request is post.
    if request.method == 'POST':
        form = forms.LogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save()

            # Render response for user.
            return HttpResponseRedirect(reverse('cae_work_log:index'))

    # Handle for non-post request.
    return render(request, 'cae_work_log/log_entry_form.html', {
        'form': form,
    })

