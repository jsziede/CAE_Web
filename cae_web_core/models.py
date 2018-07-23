"""
Models for CAE Web Core app.
"""

from django.db import models


MAX_LENGTH = 255


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
