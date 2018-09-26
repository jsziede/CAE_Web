"""
Consumers for CAE Web Core app.
"""

# System Imports.
import pytz
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import (
    AsyncJsonWebsocketConsumer,
    JsonWebsocketConsumer,
)
from channels.layers import get_channel_layer
import dateutil.parser
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.utils import timezone

# User Class Imports.
from . import models
from .views import populate_pay_periods
from cae_home import models as cae_home_models


channel_layer = get_channel_layer()

GROUP_UPDATE_ROOM_EVENT = "on-update-room-event"


class MyHoursConsumer(JsonWebsocketConsumer):
    def connect(self):
        """
        Handling for initial socket connection attempt.
        """
        # Check if user is logged in. Reject if not.
        if self.scope['user'].is_anonymous:
            self.close()
        else:
            self.accept()

    def disconnect(self, code):
        """
        Handling for socket disconnect.
        """
        pass

    def receive_json(self, content, **kwargs):
        """
        Handling for json received from connection.
        """
        # Grab user.
        user = self.scope['user']
        populate_pay_periods()

        # Attempt to get "shift_submit" value. Defaults to None.
        shift_submit = content.get('shift_submit', None)
        if shift_submit:
            self.shift_submit(user)

        # Attempt to get "pay_period" int value. Defaults to None.
        pay_period_pk = content.get('pay_period', None)
        if isinstance(pay_period_pk, int):
            self.load_pay_period(user, pay_period_pk)

    def shift_submit(self, user):
        """
        Handling for user submitting shift clock in/clock out.
        """
        # Get current pay period.
        current_time = timezone.now()
        pay_period = models.PayPeriod.objects.get(period_start__lte=current_time, period_end__gte=current_time)

        # Check if shift already exists. If not, start new one.
        shift = models.EmployeeShift.objects.filter(employee=user, clock_out=None).first()
        if shift is not None and shift.clock_out is None:
            shift.clock_out = timezone.now()
            shift.save()

        else:
            shift = models.EmployeeShift.objects.create(
                pay_period=pay_period,
                employee=user,
                clock_in=timezone.now(),
            )
            shift.save()

        # Respond to client with updated model info.
        shifts, last_shift = self.get_shifts(user, pay_period)

        # Convert shift values to user's local time.
        user_timezone = pytz.timezone(cae_home_models.Profile.objects.get(user=user).user_timezone)
        for shift in shifts:
            shift.clock_in = user_timezone.normalize(shift.clock_in.astimezone(user_timezone))
            if shift.clock_out is not None:
                shift.clock_out = user_timezone.normalize(shift.clock_out.astimezone(user_timezone))

        # Convert to json format for React.
        json_shifts = serializers.serialize(
            'json',
            shifts,
            fields=('clock_in', 'clock_out',)
        )

        json_last_shift = serializers.serialize(
            'json',
            [last_shift],
            fields=('clock_in', 'clock_out',)
        )

        # Send data.
        self.send_json({
            'json_shifts': json_shifts,
            'json_last_shift': json_last_shift,
        }, close=True)

    def get_shifts(self, user, pay_period):
        """
        Gets last shift with given pay period.
        """
        shifts = models.EmployeeShift.objects.filter(employee=user, pay_period=pay_period)

        # Try to get shift with no clock out. If none exist, then use last shift in current pay period.
        try:
            last_shift = models.EmployeeShift.objects.get(employee=user, clock_out=None)
        except ObjectDoesNotExist:
            last_shift = shifts.last()

        return (shifts, last_shift)

    def load_pay_period(self, user, pay_period_pk):
        """
        Handling for user requesting new pay period to view.
        """
        # Validation for pk going below 0 or above model count.
        pay_period_count = models.PayPeriod.objects.all().count()
        if pay_period_pk < 1:
            pay_period_pk = pay_period_count
        elif pay_period_pk > pay_period_count:
            pay_period_pk = 1

        # Get indicated pay period and associated shifts.
        pay_period = models.PayPeriod.objects.get(pk=pay_period_pk)
        shifts = models.EmployeeShift.objects.filter(employee=user, pay_period=pay_period)

        # Convert to json format for React.
        json_pay_period = serializers.serialize(
            'json',
            [pay_period],
            fields=('period_start', 'period_end',)
        )

        json_shifts = serializers.serialize(
            'json',
            shifts,
            fields=('clock_in', 'clock_out',)
        )

        # Send data.
        self.send_json({
            'json_pay_period': json_pay_period,
            'json_shifts': json_shifts,
        }, close=True)


class ScheduleConsumer(AsyncJsonWebsocketConsumer):
    ACTION_GET_EVENTS = 'get-events'
    ACTION_SEND_EVENTS = 'send-events'
    async def connect(self):
        print("CONNECT:", self.scope['user'])

        await self.accept()

    async def disconnect(self, code):
        print("DISCONNECT ({}):".format(code), self.scope['user'])

    async def receive_json(self, content, **kwargs):
        print("{}: {}".format(self.scope['user'], content))

        handlers = {
            self.ACTION_GET_EVENTS: self._handle_get_events,
        }

        action = content.get('action')
        handler = handlers.get(action)

        if handler:
            try:
                await handler(content)
            except ValueError as err:
                await self.send_json({
                    'error': "Value Error: {!r}".format(str(err)),
                })
        else:
            await self.send_json({
                'error': "Invalid action: {!r}".format(action),
            })

    async def _handle_get_events(self, content):
        start = content.get('start_time')
        end = content.get('end_time')
        room = content.get('room')
        notify = content.get('notify')

        if start:
            start = dateutil.parser.parse(start)
            if timezone.is_naive(start):
                raise ValueError("start_time is naive")

        if end:
            end = dateutil.parser.parse(end)
            if timezone.is_naive(end):
                raise ValueError("end_time is naive")

        events = await self._get_events(start, end, room)

        await self.send_json({
            'action': self.ACTION_SEND_EVENTS,
            'start': start.isoformat() if start else None,
            'end': end.isoformat() if end else None,
            'events': events,
        })

        if notify:
            self.scope['session']['start'] = start.isoformat() if start else None
            self.scope['session']['end'] = end.isoformat() if end else None
            self.scope['session']['room'] = room
            self.scope['session']['pks'] = [x['id'] for x in events]
            await self.channel_layer.group_add(
                GROUP_UPDATE_ROOM_EVENT, self.channel_name)

    async def on_update_room_event(self, content):
        room = self.scope['session'].get('room')
        event_start = dateutil.parser.parse(content['start_time'])
        event_end = dateutil.parser.parse(content['end_time'])

        notify_user = False
        if content['pk'] in self.scope['session'].get('pks', []):
            notify_user = True
        else:
            # Check if new event within time frame
            start = self.scope['session'].get('start')
            if start:
                start = dateutil.parser.parse(start)
            end = self.scope['session'].get('end')
            if end:
                end = dateutil.parser.parse(end)

            if start and event_end < start:
                # ignore
                print("end was before start")
                pass
            elif end and event_start > end:
                # ignore
                print("start was after end")
                pass
            elif room and content['room'] != room:
                # ignore
                print("Room not equal")
                pass
            else:
                notify_user = True

        if notify_user:
            await self._handle_get_events({
                'start_time': self.scope['session'].get('start'),
                'end_time': self.scope['session'].get('end'),
                'room': room,
                'notify': True,
            })

    @database_sync_to_async
    def _get_events(self, start, end, room):
        """Get room events"""
        events = models.RoomEvent.objects.all().order_by('room', 'start_time')

        if room:
            events = events.filter(room_id=room)

        if start:
            events = events.filter(end_time__gte=start)

        if end:
            events = events.filter(start_time__lte=end)

        events = events.values_list(
            'pk', 'room_id', 'event_type', 'start_time', 'end_time', 'title',
            'description', 'rrule',
        )

        # Convert to format expected by schedule.js
        events = [{
            'id': pk,
            'resource': room_id,
            'start': start.isoformat(),
            'end': end.isoformat(),
            'title': title,
            'description': description
        } for pk, room_id, event_type, start, end, title, description, rrule in events]

        return events

def on_room_event_changed(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance:
        # NOTE: if deleted, insance is no longer in database
        async_to_sync(channel_layer.group_send)(
            GROUP_UPDATE_ROOM_EVENT,
            {
                "type": "on.update.room_event",
                "pk": instance.pk,
                "start_time": instance.start_time.isoformat(),
                "end_time": instance.end_time.isoformat(),
                "room": instance.room_id,
            },
        )

post_save.connect(on_room_event_changed, sender=models.RoomEvent)
post_delete.connect(on_room_event_changed, sender=models.RoomEvent)
