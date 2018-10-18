"""
Models for CAE Web Core app.
"""

import math
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


MAX_LENGTH = 255


class PayPeriod(models.Model):
    """
    An instance of a two week pay period.
    """
    # Model fields.
    period_start = models.DateTimeField()
    period_end = models.DateTimeField(blank=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pay Period"
        verbose_name_plural = "Pay Periods"
        ordering = ('-period_start',)

    def __str__(self):
        return '{0} - {1}'.format(self.period_start, self.period_end)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        if self.period_end is None:
            self.period_end = self.period_start + timezone.timedelta(days=14) - timezone.timedelta(milliseconds=1)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(PayPeriod, self).save(*args, **kwargs)


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

    def __str__(self):
        return '{0}: {1} to {2}'.format(self.employee, self.clock_in, self.clock_out)

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
            previous_shifts = EmployeeShift.objects.filter(clock_in__lte=self.clock_in, clock_out__gte=self.clock_in)
            if len(previous_shifts) is not 0:
                raise ValidationError('Users cannot have overlapping shift times.')

        if self.clock_out is not None:
            # Check clock out is not inside other shift.
            previous_shifts = EmployeeShift.objects.filter(clock_in__lte=self.clock_out, clock_out__gte=self.clock_out)
            if len(previous_shifts) is not 0:
                raise ValidationError('Users cannot have overlapping shift times.')

            # Check old shift is not entirely inside new shift.
            previous_shifts = EmployeeShift.objects.filter(clock_in__gte=self.clock_in, clock_out__lte=self.clock_out)
            if len(previous_shifts) is not 0:
                raise ValidationError('Users cannot have overlapping shift times.')

        # Check that clock times are inside provided pay period.
        # Check clock in times. Shift just started so there's no data to lose. Raise validation error.
        if (self.clock_in < self.pay_period.period_start) or (self.clock_in > self.pay_period.period_end):
            raise ValidationError('Shift must be between pay period dates. Double check that you\'re using the correct'
                                  'pay period.')
        # Check if clock out time spans multiple pay periods. Since we don't want to lose shift data, flag as error.
        if (self.clock_out is not None) and (self.clock_out > self.pay_period.period_end):
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
        return self.clock_out.timestamp() - self.clock_in.timestamp()

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


class RoomEvent(models.Model):
    """
    A schedule "event" for a room. IE: The room is reserved for a class, meeting, etc.
    """
    # Preset field choices.
    TYPE_CLASS = 0
    TYPE_EVENT = 1
    TYPE_CHOICES = (
        (TYPE_CLASS, "Class"),
        (TYPE_EVENT, "Event"),
    )

    # Relationship keys.
    room = models.ForeignKey('cae_home.Room', on_delete=models.CASCADE)

    # Model fields.
    event_type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        default=TYPE_CLASS,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=MAX_LENGTH)
    description = models.TextField(blank=True)
    rrule = models.TextField(   # Recurrence rule?
        blank=True,
    )

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room Event"
        verbose_name_plural = "Room Events"
        ordering = ('room', 'event_type', 'start_time', 'end_time',)

    def __str__(self):
        return '{0} {1}: {2} - {3}, {4}'.format(
            self.room, self.TYPE_CHOICES[self.event_type][1], self.start_time, self.end_time, self.title,
        )

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(RoomEvent, self).save(*args, **kwargs)
