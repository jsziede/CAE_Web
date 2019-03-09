"""
Consumers for CAE Web Core app.
"""

# System Imports.
import dateutil.parser, pytz
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.utils import timezone

# User Class Imports.
from . import models
from .views import populate_pay_periods


channel_layer = get_channel_layer()


ACTION_GET_EVENTS = 'get-events'
ACTION_SEND_EVENTS = 'send-events'
GROUP_UPDATE_ROOM_EVENT = "on-update-room-event"


class MyHoursConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        """
        Handling for initial socket connection attempt.
        """
        # Check if user is logged in. Reject if not.
        if self.scope['user'].is_anonymous:
            print('Rejected {0}.'.format(self.scope['user']))
            await self.close()
        else:
            print('Connected - {0}.'.format(self.scope['user']))
            await self.accept()

    async def disconnect(self, code):
        """
        Handling for socket disconnect.
        """
        print('Disconnected with code {0} - {1}.'.format(code, self.scope['user']))

    async def receive_json(self, content, **kwargs):
        """
        Handling for json received from connection.
        """
        import traceback
        try:
            print('\n\nReceiving JSON from {0}: {1}'.format(self.scope['user'], content))

            # Check for valid pay periods.
            populate_pay_periods()

            print('Action is {0}'.format(content['action']))

            # Attempt given action.
            if content['action'] == ACTION_GET_EVENTS:
                await self._get_pay_period_data(content)
                print('Action "{0}" done.'.format(ACTION_GET_EVENTS))
            elif content['action'] == ACTION_SEND_EVENTS:
                # Check for shift submission.
                if 'submit_shift' in content:
                    await self._submit_shift(content)
                else:
                    await self._get_pay_period_data(content)
                print('Action "{0}" done.'.format(ACTION_SEND_EVENTS))
            else:
                print('Unexpected action.')
        except:
            traceback.print_exc()
            await self.disconnect(-1)
        # await self.disconnect(1)

    #     handlers = {
    #         ACTION_GET_EVENTS: self.handle_get_events,
    #     }
    #     # print('Idk: {0}'.format(handlers))
    #
    #     action = content.get('action')
    #     print('Received Action: {0}'.format(action))
    #     handler = handlers.get(action)
    #     print('Handler: {0}'.format(handler))
    #
    #     if handler:
    #         try:
    #             await handler(content)
    #         except ValueError as err:
    #             await self.send_json({
    #                 'error': 'Value Error: {0!r}'.format(str(err))
    #             })
    #         else:
    #             await self.send_json({
    #                 'error': 'Invalid Action: {0!r}'.format(action)
    #             })
    #
    # async def handle_get_events(self, content):
    #     print('Handling event. Got this content: {0}'.format(content))

        # start = content.get('start_time')
        # end = content.get('end_time')
        # room = content.get('room')
        # notify = content.get('notify')
        #
        # events = await self._get_events(start, end, room)
        #
        # await self.send_json({
        #     'action': self.ACTION_SEND_EVENTS,
        #     'start': start.isoformat() if start else None,
        #     'end': end.isoformat() if end else None,
        #     'events': events,
        # })


    async def _get_pay_period_data(self, content):
        """
        Get Data for given shift.
        Note that this logic assumes that pay periods are arranged by successive pk, due to nature of auto-creating.
        If a pay_period model is ever deleted or otherwise changed, then the database should be manually corrected.
        """
        user = self.scope['user']
        pay_period_pk = content.get('pay_period_pk', None)
        notify = content.get('notify', False)

        # Validate passed pk.
        if pay_period_pk is None or not isinstance(pay_period_pk, int):
            pay_period_pk = await self._get_current_pay_period_model_pk(timezone.now())

        # Validation for pk going below 0 or above model count.
        pay_period_count = await self._get_pay_period_model_count()
        if pay_period_pk < 1:
            pay_period_pk = pay_period_count
        elif pay_period_pk > pay_period_count:
            pay_period_pk = 1

        # Get indicated pay period and associated shifts.
        pay_period = await self._get_pay_period_model(pay_period_pk)
        shifts = await self._get_shift_models(pay_period)
        try:
            last_shift = await self._get_last_shift_model()
        except ObjectDoesNotExist:
            last_shift = None

        # Convert to json format for React.
        json_pay_period = serializers.serialize(
            'json',
            [pay_period],
            fields=('date_start', 'date_end',)
        )

        json_shifts = serializers.serialize(
            'json',
            shifts,
            fields=('clock_in', 'clock_out',)
        )

        if last_shift:
            json_last_shift = serializers.serialize(
                'json',
                [last_shift],
                fields=('clock_in', 'clock_out')
            )
        else:
            json_last_shift = last_shift

        # Send data.
        await self.send_json({
            'pay_period': json_pay_period,
            'shifts': json_shifts,
            'last_shift': json_last_shift,
        })

        # if notify:
        #     self.scope['session']['pks'] = [shift['id'] for shift in shifts]
        #     await self.channel_layer.group_add(
        #
        #     )

    async def _submit_shift(self, content):
        """
        Submits shift for user at current time.
        """
        # Update current shift.
        current_time = timezone.now()
        pay_period = await self._get_current_pay_period_model(current_time)
        await self._update_employee_shift_model(pay_period, timezone.now())

        # Refresh pay period data and resend to user.
        await self._get_pay_period_data(content)

    @database_sync_to_async
    def _get_current_pay_period_model(self, current_time):
        return models.PayPeriod.objects.get(date_start__lte=current_time, date_end__gte=current_time)

    @database_sync_to_async
    def _get_current_pay_period_model_pk(self, current_time):
        return models.PayPeriod.objects.get(date_start__lte=current_time, date_end__gte=current_time).pk

    @database_sync_to_async
    def _get_pay_period_model_count(self):
        return models.PayPeriod.objects.all().count()

    @database_sync_to_async
    def _get_pay_period_model(self, pk):
        return  models.PayPeriod.objects.get(pk=pk)

    @database_sync_to_async
    def _get_last_shift_model(self):
        return models.EmployeeShift.objects.filter(employee=self.scope['user']).last()

    @database_sync_to_async
    def _get_shift_models(self, pay_period):
        return models.EmployeeShift.objects.filter(employee=self.scope['user'], pay_period=pay_period)

    @database_sync_to_async
    def _update_employee_shift_model(self, pay_period, current_time):
        # Check if shift already exists. If not, start new one.
        shift = models.EmployeeShift.objects.filter(employee=self.scope['user'], clock_out=None).first()
        if shift is not None and shift.clock_out is None:
            shift.clock_out = current_time
            shift.save()
        else:
            shift = models.EmployeeShift.objects.create(
                pay_period=pay_period,
                employee=self.scope['user'],
                clock_in=current_time,
            )
            shift.save()


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
            'description': description,
            'event_type': event_type,
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
