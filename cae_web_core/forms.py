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

from . import models
from .utils import excel
from cae_home import forms as cae_home_forms
from cae_home.models.wmu import SemesterDate, Room


class EmployeeShiftForm(forms.ModelForm):
    """
    Define form view for Employee Shift.
    """
    class Meta:
        model = models.EmployeeShift
        fields = [
            'employee',
            'pay_period',
            'clock_in',
            'clock_out',
        ]
        widgets = {
            'clock_in': cae_home_forms.DateTimePickerWidget,
            'clock_out': cae_home_forms.DateTimePickerWidget,
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
    rrule_interval = forms.IntegerField(min_value=1, initial=1, label="Interval")
    rrule_weekly_on = forms.TypedMultipleChoiceField(
        choices=DAY_CHOICES, coerce=int, widget=forms.widgets.CheckboxSelectMultiple(),
        label="Repeat On", required=False)
    rrule_end = forms.TypedChoiceField(
        choices=END_CHOICES, coerce=int, initial=END_NEVER, widget=forms.widgets.RadioSelect(),
        label="End")
    rrule_end_after = forms.IntegerField(min_value=1, initial=1, label="After")
    rrule_end_on = forms.DateField(
        label="On", initial=lambda: timezone.localdate())
    pk = forms.IntegerField(widget=forms.HiddenInput, required=False)
    parent_pk = forms.IntegerField(widget=forms.HiddenInput, required=False)
    exclusion = forms.DateTimeField(widget=forms.HiddenInput, required=False)
    delete = forms.BooleanField(widget=forms.HiddenInput, required=False)

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

        if self.errors:
            return
        # The following assumes parent classes have defined start_time, end_time, and duration

        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')

        new_rrule, new_end_time = self.rrule_get_string(start_time)
        self.cleaned_data['rrule'] = new_rrule

        if new_rrule:
            duration = end_time - start_time
            # Change end time to encompass the entire rrule
            self.cleaned_data['end_time'] = new_end_time
            self.cleaned_data['duration'] = duration

        parent_pk = self.cleaned_data.get('parent_pk')
        exclusion = self.cleaned_data.get('exclusion')

        if parent_pk:
            # Verify parent pk is an AvailabilityEvent
            parent = self._meta.model.objects.filter(pk=parent_pk).first()
            if not parent:
                self.add_error("parent_pk", "Invalid Availability Event pk")

        if parent_pk and not exclusion:
            self.add_error(None, "Exclusion date is required with parent_pk")

    @transaction.atomic
    def rrule_save(self, *args, **kwargs):
        # Check if parent and exclusion were given to update the parent
        parent_pk = self.cleaned_data.get('parent_pk')
        exclusion = self.cleaned_data.get('exclusion')
        parent = self._meta.model.objects.filter(pk=parent_pk).first()
        if parent:
            exclusions = parent.exclusions.value
            exclusions.append(exclusion)
            parent.save(update_fields=['exclusions'])

    def rrule_get_string(self, dtstart):
        """
        Return an RRULE string from form data.
        """
        if not self.is_valid():
            raise Exception("Form must be valid")
        repeat = self.cleaned_data['rrule_repeat']
        interval = self.cleaned_data['rrule_interval']
        weekly_on = self.cleaned_data['rrule_weekly_on']
        end = self.cleaned_data['rrule_end']
        end_after = self.cleaned_data['rrule_end_after']
        end_on = self.cleaned_data['rrule_end_on']

        if repeat == self.REPEAT_NEVER:
            return "", None # No rrule necessary

        # Make the times Eastern Time, then convert to UTC for rrule
        dtstart = dtstart.astimezone(pytz.utc)
        end_time = datetime.datetime.combine(end_on, datetime.time(11, 59))
        end_time = timezone.make_aware(end_time, timezone=pytz.timezone("America/Detroit")).astimezone(pytz.utc)

        rrule_weekdays = [None, rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA, rrule.SU]

        converted_days = [rrule_weekdays[x] for x in weekly_on]

        kwargs = {
            'freq': rrule.DAILY if repeat == self.REPEAT_DAILY else rrule.WEEKLY,
            'dtstart': dtstart,
            'interval': interval,
            'count': end_after if end == self.END_AFTER else None,
            'until': end_time if end == self.END_ON else None,
            'byweekday': converted_days if repeat == self.REPEAT_WEEKLY else None,
        }

        rule = rrule.rrule(**kwargs)

        new_end_time = None
        if end == self.END_ON:
            new_end_time = end_time
        elif end == self.END_NEVER:
            # Keep None
            pass
        else:
            # Need to compute last date
            new_end_time = list(rule)[-1]

        return str(rule), new_end_time

    @classmethod
    def rrule_get_form_data(cls, rule):
        """
        Used by consumers socket to give client js form data.

        See rrule_form.js rruleSetFromFormData().
        """
        repeat = {
            rrule.DAILY: cls.REPEAT_DAILY,
            rrule.WEEKLY: cls.REPEAT_WEEKLY,
        }[rule._freq]

        end = cls.END_NEVER
        end_on = timezone.localdate()
        end_after = 1
        if rule._until:
            end = cls.END_ON
            end_on = rule._until
        if rule._count:
            end = cls.END_AFTER
            end_after = rule._count

        weekly_on = []
        if rule._byweekday:
            # Convert rrule weekday to our weekday
            rrule_weekdays = [None, rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR, rrule.SA, rrule.SU]
            rrule_weekdays = [x.weekday if x else None for x in rrule_weekdays]

            weekly_on = [rrule_weekdays.index(x) for x in rule._byweekday]

        form_data = {
            'id_rrule_repeat': repeat,
            'id_rrule_interval': rule._interval,
            'id_rrule_weekly_on': weekly_on,
            'id_rrule_end': end,
            'id_rrule_end_after': end_after,
            'id_rrule_end_on': end_on.strftime('%Y-%m-%d'),
        }

        return form_data


class RoomEventForm(forms.ModelForm, RRuleFormMixin):
    class Meta:
        model = models.RoomEvent
        fields = [
            'title',
            'start_time',
            'end_time',
            'rrule',
            'duration',
            'description',
            'event_type',
            'room',
        ]
    class Media:
        js = RRuleFormMixin.RRuleMedia.js

    def __init__(self, user, *args, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        super().rrule_clean()

        delete = self.cleaned_data.get('delete')
        if delete and not self._user.has_perm('cae_web_core.delete_roomevent'):
            self.add_error(None, "You don't have permission to delete Room Events")

        if self.instance and not self.instance.pk and not self._user.has_perm('cae_web_core.add_roomevent'):
            self.add_error(None, "You don't have permission to create Room Events")

        if self.instance and self.instance.pk and not self._user.has_perm('cae_web_core.change_roomevent'):
            self.add_error(None, "You don't have permission to change Room Events")


    @transaction.atomic
    def save(self, *args, **kwargs):
        saved = None
        delete = self.cleaned_data.get('delete')
        if delete:
            if self.instance and self.instance.pk:
                self.instance.delete()
        else:
            saved = super().save(*args, **kwargs)

        super().rrule_save()

        return saved


class AvailabilityEventForm(forms.ModelForm, RRuleFormMixin):
    class Meta:
        model = models.AvailabilityEvent
        fields = [
            'start_time',
            'end_time',
            'rrule',
            'duration',
            'event_type',
            'employee',
        ]
    class Media:
        js = RRuleFormMixin.RRuleMedia.js

    def __init__(self, user, *args, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        super().rrule_clean()

        delete = self.cleaned_data.get('delete')
        if delete and not self._user.has_perm('cae_web_core.delete_availabilityevent'):
            self.add_error(None, "You don't have permission to delete Availability Events")

        if self.instance and not self.instance.pk and not self._user.has_perm('cae_web_core.add_availabilityevent'):
            self.add_error(None, "You don't have permission to create Availability Events")

        if self.instance and self.instance.pk and not self._user.has_perm('cae_web_core.change_availabilityevent'):
            self.add_error(None, "You don't have permission to change Availability Events")

    @transaction.atomic
    def save(self, *args, **kwargs):
        saved = None
        delete = self.cleaned_data.get('delete')
        if delete:
            if self.instance and self.instance.pk:
                self.instance.delete()
        else:
            saved = super().save(*args, **kwargs)

        super().rrule_save()

        return saved


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
