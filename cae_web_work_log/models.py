"""
Models for CAE Web Work Log app.
"""

from django.contrib.auth.models import Group
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


MAX_LENGTH = 255


class TimeFrameType(models.Model):
    """
    A category of timeframe to use.
    """
    # Preset field choices.
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2
    YEARLY = 3
    TIMEFRAME_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    )

    # Model fields.
    name = models.PositiveSmallIntegerField(choices=TIMEFRAME_CHOICES,)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Timeframe Type"
        verbose_name_plural = "Timeframe Types"

    def __str__(self):
        return '{0}'.format(self.TIMEFRAME_CHOICES[self.name][1])

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(TimeFrameType, self).save(*args, **kwargs)

    def full_name(self):
        return self.TIMEFRAME_CHOICES[self.name][1]


class WorkLogSet(models.Model):
    """
    A set of logs for the associated group and timeframe.
    """
    # Relationship keys.
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    timeframe_type = models.ForeignKey('TimeFrameType', on_delete=models.CASCADE)

    # Model fields.
    description = models.CharField(max_length=MAX_LENGTH, blank=True)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Log Set"
        verbose_name_plural = "Log Sets"

    def __str__(self):
        return '{0}'.format(self.description)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        self.description = 'Set of {0} {1} work logs.'.format(self.timeframe_type.full_name(), self.group)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(WorkLogSet, self).save(*args, **kwargs)


class WorkLogEntry(models.Model):
    """
    An individual entry for a given log set.
    """
    # Relationship keys.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    log_set = models.ForeignKey('WorkLogSet', blank=True, on_delete=models.CASCADE)

    # Model fields.
    entry_date = models.DateField()
    description = models.TextField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Log Entry"
        verbose_name_plural = "Log Entries"
        unique_together = (
            ('user', 'log_set', 'entry_date'),
        )

    def __str__(self):
        return '{0} {1}'.format(self.user, self.entry_date)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # Automatically choose log_set if none provided. Defaults to weekly.
        if not hasattr(self, 'log_set'):
            valid_log_groups = [
                Group.objects.get(name='CAE Admin'),
                Group.objects.get(name='CAE Programmer'),
            ]
            user_log_group = None
            for group in self.user.groups.all():
                if group in valid_log_groups:
                    user_log_group = group

            timeframe_type = TimeFrameType.objects.get(name=TimeFrameType.WEEKLY)
            if user_log_group is not None:
                self.log_set = WorkLogSet.objects.filter(timeframe_type=timeframe_type).filter(group=user_log_group).first()
            else:
                raise ValidationError(
                    'User group not set to one of {0}. Could not automatically assign log set. Please manually select a'
                    'log set.'.format(valid_log_groups)
                )

        # Determine date values based on associated log_set timeframe.
        log_type = str(self.log_set.timeframe_type.full_name())

        # Don't modify log date on daily. On all others, set date to start of given timeframe period.
        if log_type == 'Weekly':  # Note: Start of week is considered Monday.
            self.entry_date = self.entry_date - timezone.timedelta(days=self.entry_date.weekday())
        elif log_type == 'Monthly':
            self.entry_date = self.entry_date.replace(day=1)
        elif log_type == 'Yearly':
            self.entry_date = self.entry_date.replace(month=1, day=1)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(WorkLogEntry, self).save(*args, **kwargs)

