"""
Models for CAE Web Core app.
"""

from django.db import models


MAX_LENGTH = 255


class RoomEvent(models.Model):
    TYPE_CLASS = 1
    TYPE_EVENT = 2
    TYPE_CHOICES = (
        (TYPE_CLASS, "Class"),
        (TYPE_EVENT, "Event"),
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    event_type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        default=TYPE_CLASS,
    )
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=MAX_LENGTH)
    description = models.TextField(blank=True)
    rrule = models.TextField(
        blank=True,
    )

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
