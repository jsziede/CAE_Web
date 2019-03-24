"""
Form views for CAE Web Core app.
"""
import datetime

from dateutil import rrule
from django import forms
from django.core.validators import FileExtensionValidator
from django.db import transaction
from django.utils import timezone
import pytz

from cae_home.models.wmu import SemesterDate, Room
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
    name = forms.CharField()
    semester = forms.ModelChoiceField(
        SemesterDate.objects.all().order_by('-start_date'),
        help_text="Specifies the start and end dates for the events.")
    schedule = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])])
    overwrite = forms.BooleanField(required=False)

    def clean(self):
        """Verify if overwrite is required."""
        if self.errors:
            return
        cleaned_data = super().clean()

        name = self.cleaned_data['name']
        overwrite = self.cleaned_data['overwrite']

        if models.UploadedSchedule.objects.filter(name=name).exists() and not overwrite:
            raise forms.ValidationError("That name is already in use. Please check overwrite if you want to replace previous events.")

        return cleaned_data


    @transaction.atomic()
    def save(self):
        """Parse and create events"""
        if not self.is_valid():
            raise Exception("Form must be valid")
        name = self.cleaned_data['name']
        schedule = self.cleaned_data['schedule']
        semester = self.cleaned_data['semester']
        overwrite = self.cleaned_data['overwrite']

        exists = models.UploadedSchedule.objects.filter(name=name).exists()

        if exists and not overwrite:
            # Catches a race condition between clean() and save() where it suddenly exists now.
            raise forms.ValidationError("That name is already in use, and overwrite was not True.")
        elif exists and overwrite:
            uploaded_schedule = models.UploadedSchedule.objects.get(name=name)
            uploaded_schedule.events.all().delete()
            uploaded_schedule.delete()

        uploaded_schedule = models.UploadedSchedule.objects.create(
            name=name,
        )

        events = excel.upload_room_schedule(schedule.read())

        valid_events = [] # (room_name, title, start, end, weekdays)
        error_events = [] # (room_name, title, start, end, weekdays, error_msg)
        db_events = []

        for (room_name, title, start, end), weekdays in events.items():
            room = Room.objects.filter(
                name=room_name,
            ).first()
            if not room:
                error_events.append((room_name, title, start, end, weekdays, "Unable to find room {0!r}.".format(room_name)))
                continue

            start_time = datetime.datetime.combine(semester.start_date, start)
            end_time = datetime.datetime.combine(semester.end_date, end)
            duration = datetime.datetime.combine(semester.start_date, end) - start_time

            # Make the times Eastern Time, then convert to UTC for rrule
            start_time = timezone.make_aware(start_time, timezone=pytz.timezone("America/Detroit")).astimezone(pytz.utc)
            end_time = timezone.make_aware(end_time, timezone=pytz.timezone("America/Detroit")).astimezone(pytz.utc)

            # TODO: The socket controller needs to read rrules and generate 'events' for the client js to use.
            # This also means that editing an event will be a little more complicated if it's from an rrule.

            rrule_weekdays = [None, rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA, rrule.SU]

            converted_days = [rrule_weekdays[x] for x in weekdays]

            # NOTE: rrule does not have duration!
            rule = rrule.rrule(rrule.WEEKLY, byweekday=converted_days, dtstart=start_time, until=end_time)

            event = models.RoomEvent.objects.create(
                room=room,
                start_time=start_time,
                end_time=end_time,
                title=title,
                rrule=str(rule),
                duration=duration,
            )
            db_events.append(event)
            valid_events.append((room_name, title, start, end, weekdays))

        uploaded_schedule.events.add(*db_events)

        return valid_events, error_events
