"""
Consumers for CAE Web Core app.
"""

from channels.generic.websocket import JsonWebsocketConsumer
from django.core import serializers
from django.utils import timezone

from . import models


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

        # Attempt to get "shift_submit" value. Defaults to None.
        shift_submit = content.get('shift_submit', None)

        if shift_submit:
            # Check if shift already exists. If not, start new one.
            shift = models.EmployeeShift.objects.filter(employee=user).last()
            if shift.clock_out is None:
                shift.clock_out = timezone.now()
                shift.save()
            else:
                shift = models.EmployeeShift.objects.create(
                    employee=user,
                    clock_in=timezone.now(),
                )
                shift.save()

            # Respond to client with updated model info.
            shifts = models.EmployeeShift.objects.filter(employee=user)
            json_shifts = serializers.serialize(
                'json',
                shifts,
                fields=('clock_in', 'clock_out', 'date_created', 'date_modified',)
            )

            # Send data.
            self.send_json({
                'json_shifts': json_shifts,
            })
