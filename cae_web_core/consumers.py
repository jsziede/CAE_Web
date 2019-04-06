"""
Consumers for CAE Web Core app.
"""

# System Imports.
import dateutil.parser, pytz
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from dateutil import rrule
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete
from django.utils import timezone

# User Class Imports.
from . import models
from . import forms
from .views import populate_pay_periods


channel_layer = get_channel_layer()


ACTION_GET_EVENTS = 'get-events'
ACTION_SEND_EVENTS = 'send-events'
GROUP_UPDATE_ROOM_EVENT = "on-update-room-event"
GROUP_UPDATE_AVAILABILITY_EVENT = "on-update-availability-event"


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
            current_date = timezone.now().date() # Assuming settings.TIME_ZONE is America/Detroit
            pay_period_pk = await self._get_current_pay_period_model_pk(current_date)

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
        current_date = timezone.now().date() # Assuming settings.TIME_ZONE is America/Detroit
        pay_period = await self._get_current_pay_period_model(current_date)
        await self._update_employee_shift_model(pay_period, timezone.now())

        # Refresh pay period data and resend to user.
        await self._get_pay_period_data(content)

    @database_sync_to_async
    def _get_current_pay_period_model(self, current_date):
        return models.PayPeriod.objects.get(date_start__lte=current_date, date_end__gte=current_date)

    @database_sync_to_async
    def _get_current_pay_period_model_pk(self, current_date):
        return models.PayPeriod.objects.get(date_start__lte=current_date, date_end__gte=current_date).pk

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

    MODE_ROOMS = 'rooms'
    MODE_AVAILABILITY = 'availability'

    async def connect(self):
        #print("CONNECT:", self.scope['user'])

        await self.accept()

    async def disconnect(self, code):
        #print("DISCONNECT ({}):".format(code), self.scope['user'])
        pass

    async def receive_json(self, content, **kwargs):
        #print("{}: {}".format(self.scope['user'], content))

        handlers = {
            self.ACTION_GET_EVENTS: self._handle_get_events,
        }

        action = content.get('action')
        handler = handlers.get(action)

        if handler:
            try:
                await handler(content)
            except ValueError as err:
                print(err)
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
        mode = content.get('mode')

        if start:
            start = dateutil.parser.parse(start)
            if timezone.is_naive(start):
                raise ValueError("start_time is naive")

        if end:
            end = dateutil.parser.parse(end)
            if timezone.is_naive(end):
                raise ValueError("end_time is naive")

        if mode == self.MODE_ROOMS:
            await self._handle_get_room_events(content, start, end)
        elif mode == self.MODE_AVAILABILITY:
            await self._handle_get_availability_events(content, start, end)
        else:
            raise ValueError("mode is missing or invalid")

    async def _handle_get_room_events(self, content, start, end):
        room = content.get('room')
        room_type_slug = content.get('resource_identifier')
        notify = content.get('notify')

        events = await self._get_room_events(start, end, room, room_type_slug)

        await self.send_json({
            'action': self.ACTION_SEND_EVENTS,
            'start': start.isoformat() if start else None,
            'end': end.isoformat() if end else None,
            'resource_identifier': room_type_slug,
            'events': events,
        })

        if notify:
            self.scope['session']['start'] = start.isoformat() if start else None
            self.scope['session']['end'] = end.isoformat() if end else None
            self.scope['session']['room'] = room
            self.scope['session']['resource_identifier'] = room_type_slug
            self.scope['session']['pks'] = [x['id'] for x in events]
            await self.channel_layer.group_add(
                GROUP_UPDATE_ROOM_EVENT, self.channel_name)

    async def _handle_get_availability_events(self, content, start, end):
        employee = content.get('employee')
        employee_type_pk = content.get('resource_identifier')
        notify = content.get('notify')

        events = await self._get_availability_events(start, end, employee, employee_type_pk)

        await self.send_json({
            'action': self.ACTION_SEND_EVENTS,
            'start': start.isoformat() if start else None,
            'end': end.isoformat() if end else None,
            'resource_identifier': employee_type_pk,
            'events': events,
        })

        if notify:
            self.scope['session']['start'] = start.isoformat() if start else None
            self.scope['session']['end'] = end.isoformat() if end else None
            self.scope['session']['employee'] = employee
            self.scope['session']['resource_identifier'] = employee_type_pk
            self.scope['session']['pks'] = [x['id'] for x in events]
            await self.channel_layer.group_add(
                GROUP_UPDATE_AVAILABILITY_EVENT, self.channel_name)

    async def on_update_room_event(self, content):
        room = self.scope['session'].get('room')
        room_type_slug = self.scope['session'].get('resource_identifier')
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
                #print("end was before start")
                pass
            elif end and event_start > end:
                # ignore
                #print("start was after end")
                pass
            elif room and content['room'] != room:
                # ignore
                #print("Room not equal")
                pass
            else:
                notify_user = True

        if notify_user:
            await self._handle_get_room_events({
                'start_time': self.scope['session'].get('start'),
                'end_time': self.scope['session'].get('end'),
                'room': room,
                'resource_identifier': room_type_slug,
                'notify': True,
            }, event_start, event_end)

    @database_sync_to_async
    def _get_room_events(self, start, end, room, room_type_slug):
        """Get room events"""
        events = models.RoomEvent.objects.all().order_by('room', 'start_time')

        if room:
            events = events.filter(room_id=room)

        if room_type_slug:
            events = events.filter(room__room_type__slug=room_type_slug)

        if start:
            events = events.filter(end_time__gte=start)

        if end:
            events = events.filter(start_time__lte=end)

        event_types = models.RoomEventType.objects.all().values(
            'pk',
            'name',
            'fg_color',
            'bg_color',
        )
        event_types = {x['pk']: x for x in event_types}

        events = events.values(
            'pk', 'room', 'event_type', 'start_time', 'end_time', 'title',
            'description', 'rrule', 'duration', 'exclusions',
        )

        event_dicts = self._convert_events_to_dicts(
            events, event_types, start, end, 'room')

        return event_dicts

    @database_sync_to_async
    def _get_availability_events(self, start, end, employee, employee_type_pk):
        """Get room events"""
        events = models.AvailabilityEvent.objects.all().order_by('employee', 'start_time')

        if employee:
            events = events.filter(employee__pk=employee)

        if employee_type_pk:
            events = events.filter(employee__groups=employee_type_pk)

        if start:
            events = events.filter(end_time__gte=start)

        if end:
            events = events.filter(start_time__lte=end)

        event_types = models.AvailabilityEventType.objects.all().values(
            'pk',
            'name',
            'fg_color',
            'bg_color',
        )
        event_types = {x['pk']: x for x in event_types}

        events = events.values(
            'pk', 'employee', 'event_type', 'start_time', 'end_time', 'rrule', 'duration', 'exclusions',
        )

        event_dicts = self._convert_events_to_dicts(
            events, event_types, start, end, 'employee')

        return event_dicts

    def _convert_events_to_dicts(self, events, event_types, start, end, resource_key):
        event_dicts = []

        # Convert to format expected by schedule.js
        for event in events:
            if not event['rrule']:
                # Simple event
                event_dicts.append({
                    'id': event['pk'],
                    'resource': event[resource_key],
                    'start': event['start_time'].isoformat(),
                    'end': event['end_time'].isoformat(),
                    'event_type': event_types[event['event_type']],
                    'title': event.get('title'),
                    'description': event.get('description'),
                })
            else:
                # Need to generate events using rrule, within start and end
                # Convert time to EST and make naive to prevent DST from affecting event times
                dtstart = timezone.make_naive(event['start_time'], timezone=pytz.timezone("America/Detroit"))
                until = timezone.make_naive(event['end_time'], timezone=pytz.timezone("America/Detroit"))
                # Override 'dtstart' and 'until' in case event model was changed but rrule was not.
                new_starts = rrule.rrulestr(event['rrule']).replace(dtstart=dtstart, until=until)

                rrule_form_data = forms.RRuleFormMixin.rrule_get_form_data(new_starts)

                # Get list of dates that have been excluded
                exclusions = event['exclusions'].value

                for i, new_start in enumerate(new_starts):
                    # Convert time back to aware and then to UTC for the client.
                    new_start = timezone.make_aware(new_start, timezone=pytz.timezone("America/Detroit")).astimezone(pytz.utc)
                    if new_start < start or new_start > end or new_start in exclusions:
                        continue
                    new_end = new_start + event['duration']
                    event_dicts.append({
                        'id': event['pk'],
                        'rrule': rrule_form_data,
                        'rrule_index': i,
                        'resource': event[resource_key],
                        'start': new_start.isoformat(),
                        'end': new_end.isoformat(),
                        'orig_start': event['start_time'].isoformat(),
                        'orig_end': (event['start_time'] + event['duration']).isoformat(),
                        'event_type': event_types[event['event_type']],
                        'title': event.get('title'),
                        'description': event.get('description'),
                    })

        return event_dicts

def on_room_event_changed(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance:
        # NOTE: if deleted, insance is no longer in database
        async_to_sync(channel_layer.group_send)(
            GROUP_UPDATE_ROOM_EVENT,
            {
                "type": "on_update_room_event",
                "pk": instance.pk,
                "start_time": instance.start_time.isoformat(),
                "end_time": instance.end_time.isoformat(),
                "room": instance.room_id,
            },
        )

post_save.connect(on_room_event_changed, sender=models.RoomEvent)
post_delete.connect(on_room_event_changed, sender=models.RoomEvent)
