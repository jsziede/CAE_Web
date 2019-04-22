"""
Models for CAE Web Attendants app.
"""

from django.utils import timezone
from django.db import models
from django.db.models import F
from django.db.models import ObjectDoesNotExist
from random import randint

from cae_home import models as cae_home_models

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
        return self.room.name + " " + self.checkout_date

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        try:
            return RoomCheckout.objects.get(id=1)
        except ObjectDoesNotExist:
            employee = cae_home_models.User.create_dummy_model()
            student = cae_home_models.WmuUser.create_dummy_model()
            room = cae_home_models.Room.create_dummy_model()

            return RoomCheckout.objects.create(
                employee=employee,
                student=student,
                room=room,
                checkout_date=timezone.localdate(),
            )


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

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        try:
            return ChecklistTemplate.objects.get(id=1)
        except ObjectDoesNotExist:
            room = cae_home_models.Room.create_dummy_model()
            tasks = ChecklistItem.create_dummy_tasks()
            new_template = ChecklistTemplate.objects.create(
                title="Dummy Checklist Template",
                room=room,
            )
            for task in tasks:
                new_template.checklist_item.add(task.pk)
            return new_template


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

    @staticmethod
    def create_dummy_tasks():
        """
        Inserts two dummy tasks into the ChecklistItem table
        and returns them as a list.
        Should only be used for testing, attendants probably
        wouldn't find these tasks useful ;P
        """
        new_tasks = [None] * 2
        new_tasks[0] = ChecklistItem.objects.create(
            task="Break the things",
            completed=True
        )
        new_tasks[1] = ChecklistItem.objects.create(
            task="Fix the things",
            completed=False
        )
        return new_tasks

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        try:
            return ChecklistItem.objects.get(id=1)
        except ObjectDoesNotExist:
            return ChecklistItem.objects.create(
            task="Dummy task",
            completed=False
        )

class ChecklistInstance(models.Model):
    """
    An instance of an attendant checklist that inherits from a checklist template.
    This is what the attendants fill out and submit on a daily basis.
    """

    #TODO: It would probably be beneficial to add a function to automatically insert tasks for the new checklist instance based on the template that it inherits from. Currently this is done from the view when creating a checklist instance from a form but now I think it would make more sense to have it happen from the model.

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
        return self.title + " " + self.date_created.strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def create_dummy_model():
        """
        Attempts to get or create a dummy model.
        Used for testing.
        """
        try:
            return ChecklistInstance.objects.get(id=1)
        except ObjectDoesNotExist:
            template = models.ChecklistTemplate.create_dummy_model()
            employee = cae_home_models.User.create_dummy_model()
            tasks = models.ChecklistItem.create_dummy_tasks()
            new_instance = ChecklistInstance.objects.create(
                template=template,
                room=template.room,
                employee=employee,
                title="Dummy Checklist Instance",
            )
            for task in tasks:
                new_instance.task.add(task.pk)
            return new_instance
