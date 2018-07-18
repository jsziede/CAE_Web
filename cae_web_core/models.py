"""
Models for CAE Web Core app.
"""

from django.db import models


MAX_LENGTH = 255


class RoomType(models.Model):
    """
    Room types.
    """
    # Preset field choices.
    CLASS = 0
    COMPUTER = 1
    BREAKOUT = 2
    SPECIAL = 3
    ROOM_CHOICES = (
        (CLASS, "Classroom"),
        (COMPUTER, "Computer Classroom"),
        (BREAKOUT, "Breakout Room"),
        (SPECIAL, "Special Room"),
    )

    # Model fields.
    name = models.PositiveSmallIntegerField(
        choices=ROOM_CHOICES,
    )
    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room Type"
        verbose_name_plural = "Room Types"

    def __str__(self):
        return '{0}'.format(self.ROOM_CHOICES[self.name][1])

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(RoomType, self).save(*args, **kwargs)


class Department(models.Model):
    """
    A university department.
    """
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ('name',)

    def __str__(self):
        return '{0}'.format(self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Department, self).save(*args, **kwargs)


class Room(models.Model):
    """
    A standard university room.
    """
    # Relationship keys.
    room_type = models.ForeignKey('RoomType', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE, blank=True, null=True)

    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH)
    capacity = models.PositiveSmallIntegerField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room"
        verbose_name_plural = "Rooms"
        ordering = ('name',)

    def __str__(self):
        return '{0}'.format(self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Room, self).save(*args, **kwargs)
