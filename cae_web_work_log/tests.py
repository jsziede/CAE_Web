"""
Tests for CAE Work Log app.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from . import models


class TimeFrameTypeModelTests(TestCase):
    """
    Tests to ensure valid Timeframe Type Model creation/logic.
    """
    def setUp(self):
        self.test_timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.DAILY)

    def test_model_creation(self):
        self.assertEqual(self.test_timeframe.name, models.TimeFrameType.DAILY)
        self.assertEqual(models.TimeFrameType.TIMEFRAME_CHOICES[self.test_timeframe.name][1], 'Daily')

    def test_string_representation(self):
        self.assertEqual(str(self.test_timeframe), self.test_timeframe.full_name())

    def test_plural_representation(self):
        self.assertEqual(str(self.test_timeframe._meta.verbose_name), 'Timeframe Type')
        self.assertEqual(str(self.test_timeframe._meta.verbose_name_plural), 'Timeframe Types')

    def test_full_name(self):
        self.assertEqual(self.test_timeframe.full_name(), 'Daily')


class WorkLogSetModelTests(TestCase):
    """
    Tests to ensure valid Work Log Set Model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(name='Test Group')
        cls.timeframe_type = models.TimeFrameType.objects.create(name=models.TimeFrameType.DAILY)

    def setUp(self):
        self.test_log_set = models.WorkLogSet.objects.create(
            group=self.group,
            timeframe_type=self.timeframe_type,
        )

    def test_model_creation(self):
        self.assertEqual(
            self.test_log_set.description,
            'Set of ' + self.timeframe_type.full_name() + ' ' + str(self.group) + ' work logs.'
        )
        self.assertEqual(self.test_log_set.timeframe_type, self.timeframe_type)

    def test_string_representation(self):
        self.assertEqual(str(self.test_log_set), str(self.test_log_set.description))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_log_set._meta.verbose_name), 'Log Set')
        self.assertEqual(str(self.test_log_set._meta.verbose_name_plural), 'Log Sets')


class WorkLogEntryTests(TestCase):
    """
    Tests to ensure valid Work Log Entry Model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.group = Group.objects.create(name='Test Group')
        cls.user = get_user_model().objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        cls.timeframe_type = models.TimeFrameType.objects.create(name=models.TimeFrameType.DAILY)
        cls.log_set = models.WorkLogSet.objects.create(group=cls.group, timeframe_type=cls.timeframe_type)
        cls.log_creation_date = timezone.datetime(2018, 1, 1)

    def setUp(self):
        self.test_entry = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=self.log_set,
            entry_date=self.log_creation_date,
            description='Test Description',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_entry.log_set, self.log_set)
        self.assertEqual(self.test_entry.entry_date, self.log_creation_date.date())
        self.assertEqual(str(self.test_entry.description), 'Test Description')

    def test_string_representation(self):
        self.assertEqual(str(self.test_entry), '{0} {1}'.format(self.test_entry.user, self.test_entry.entry_date))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_entry._meta.verbose_name), 'Log Entry')
        self.assertEqual(str(self.test_entry._meta.verbose_name_plural), 'Log Entries')

    #region Log Date Overlap and Date Calculation Testing

    def test_daily_timeframe_logs_overlap(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.DAILY)
        log_set = models.WorkLogSet.objects.create(group=self.group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first weekly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date,
            description='Test Description',
        )
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second entry on same week.
        with self.assertRaises(ValidationError):
            log_entry_2 = models.WorkLogEntry.objects.create(
                user=self.user,
                log_set=log_set,
                entry_date=self.log_creation_date,
                description='Test Description',
            )

    def test_weekly_timeframe_logs(self):
        # Create parent models.
        user_2 = get_user_model().objects.create_user('temporary_2', 'temporary_2@gmail.com', 'temporary_2')
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.WEEKLY)
        log_set = models.WorkLogSet.objects.create(group=self.group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first weekly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.user, self.user)
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second weekly entry. Different week.
        log_entry_2 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=7),
            description='Test Description',
        )
        self.assertEqual(log_entry_2.user, self.user)
        self.assertEqual(log_entry_2.entry_date, self.log_creation_date.date() + timezone.timedelta(days=7))

        # Create third weekly entry. Different user.
        log_entry_3 = models.WorkLogEntry.objects.create(
            user=user_2,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_3.user, user_2)
        self.assertEqual(log_entry_3.entry_date, self.log_creation_date.date())

    def test_weekly_timeframe_logs_overlap(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.WEEKLY)
        log_set = models.WorkLogSet.objects.create(group=self.group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first weekly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second entry on same week.
        with self.assertRaises(ValidationError):
            log_entry_2 = models.WorkLogEntry.objects.create(
                user=self.user,
                log_set=log_set,
                entry_date=self.log_creation_date + timezone.timedelta(days=6),
                description='Test Description',
            )

    def test_monthly_timeframe_logs(self):
        # Create parent models.
        user_2 = get_user_model().objects.create_user('temporary_2', 'temporary_2@gmail.com', 'temporary_2')
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.MONTHLY)
        log_set = models.WorkLogSet.objects.create(group=self.group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first monthly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.user, self.user)
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second monthly entry. Different month.
        log_entry_2 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=37),
            description='Test Description',
        )
        self.assertEqual(log_entry_2.user, self.user)
        self.assertEqual(log_entry_2.entry_date, self.log_creation_date.date() + timezone.timedelta(days=31))

        # Create third monthly entry. Different user.
        log_entry_3 = models.WorkLogEntry.objects.create(
            user=user_2,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_3.user, user_2)
        self.assertEqual(log_entry_3.entry_date, self.log_creation_date.date())

    def test_monthly_timeframe_logs_overlap(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.MONTHLY)
        log_set = models.WorkLogSet.objects.create(group=self.group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first weekly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second entry on same month.
        with self.assertRaises(ValidationError):
            log_entry_2 = models.WorkLogEntry.objects.create(
                user=self.user,
                log_set=log_set,
                entry_date=self.log_creation_date + timezone.timedelta(days=6),
                description='Test Description',
            )

    def test_yearly_timeframe_logs(self):
        # Create parent models.
        user_2 = get_user_model().objects.create_user('temporary_2', 'temporary_2@gmail.com', 'temporary_2')
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.YEARLY)
        log_set = models.WorkLogSet.objects.create(group=self.group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first yearly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.user, self.user)
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second yearly entry. Different year.
        log_entry_2 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=367),
            description='Test Description',
        )
        self.assertEqual(log_entry_2.user, self.user)
        self.assertEqual(log_entry_2.entry_date, self.log_creation_date.date() + timezone.timedelta(days=365))

        # Create third yearly entry. Different user.
        log_entry_3 = models.WorkLogEntry.objects.create(
            user=user_2,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_3.user, user_2)
        self.assertEqual(log_entry_3.entry_date, self.log_creation_date.date())

    def test_yearly_timeframe_logs_overlap(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.YEARLY)
        log_set = models.WorkLogSet.objects.create(group=self.group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first yearly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.user,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second entry on same year.
        with self.assertRaises(ValidationError):
            log_entry_2 = models.WorkLogEntry.objects.create(
                user=self.user,
                log_set=log_set,
                entry_date=self.log_creation_date + timezone.timedelta(days=266),
                description='Test Description',
            )

    # endregion Log Date Overlap and Date Calculation Testing
