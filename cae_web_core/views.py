"""
Views for CAE_Web Core App.
"""
import json

from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.template.response import TemplateResponse
from django.utils.html import format_html

import dateutil.parser
import pytz

from .models import Room, RoomEvent


def index(request):
    """
    Root project url.
    """
    return TemplateResponse(request, 'cae_web_core/index.html', {})


def calendar_test(request):
    rooms = Room.objects.all().order_by('room_type', 'name').values_list(
        'pk', 'name', 'capacity',
    )
    events = RoomEvent.objects.all().order_by('room', 'start')

    rooms_json = []
    for pk, name, capacity in rooms:
        rooms_json.append({
            'id': pk,
            'html': format_html('{}<br>{}'.format(name, capacity)),
        })

    return TemplateResponse(request, 'cae_web_core/calendar_test.html', {
        'rooms': rooms,
        'rooms_json': json.dumps(rooms_json),
        'events': events,
    })


@login_required
def api_room_schedule(request):
    """Get room events"""
    start = request.GET.get('startdate', None)
    end = request.GET.get('enddate', None)
    room = request.GET.get('room', None)

    events = RoomEvent.objects.all().order_by('room', 'start')

    if room:
        events = events.filter(room_id=room)

    user_timezone = request.user.profile.user_timezone

    if start:
        start = dateutil.parser.parse(start)
        if start.tzinfo is None or start.utcoffset is None:
            start = start.replace(tzinfo=pytz.timezone(user_timezone))
        events = events.filter(start__gte=start)

    if end:
        end = dateutil.parser.parse(end)
        if end.tzinfo is None or end.utcoffset is None:
            end = end.replace(tzinfo=pytz.timezone(user_timezone))
        events = events.filter(end__lte=end)

    events = events.values_list(
        'pk', 'room_id', 'event_type', 'start', 'end', 'title', 'description', 'rrule',
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
