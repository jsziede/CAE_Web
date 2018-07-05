"""CAE Web Core Models"""
from django.db import models


class Room(models.Model):
    """Room"""
    # TODO: Have type of room be dynamic for extensibility. (Another table)
    ROOM_TYPE_CLASS = 1
    ROOM_TYPE_COMPUTER = 2
    ROOM_TYPE_BREAKOUT = 3
    ROOM_TYPE_SPECIAL = 4
    ROOM_TYPE_CHOICES = (
        (ROOM_TYPE_CLASS, "Classroom"),
        (ROOM_TYPE_COMPUTER, "Computer Classroom"),
        (ROOM_TYPE_BREAKOUT, "Breakout Room"),
        (ROOM_TYPE_SPECIAL, "Special Room"),
    )
    name = models.CharField(max_length=10)
    capacity = models.PositiveSmallIntegerField()
    room_type = models.PositiveSmallIntegerField(
        choices=ROOM_TYPE_CHOICES,
    )
