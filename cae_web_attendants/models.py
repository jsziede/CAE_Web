"""
Models for CAE Web Attendants app.
"""
from django.utils import timezone
from django.db import models

# Information needed in order for an attendant to reserve a room for students' use
class RoomCheckout(models.Model):
    # Foreign keys
    room = models.ForeignKey('cae_home.Room', on_delete=models.CASCADE)
    employee = models.ForeignKey('cae_home.User', on_delete=models.CASCADE)
    student = models.ForeignKey('cae_home.WmuUser', on_delete=models.CASCADE)

    # Fields specific to RoomCheckout model
    checkout_date = models.DateTimeField(default=timezone.now)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room Checkout"
        verbose_name_plural = "Room Checkouts"
        ordering = ('-checkout_date',)

# Acts as a template for room checklists
class OpenCloseChecklist(models.Model):
    # Foreign keys
    employee = models.ForeignKey('cae_home.User', on_delete=models.CASCADE)
    checklist_item = models.ForeignKey('ChecklistItem', on_delete=models.CASCADE)

    # Fields specific to RoomCheckout model
    name = models.TextField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Checklist Template"
        verbose_name_plural = "Checklist Templates"
        ordering = ('checklist',)

# Contains the actual tasks on the checklist, which can vary by room or checklist type (such as opening vs closing checklists)
class ChecklistItem(models.Model):
    # Fields specific to RoomCheckout model
    task = models.TextField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Checklist Item"
        verbose_name_plural = "Checklist Items"
        ordering = ('checklist_item',)
        