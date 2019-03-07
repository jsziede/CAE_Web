"""
Form views for CAE Web Core app.
"""

from django import forms

from . import models


class EmployeeShiftForm(forms.ModelForm):
    """
    Define form view for Employee Shift.
    """
    class Meta:
        model = models.EmployeeShift
        fields = {
            'employee',
            'pay_period',
            'clock_in',
            'clock_out',
        }


class RoomEventForm(forms.ModelForm):
    room_event_pk = forms.IntegerField(widget=forms.HiddenInput)
    class Meta:
        model = models.RoomEvent
        fields = [
            'title',
            'start_time',
            'end_time',
            'rrule',
            'description',
            'event_type',
            'room',
        ]
