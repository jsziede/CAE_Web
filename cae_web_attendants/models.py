"""
Models for CAE Web Attendants app.
"""

from django.utils import timezone
from django.db import models
from django.db.models import F


MAX_LENGTH = 255


class RoomCheckout(models.Model):
    """
    Information regarding a checkout of a CAE computer classroom by a student.
    """
    # Foreign keys
    room = models.ForeignKey('cae_home.Room', on_delete=models.CASCADE)
    employee = models.ForeignKey('cae_home.User', on_delete=models.CASCADE)
    student = models.ForeignKey('cae_home.WmuUser', on_delete=models.CASCADE)

    # Fields specific to RoomCheckout model
    checkout_date = models.DateField(default=timezone.now)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room Checkout"
        verbose_name_plural = "Room Checkouts"
        ordering = ('-checkout_date',)
        unique_together = ('room', 'checkout_date',)

    def __str__(self):
        return self.room + " " + self.checkout_date


class ChecklistTemplate(models.Model):
    """
    Generic template for attendant checklists to inherit. A template should not be edited after creation.
    """
    # Foreign keys
    room = models.ForeignKey('cae_home.Room',
        on_delete=models.CASCADE,
        blank=True,
        null=True)

    # Many to many keys
    checklist_item = models.ManyToManyField('ChecklistItem', blank=True)

    # Fields specific to ChecklistTemplate model
    title = models.TextField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Checklist Template"
        verbose_name_plural = "Checklist Templates"
        ordering = ('title',)

    def __str__(self):
        return self.title


class ChecklistItem(models.Model):
    """
    Each individual task on an attendant checklist.
    """
    # Fields specific to ChecklistItem model
    task = models.CharField(max_length=MAX_LENGTH)#, unique=True)
    completed = models.BooleanField(default=False)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Checklist Item"
        verbose_name_plural = "Checklist Items"
        ordering = ('task',)

    def __str__(self):
        return self.task


class ChecklistInstance(models.Model):
    """
    An instance of an attendant checklist that inherits from a checklist template.
    This is what the attendants fill out and submit on a daily basis.
    """
    # Foreign keys
    template = models.ForeignKey('ChecklistTemplate', on_delete=models.CASCADE)
    room = models.ForeignKey('cae_home.Room', on_delete=models.CASCADE)
    employee = models.ForeignKey('cae_home.User', on_delete=models.CASCADE)

    # Many to many keys
    task = models.ManyToManyField('ChecklistItem')

    # Fields specific to ChecklistInstance model
    title = models.TextField(blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Checklist Instance"
        verbose_name_plural = "Checklist Instances"
        ordering = [F('date_completed').desc(nulls_first=True), ('-date_created')]

    def __str__(self):
        return self.title + " " + self.date_created
