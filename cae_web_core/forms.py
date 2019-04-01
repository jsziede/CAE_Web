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
        widgets = {
            'clock_in': forms.widgets.SplitDateTimeWidget(
                date_attrs={'type': 'date'},
                time_attrs={'type': 'time'},
            ),
            'clock_out': forms.widgets.SplitDateTimeWidget(
                date_attrs={'type': 'date'},
                time_attrs={'type': 'time'},
            ),
        }
        field_classes = {
            'clock_in': forms.SplitDateTimeField,
            'clock_out': forms.SplitDateTimeField,
        }


class RRuleFormMixin(forms.Form):
    REPEAT_NEVER = 0
    REPEAT_DAILY = 1
    REPEAT_WEEKLY = 2
    REPEAT_CHOICES = (
        (REPEAT_NEVER, "Never"),
        (REPEAT_DAILY, "Daily"),
        (REPEAT_WEEKLY, "Weekly"),
    )
    END_NEVER = 0
    END_AFTER = 1
    END_ON = 2
    END_CHOICES = (
        (END_NEVER, "Never"),
        (END_AFTER, "After"),
        (END_ON, "On"),
    )
    DAY_CHOICES = (
        (7, "Su"),
        (1, "Mo"),
        (2, "Tu"),
        (3, "We"),
        (4, "Th"),
        (5, "Fr"),
        (6, "Sa"),
    )
    rrule_repeat = forms.TypedChoiceField(
        choices=REPEAT_CHOICES, coerce=int, initial=REPEAT_NEVER, label="Repeat")
    rrule_count = forms.IntegerField(min_value=1, initial=1, label="Count")
    rrule_weekly_on = forms.TypedMultipleChoiceField(
        choices=DAY_CHOICES, coerce=int, widget=forms.widgets.CheckboxSelectMultiple(),
        label="Repeat On", required=False)
    rrule_end = forms.TypedChoiceField(
        choices=END_CHOICES, coerce=int, initial=END_NEVER, widget=forms.widgets.RadioSelect(),
        label="End")
    rrule_end_after = forms.IntegerField(min_value=1, initial=1, label="After")
    rrule_end_on = forms.DateField(
        label="On", initial=lambda: timezone.now().date())

    class RRuleMedia:
        """Subclasses should explicitly import these"""
        js = ("cae_web_core/js/rrule_form.js",)

    def rrule_clean(self):
        """
        Subclasses should call this method in their clean() methods.
        """
        repeat = self.cleaned_data.get('rrule_repeat')
        weekly_on = self.cleaned_data.get('rrule_weekly_on')

        if repeat == self.REPEAT_WEEKLY and not weekly_on:
            self.add_error('rrule_repeat', "Days must be chosen if repeating Weekly.")

    def rrule_get_string(self):
        """
        Return an RRULE string from form data.
        """
        if not self.is_valid():
            raise Exception("Form must be valid")


class RoomEventForm(forms.ModelForm, RRuleFormMixin):
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
    class Media:
        js = RRuleFormMixin.RRuleMedia.js

    def clean(self):
        super().rrule_clean()


class AvailabilityEventForm(forms.ModelForm, RRuleFormMixin):
    availability_event_pk = forms.IntegerField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = models.AvailabilityEvent
        fields = [
            'start_time',
            'end_time',
            'rrule',
            'event_type',
            'employee',
        ]
    class Media:
        js = RRuleFormMixin.RRuleMedia.js

    def clean(self):
        super().rrule_clean()


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

        # TODO: Make this a system setting?
        # Or allow user to choose?
        event_type = models.RoomEventType.objects.get(name="Class")

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
                event_type=event_type,
            )
            db_events.append(event)
            valid_events.append((room_name, title, start, end, weekdays))

        uploaded_schedule.events.add(*db_events)

        return valid_events, error_events
