"""
Tests for CAE Work Log app models.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone

from .. import models
from cae_home.management.commands.seeders.user import create_permission_groups, create_permission_group_users
from cae_home.tests.utils import IntegrationTestCase


class TimeFrameTypeModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Timeframe Type Model creation/logic.
    """
    def setUp(self):
        self.test_timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.DAILY)

    def test_model_creation(self):
        self.assertEqual(self.test_timeframe.name, models.TimeFrameType.DAILY)
        self.assertEqual(self.test_timeframe.get_name_from_int(self.test_timeframe.name), 'Daily')

    def test_string_representation(self):
        self.assertEqual(str(self.test_timeframe), self.test_timeframe.full_name())

    def test_plural_representation(self):
        self.assertEqual(str(self.test_timeframe._meta.verbose_name), 'Timeframe Type')
        self.assertEqual(str(self.test_timeframe._meta.verbose_name_plural), 'Timeframe Types')

    def test_full_name(self):
        self.assertEqual(self.test_timeframe.full_name(), 'Daily')

    def test_name_from_int(self):
        self.assertEqual(models.TimeFrameType.get_name_from_int(0), 'Daily')
        self.assertEqual(models.TimeFrameType.get_name_from_int(1), 'Weekly')
        self.assertEqual(models.TimeFrameType.get_name_from_int(2), 'Monthly')
        self.assertEqual(models.TimeFrameType.get_name_from_int(3), 'Yearly')

    def test_int_from_name(self):
        self.assertEqual(models.TimeFrameType.get_int_from_name('Daily'), 0)
        self.assertEqual(models.TimeFrameType.get_int_from_name('Weekly'), 1)
        self.assertEqual(models.TimeFrameType.get_int_from_name('Monthly'), 2)
        self.assertEqual(models.TimeFrameType.get_int_from_name('Yearly'), 3)


class WorkLogSetModelTests(IntegrationTestCase):
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
            self.timeframe_type.full_name() + ' ' + str(self.group) + ' work logs'
        )
        self.assertEqual(self.test_log_set.timeframe_type, self.timeframe_type)

    def test_string_representation(self):
        self.assertEqual(str(self.test_log_set), str(self.test_log_set.description))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_log_set._meta.verbose_name), 'Log Set')
        self.assertEqual(str(self.test_log_set._meta.verbose_name_plural), 'Log Sets')


class WorkLogEntryTests(IntegrationTestCase):
    """
    Tests to ensure valid Work Log Entry Model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.groups = create_permission_groups()
        cls.test_group = Group.objects.create(name='Test Group')
        cls.users = create_permission_group_users()
        cls.test_user_1 = get_user_model().objects.create_user('temporary_1', 'temporary_1@gmail.com', 'temporary_1')
        cls.test_user_2 = get_user_model().objects.create_user('temporary_2', 'temporary_2@gmail.com', 'temporary_2')

        cls.timeframe_type_daily = models.TimeFrameType.objects.create(name=models.TimeFrameType.DAILY)
        cls.timeframe_type_weekly = models.TimeFrameType.objects.create(name=models.TimeFrameType.WEEKLY)
        cls.timeframe_type_monthly = models.TimeFrameType.objects.create(name=models.TimeFrameType.MONTHLY)
        cls.timeframe_type_yearly = models.TimeFrameType.objects.create(name=models.TimeFrameType.YEARLY)

        cls.admin_log_set = []
        cls.programmer_log_set = []
        cls.test_log_set = models.WorkLogSet.objects.create(group=cls.test_group, timeframe_type=cls.timeframe_type_weekly)
        cls.admin_log_set.append(models.WorkLogSet.objects.create(group=cls.groups[4], timeframe_type=cls.timeframe_type_daily))
        cls.admin_log_set.append(models.WorkLogSet.objects.create(group=cls.groups[4], timeframe_type=cls.timeframe_type_weekly))
        cls.admin_log_set.append( models.WorkLogSet.objects.create(group=cls.groups[4], timeframe_type=cls.timeframe_type_monthly))
        cls.admin_log_set.append(models.WorkLogSet.objects.create(group=cls.groups[4], timeframe_type=cls.timeframe_type_yearly))
        cls.programmer_log_set.append(models.WorkLogSet.objects.create(group=cls.groups[5], timeframe_type=cls.timeframe_type_daily))
        cls.programmer_log_set.append(models.WorkLogSet.objects.create(group=cls.groups[5], timeframe_type=cls.timeframe_type_weekly))
        cls.programmer_log_set.append(models.WorkLogSet.objects.create(group=cls.groups[5], timeframe_type=cls.timeframe_type_monthly))
        cls.programmer_log_set.append(models.WorkLogSet.objects.create(group=cls.groups[5], timeframe_type=cls.timeframe_type_yearly))

        cls.log_creation_date = timezone.datetime(2018, 1, 1)

    def setUp(self):
        self.test_entry = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=self.test_log_set,
            entry_date=self.log_creation_date,
            description='Test Description',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_entry.log_set, self.test_log_set)
        self.assertEqual(self.test_entry.entry_date, self.log_creation_date.date())
        self.assertEqual(str(self.test_entry.description), 'Test Description')

    def test_string_representation(self):
        self.assertEqual(str(self.test_entry), '{0} {1}'.format(self.test_entry.user, self.test_entry.entry_date))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_entry._meta.verbose_name), 'Log Entry')
        self.assertEqual(str(self.test_entry._meta.verbose_name_plural), 'Log Entries')

    #region Group Permission Default Testing

    def test_admin_ga_log_set_selection(self):
        # Make sure we have correct user from array.
        user = self.users[2]
        self.assertEqual(self.users[2].username, 'cae_admin_ga')

        test_entry = models.WorkLogEntry.objects.create(
            user=user,
            entry_date=self.log_creation_date,
            description='Test Description',
        )

        # Test that default selected log set is one we expect.
        self.assertEqual(self.admin_log_set[1].group.name, 'CAE Admin')
        self.assertEqual(test_entry.log_set, self.admin_log_set[1])
        self.assertEqual(test_entry.user, user)
        self.assertEqual(test_entry.entry_date, self.log_creation_date.date())
        self.assertEqual(str(test_entry.description), 'Test Description')

    def test_programmer_ga_log_set_selection(self):
        # Make sure we have correct user from array.
        user = self.users[3]
        self.assertEqual(self.users[3].username, 'cae_programmer_ga')

        test_entry = models.WorkLogEntry.objects.create(
            user=user,
            entry_date=self.log_creation_date,
            description='Test Description',
        )

        # Test that default selected log set is one we expect.
        self.assertEqual(self.programmer_log_set[1].group.name, 'CAE Programmer')
        self.assertEqual(test_entry.log_set, self.programmer_log_set[1])
        self.assertEqual(test_entry.user, user)
        self.assertEqual(test_entry.entry_date, self.log_creation_date.date())
        self.assertEqual(str(test_entry.description), 'Test Description')

    def test_admin_log_set_selection(self):
        # Make sure we have correct user from array.
        user = self.users[4]
        self.assertEqual(self.users[4].username, 'cae_admin')

        test_entry = models.WorkLogEntry.objects.create(
            user=user,
            entry_date=self.log_creation_date,
            description='Test Description',
        )

        # Test that default selected log set is one we expect.
        self.assertEqual(self.admin_log_set[1].group.name, 'CAE Admin')
        self.assertEqual(test_entry.log_set, self.admin_log_set[1])
        self.assertEqual(test_entry.user, user)
        self.assertEqual(test_entry.entry_date, self.log_creation_date.date())
        self.assertEqual(str(test_entry.description), 'Test Description')

    def test_programmer_log_set_selection(self):
        # Make sure we have correct user from array.
        user = self.users[5]
        self.assertEqual(self.users[5].username, 'cae_programmer')

        test_entry = models.WorkLogEntry.objects.create(
            user=self.users[5],
            entry_date=self.log_creation_date,
            description='Test Description',
        )

        # Test that default selected log set is one we expect.
        self.assertEqual(self.programmer_log_set[1].group.name, 'CAE Programmer')
        self.assertEqual(test_entry.log_set, self.programmer_log_set[1])
        self.assertEqual(test_entry.user, user)
        self.assertEqual(test_entry.entry_date, self.log_creation_date.date())
        self.assertEqual(str(test_entry.description), 'Test Description')

    #endregion Group Permission Default Testing

    #region Log Date Overlap and Date Calculation Testing

    def test_daily_timeframe_logs(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.DAILY)
        log_set = models.WorkLogSet.objects.create(group=self.test_group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first daily entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date,
            description='Test Description',
        )
        self.assertEqual(log_entry_1.user, self.test_user_1)
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second daily entry. Different day.
        log_entry_2 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=1),
            description='Test Description',
        )
        self.assertEqual(log_entry_2.user, self.test_user_1)
        self.assertEqual(log_entry_2.entry_date, self.log_creation_date.date() + timezone.timedelta(days=1))

        # Create third daily entry. Different user.
        log_entry_3 = models.WorkLogEntry.objects.create(
            user=self.test_user_2,
            log_set=log_set,
            entry_date=self.log_creation_date,
            description='Test Description',
        )
        self.assertEqual(log_entry_3.user, self.test_user_2)
        self.assertEqual(log_entry_3.entry_date, self.log_creation_date.date())

    def test_daily_timeframe_logs_overlap(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.DAILY)
        log_set = models.WorkLogSet.objects.create(group=self.test_group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first weekly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date,
            description='Test Description',
        )
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second entry on same week.
        with self.assertRaises(ValidationError):
            log_entry_2 = models.WorkLogEntry.objects.create(
                user=self.test_user_1,
                log_set=log_set,
                entry_date=self.log_creation_date,
                description='Test Description',
            )

    def test_weekly_timeframe_logs(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.WEEKLY)
        log_set = models.WorkLogSet.objects.create(group=self.test_group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first weekly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.user, self.test_user_1)
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second weekly entry. Different week.
        log_entry_2 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=7),
            description='Test Description',
        )
        self.assertEqual(log_entry_2.user, self.test_user_1)
        self.assertEqual(log_entry_2.entry_date, self.log_creation_date.date() + timezone.timedelta(days=7))

        # Create third weekly entry. Different user.
        log_entry_3 = models.WorkLogEntry.objects.create(
            user=self.test_user_2,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_3.user, self.test_user_2)
        self.assertEqual(log_entry_3.entry_date, self.log_creation_date.date())

    def test_weekly_timeframe_logs_overlap(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.WEEKLY)
        log_set = models.WorkLogSet.objects.create(group=self.groups[2], timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first weekly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second entry on same week.
        with self.assertRaises(ValidationError):
            log_entry_2 = models.WorkLogEntry.objects.create(
                user=self.test_user_1,
                log_set=log_set,
                entry_date=self.log_creation_date + timezone.timedelta(days=6),
                description='Test Description',
            )

    def test_monthly_timeframe_logs(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.MONTHLY)
        log_set = models.WorkLogSet.objects.create(group=self.test_group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first monthly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.user, self.test_user_1)
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second monthly entry. Different month.
        log_entry_2 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=37),
            description='Test Description',
        )
        self.assertEqual(log_entry_2.user, self.test_user_1)
        self.assertEqual(log_entry_2.entry_date, self.log_creation_date.date() + timezone.timedelta(days=31))

        # Create third monthly entry. Different user.
        log_entry_3 = models.WorkLogEntry.objects.create(
            user=self.test_user_2,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_3.user, self.test_user_2)
        self.assertEqual(log_entry_3.entry_date, self.log_creation_date.date())

    def test_monthly_timeframe_logs_overlap(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.MONTHLY)
        log_set = models.WorkLogSet.objects.create(group=self.test_group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first weekly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second entry on same month.
        with self.assertRaises(ValidationError):
            log_entry_2 = models.WorkLogEntry.objects.create(
                user=self.test_user_1,
                log_set=log_set,
                entry_date=self.log_creation_date + timezone.timedelta(days=6),
                description='Test Description',
            )

    def test_yearly_timeframe_logs(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.YEARLY)
        log_set = models.WorkLogSet.objects.create(group=self.test_group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first yearly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.user, self.test_user_1)
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second yearly entry. Different year.
        log_entry_2 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=367),
            description='Test Description',
        )
        self.assertEqual(log_entry_2.user, self.test_user_1)
        self.assertEqual(log_entry_2.entry_date, self.log_creation_date.date() + timezone.timedelta(days=365))

        # Create third yearly entry. Different user.
        log_entry_3 = models.WorkLogEntry.objects.create(
            user=self.test_user_2,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_3.user, self.test_user_2)
        self.assertEqual(log_entry_3.entry_date, self.log_creation_date.date())

    def test_yearly_timeframe_logs_overlap(self):
        # Create parent models.
        timeframe = models.TimeFrameType.objects.create(name=models.TimeFrameType.YEARLY)
        log_set = models.WorkLogSet.objects.create(group=self.test_group, timeframe_type=timeframe)
        self.assertEqual(log_set.timeframe_type, timeframe)

        # Create first yearly entry.
        log_entry_1 = models.WorkLogEntry.objects.create(
            user=self.test_user_1,
            log_set=log_set,
            entry_date=self.log_creation_date + timezone.timedelta(days=2),
            description='Test Description',
        )
        self.assertEqual(log_entry_1.entry_date, self.log_creation_date.date())

        # Create second entry on same year.
        with self.assertRaises(ValidationError):
            log_entry_2 = models.WorkLogEntry.objects.create(
                user=self.test_user_1,
                log_set=log_set,
                entry_date=self.log_creation_date + timezone.timedelta(days=266),
                description='Test Description',
            )

    # endregion Log Date Overlap and Date Calculation Testing
