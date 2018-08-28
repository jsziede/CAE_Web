"""
Models for CAE Web Core app.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


MAX_LENGTH = 255


class EmployeeShift(models.Model):
    """
    An instance of an employee clocking in and out for a shift.
    """
    # Model fields.
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(blank=True, null=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee Shift"
        verbose_name_plural = "Employee Shifts"

    def __str__(self):
        return '{0}: {1} to {2}'.format(self.employee, self.clock_in, self.clock_out)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        if self.clock_in is not None and self.clock_out is not None:
            # Check that clock_out time is after clock_in time.
            if (self.clock_out == self.clock_in) or (self.clock_out < self.clock_in):
                raise ValidationError('Clock out time must be after clock in time.')

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(EmployeeShift, self).save(*args, **kwargs)


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

    # Model fields.
    room = models.ForeignKey('cae_home.Room', on_delete=models.CASCADE)
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
