"""
Models for CAE Web Core app.
"""

import datetime, math, pytz
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from .fields import DatetimeListField


MAX_LENGTH = 255


class PayPeriod(models.Model):
    """
    An instance of a two week pay period.
    """
    # Model fields.
    date_start = models.DateField(unique=True)
    date_end = models.DateField(blank=True, unique=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pay Period"
        verbose_name_plural = "Pay Periods"
        ordering = ('-date_start',)

    def __str__(self):
        return '{0} - {1}'.format(self.date_start, self.date_end)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        if self.date_end is None:
            end_datetime = self.get_start_as_datetime() + datetime.timedelta(days=13)
            end_date = end_datetime.date()
            self.date_end = end_date

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(PayPeriod, self).save(*args, **kwargs)

    def get_start_as_datetime(self):
        """
        Returns start date at exact midnight, local time.
        """
        midnight = datetime.time(0, 0, 0, 0)
        start_datetime = pytz.timezone('America/Detroit').localize(datetime.datetime.combine(self.date_start, midnight))
        return start_datetime

    def get_end_as_datetime(self):
        """
        Returns end date just before midnight of next day, local time.
        """
        day_end = datetime.time(23, 59, 59)
        end_datetime = pytz.timezone('America/Detroit').localize(datetime.datetime.combine(self.date_end, day_end))
        return end_datetime


class EmployeeShift(models.Model):
    """
    An instance of an employee clocking in and out for a shift.
    """
    # Relationship keys.
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pay_period = models.ForeignKey('PayPeriod', on_delete=models.CASCADE)
    error_flag = models.BooleanField(default=False)

    # Model fields.
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(blank=True, null=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee Shift"
        verbose_name_plural = "Employee Shifts"
        ordering = ('clock_in', 'clock_out',)
        unique_together = (
            ('employee', 'clock_in',),
            ('employee', 'clock_out',),
        )

    def __str__(self):
        return '{0}: {1} to {2}'.format(self.employee, self.clock_in, self.clock_out)

    def get_absolute_url(self):
        return reverse('cae_web_core:shift_edit', kwargs={
            'pk': self.pk,
        })

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # Check that clock_out time is after clock_in time.
        if self.clock_in is not None and self.clock_out is not None:
            if (self.clock_out == self.clock_in) or (self.clock_out < self.clock_in):
                raise ValidationError('Clock out time must be after clock in time.')

        # Check that clock times do not overlap previous shifts for user.
        # Check clock in is not inside other shift.
        if self.clock_in is not None:
            previous_shifts = EmployeeShift.objects.filter(
                employee=self.employee,
                clock_in__lte=self.clock_in,
                clock_out__gte=self.clock_in
            ).exclude(id=self.id)
            if len(previous_shifts) is not 0:
                raise ValidationError('Users cannot have overlapping shift times.')

        if self.clock_out is not None:
            # Check clock out is not inside other shift.
            previous_shifts = EmployeeShift.objects.filter(
                employee=self.employee,
                clock_in__lte=self.clock_out,
                clock_out__gte=self.clock_out
            ).exclude(id=self.id)
            if len(previous_shifts) is not 0:
                raise ValidationError('Users cannot have overlapping shift times.')

            # Check old shift is not entirely inside new shift.
            previous_shifts = EmployeeShift.objects.filter(
                employee=self.employee,
                clock_in__gte=self.clock_in,
                clock_out__lte=self.clock_out
            ).exclude(id=self.id)
            if len(previous_shifts) is not 0:
                raise ValidationError('Users cannot have overlapping shift times.')

        # Check that clock times are inside provided pay period.
        # Check clock in times. Shift just started so there's no data to lose. Raise validation error.
        if (self.clock_in < self.pay_period.get_start_as_datetime()) or\
                (self.clock_in > self.pay_period.get_end_as_datetime()):
            raise ValidationError('Shift must be between pay period dates. Double check that you\'re using the correct'
                                  'pay period.')
        # Check if clock out time spans multiple pay periods. Since we don't want to lose shift data, flag as error.
        if (self.clock_out is not None) and (self.clock_out > self.pay_period.get_end_as_datetime()):
            self.error_flag = True

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(EmployeeShift, self).save(*args, **kwargs)

    def get_time_worked(self):
        """
        Calculates total time worked, both total seconds and h/m/s.
        :return: Tuple of (total_seconds, (hours, minutes, seconds)) worked.
        """
        if self.clock_out is not None:
            return self.clock_out.timestamp() - self.clock_in.timestamp()
        else:
            return timezone.now().timestamp() - self.clock_in.timestamp()

    def get_time_worked_as_decimal(self, total_seconds=None):
        """
        Gets hours worked, in decimal format.
        :param total_seconds:
        :return: Decimal of hours worked.
        """
        # Populate seconds if none was provided.
        if total_seconds is None:
            total_seconds = self.get_time_worked()

        return round((total_seconds / 60 / 60), 2)

    def get_time_worked_as_hms(self, total_seconds=None):
        """
        Gets hours worked, in h/m/s format.
        :param total_seconds: Total time worked in seconds. Defaults
        :return: Tuple of hours, minutes, and seconds worked.
        """
        # Populate seconds if none was provided.
        if total_seconds is None:
            total_seconds = self.get_time_worked()

        total_minutes = total_seconds / 60
        total_hours = total_minutes / 60
        hours = math.trunc(total_hours)
        minutes = math.trunc(total_minutes - (hours * 60))
        seconds = math.trunc(total_seconds - (minutes * 60) - (hours * 60 * 60))

        return (hours, minutes, seconds)


class AbstractEvent(models.Model):
    """
    Abstract Model for Events. Models that inherit this class will also have these fields.
    """
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    # rrule means Recurrence rule
    # See https://dateutil.readthedocs.io/en/stable/rrule.html
    rrule = models.TextField(
        blank=True,
        help_text="Note: DTSTART and UNTIL will be replaced by Start Time and End Time, respectively."
    )
    duration = models.DurationField(
        blank=True, null=True, help_text="Used only with rrules.")
    exclusions = DatetimeListField(
        blank=True, help_text="Newline separated list of isoformat datetimes to exclude.")

    class Meta:
        abstract = True


class RoomEventTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        """Allow fixtures to refer to Room Event Types by name instead of pk"""
        return self.get(name=name)


class RoomEventType(models.Model):
    """
    A type for a Room Event. Used to specify the event colors.
    """
    name = models.CharField(max_length=MAX_LENGTH, unique=True)
    fg_color = models.CharField(
        default='black',
        help_text="Foreground css color. E.g. 'red' or '#FF0000'",
        max_length=30)
    bg_color = models.CharField(
        default='lightgoldenrodyellow',
        help_text="Foreground css color. E.g. 'red' or '#FF0000'",
        max_length=30)

    objects = RoomEventTypeManager()

    class Meta:
        verbose_name = "Room Event Type"
        verbose_name_plural = "Room Event Types"

    def __str__(self):
        return self.name


class RoomEvent(AbstractEvent):
    """
    A schedule "event" for a room. IE: The room is reserved for a class, meeting, etc.
    """
    # Relationship keys.
    room = models.ForeignKey('cae_home.Room', on_delete=models.CASCADE)
    event_type = models.ForeignKey(
        RoomEventType,
        on_delete=models.PROTECT, # Prevent deleting types if event exists
    )

    # Model fields.
    title = models.CharField(max_length=MAX_LENGTH)
    description = models.TextField(blank=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room Event"
        verbose_name_plural = "Room Events"
        ordering = ('room', 'event_type', 'start_time', 'end_time')
        unique_together = (
            ('room', 'start_time', 'rrule'),
            ('room', 'end_time', 'rrule'),
        )

    def __str__(self):
        return '{0} {1}: {2} - {3}, {4}'.format(
            self.room, self.event_type, self.start_time, self.end_time, self.title,
        )

    def clean(self, *args, **kwargs):
        """
        Verify there are no overlapping events.
        """
        if not self.rrule:
            # Verify no event is within start and end
            non_rrule_events = RoomEvent.objects.filter(
                room=self.room,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                rrule='',
            ).exclude(
                pk=self.pk,
            )
            # TODO: Check rrule events
            if non_rrule_events.exists():
                raise ValidationError("Room Events can't overlap.")
        else:
            # Verify no event falls on an event from our rrule
            pass # TODO: evaluate the rrule, and check
        return super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)


class AvailabilityEventTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        """Allow fixtures to refer to Availability Event Types by name instead of pk"""
        return self.get(name=name)


class AvailabilityEventType(models.Model):
    """
    A type for a Availability Event. Used to specify the event colors.
    """
    name = models.CharField(max_length=MAX_LENGTH, unique=True)
    fg_color = models.CharField(
        blank=True,
        help_text="Foreground css color. E.g. 'red' or '#FF0000'",
        max_length=30)
    bg_color = models.CharField(
        blank=True,
        help_text="Foreground css color. E.g. 'red' or '#FF0000'",
        max_length=30)

    objects = AvailabilityEventTypeManager()

    class Meta:
        verbose_name = "Availability Event Type"
        verbose_name_plural = "Availability Event Types"

    def __str__(self):
        return self.name


class AvailabilityEvent(AbstractEvent):
    """
    A schedule "event" for an employee. E.g. Person is unavailable from 5:30 - 6:30.
    """
    # Relationship keys.
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_type = models.ForeignKey(
        AvailabilityEventType,
        on_delete=models.PROTECT, # Prevent deleting types if event exists
    )

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Availability Event"
        verbose_name_plural = "Availability Events"
        ordering = ('employee', 'event_type', 'start_time', 'end_time')
        unique_together = (
            ('employee', 'start_time', 'rrule'),
            ('employee', 'end_time', 'rrule'),
        )

    def clean(self, *args, **kwargs):
        """
        Verify there are no overlapping events.
        """
        if not self.rrule:
            # Verify no event is within start and end
            non_rrule_events = AvailabilityEvent.objects.filter(
                employee=self.employee,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time,
                rrule='',
            ).exclude(
                pk=self.pk,
            )
            # TODO: Check rrule events
            if non_rrule_events.exists():
                raise ValidationError("Availability Events can't overlap.")
        else:
            # Verify no event falls on an event from our rrule
            pass # TODO: evaluate the rrule, and check
        return super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super().save(*args, **kwargs)


class UploadedSchedule(models.Model):
    """
    Represents an uploaded schedule instance.

    Used to delete all events associated with a schedule.
    """
    name = models.CharField(max_length=MAX_LENGTH, unique=True)
    events = models.ManyToManyField(RoomEvent, related_name='+')

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
