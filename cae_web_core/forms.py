"""
Form views for CAE Web Core app.
"""

from django import forms
from django.core.validators import FileExtensionValidator

from . import models
from .utils import excel


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
    room_event_pk = forms.IntegerField(widget=forms.HiddenInput, required=False)
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


class UploadRoomScheduleForm(forms.Form):
    # TODO: Add name field to use for uploaded schedule model
    schedule = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])])

    def save(self):
        if not self.is_valid():
            raise Exception("Form must be valid")
        schedule = self.cleaned_data['schedule']

        return excel.upload_room_schedule(schedule.read())
