"""
Test for CAE Web Core app.
"""

import datetime, pytz
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from . import models
from .views import normalize_for_daylight_savings, populate_pay_periods
from cae_home import models as cae_home_models


#region Model Tests

class PayPeriodTests(TestCase):
    """
    Tests to ensure valid Pay Period model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.period_start = timezone.now()
        cls.period_end = cls.period_start + timezone.timedelta(days=14) - timezone.timedelta(milliseconds=1)

    def setUp(self):
        self.test_pay_period = models.PayPeriod.objects.create(
            period_start=self.period_start,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_pay_period.period_start, self.period_start)
        self.assertEqual(self.test_pay_period.period_end, self.period_end)

    def test_string_representation(self):
        self.assertEqual(str(self.test_pay_period), '{0} - {1}'.format(self.period_start, self.period_end))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_pay_period._meta.verbose_name), 'Pay Period')
        self.assertEqual(str(self.test_pay_period._meta.verbose_name_plural), 'Pay Periods')


class EmployeeShiftTests(TestCase):
    """
    Tests to ensure valid Employee Shift model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = get_user_model().objects.create_user('temporary_1', 'temporary@gmail.com', 'temporary')
        cls.user_2 = get_user_model().objects.create_user('temporary_2', 'temporary@gmail.com', 'temporary')
        cls.period_start = timezone.now() - timezone.timedelta(days=2, hours=12)
        cls.pay_period = models.PayPeriod.objects.create(period_start=cls.period_start)

    def setUp(self):
        self.clock_in = timezone.now()
        self.clock_out = self.clock_in + timezone.timedelta(hours=5, minutes=30)
        self.test_employee_shift = models.EmployeeShift.objects.create(
            pay_period=self.pay_period,
            employee=self.user_1,
            clock_in=self.clock_in,
            clock_out=self.clock_out,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_employee_shift.pay_period, self.pay_period)
        self.assertEqual(self.test_employee_shift.employee, self.user_1)
        self.assertEqual(self.test_employee_shift.clock_in, self.clock_in)
        self.assertEqual(self.test_employee_shift.clock_out, self.clock_out)

    def test_string_representation(self):
        self.assertEqual(
            str(self.test_employee_shift),
            '{0}: {1} to {2}'.format(self.user_1, self.clock_in, self.clock_out)
        )

    def test_plural_representation(self):
        self.assertEqual(str(self.test_employee_shift._meta.verbose_name), 'Employee Shift')
        self.assertEqual(str(self.test_employee_shift._meta.verbose_name_plural), 'Employee Shifts')

    def test_clock_in_equal_to_clock_out(self):
        # Test clock in equal to clock out.
        clock_in = self.clock_out
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(employee=self.user_1, clock_in=clock_in, clock_out=self.clock_out)

    def test_clock_in_after_clock_out(self):
        # Test clock in of 1 minute after clock out.
        clock_in = self.clock_out + timezone.timedelta(minutes=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(employee=self.user_1, clock_in=clock_in, clock_out=self.clock_out)

    def test_overlapping_shifts_clockin_between_clockout_same(self):
        # Test with clock in time between old shift values. Clock out time is same.
        clock_in = self.clock_in + timezone.timedelta(minutes=1)

        # Different users. Should be okay.
        shift = models.EmployeeShift.objects.create(
            employee=self.user_2,
            pay_period=self.pay_period,
            clock_in=clock_in,
            clock_out=self.clock_out,
        )
        self.assertGreater(shift.clock_in, self.test_employee_shift.clock_in)
        self.assertLess(shift.clock_in, self.test_employee_shift.clock_out)
        self.assertEqual(shift.clock_out, self.test_employee_shift.clock_out)
        self.assertNotEqual(shift.employee, self.test_employee_shift.employee)

        # Same user. Should fail.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user_1,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                )

    def test_overlapping_shifts_clockin_same_clockout_between(self):
        # Test clock in time is same. Clock out time between old shift.
        clock_out = self.clock_in + timezone.timedelta(minutes=1)

        # Different users. Should be okay.
        shift = models.EmployeeShift.objects.create(
            employee=self.user_2,
            pay_period=self.pay_period,
            clock_in=self.clock_in,
            clock_out=clock_out,
        )
        self.assertEqual(shift.clock_in, self.test_employee_shift.clock_in)
        self.assertGreater(shift.clock_out, self.test_employee_shift.clock_in)
        self.assertLess(shift.clock_out, self.test_employee_shift.clock_out)
        self.assertNotEqual(shift.employee, self.test_employee_shift.employee)

        # Same user. Should fail.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user_1,
                    pay_period=self.pay_period,
                    clock_in=self.clock_in,
                    clock_out=clock_out,
                )

    def test_overlapping_shifts_new_shift_in_old(self):
        # Test new shift entirely inside old shift.
        clock_in = self.clock_in + timezone.timedelta(minutes=1)
        clock_out = self.clock_out - timezone.timedelta(minutes=1)

        # Different users. Should be okay.
        shift = models.EmployeeShift.objects.create(
            employee=self.user_2,
            pay_period=self.pay_period,
            clock_in=clock_in,
            clock_out=clock_out,
        )
        self.assertGreater(shift.clock_in, self.test_employee_shift.clock_in)
        self.assertLess(shift.clock_in, self.test_employee_shift.clock_out)
        self.assertGreater(shift.clock_out, self.test_employee_shift.clock_in)
        self.assertLess(shift.clock_out, self.test_employee_shift.clock_out)
        self.assertNotEqual(shift.employee, self.test_employee_shift.employee)

        # Same user. Should fail.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user_1,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )

    def test_overlapping_shifts_old_shift_in_new(self):
        # Test old shift entirely inside new shift.
        clock_in = self.clock_in - timezone.timedelta(minutes=1)
        clock_out = self.clock_out + timezone.timedelta(minutes=1)

        # Different users. Should be okay.
        shift = models.EmployeeShift.objects.create(
            employee=self.user_2,
            pay_period=self.pay_period,
            clock_in=clock_in,
            clock_out=clock_out,
        )
        self.assertLess(shift.clock_in, self.test_employee_shift.clock_in)
        self.assertLess(shift.clock_in, self.test_employee_shift.clock_out)
        self.assertGreater(shift.clock_out, self.test_employee_shift.clock_in)
        self.assertGreater(shift.clock_out, self.test_employee_shift.clock_out)
        self.assertNotEqual(shift.employee, self.test_employee_shift.employee)

        # Same user. Should fail.
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user_1,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )

    def test_outside_of_pay_period(self):
        # Test before pay period.
        clock_in = self.pay_period.period_start - timezone.timedelta(hours=5)
        clock_out = self.pay_period.period_start - timezone.timedelta(hours=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user_1,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )

        # Test after pay period.
        clock_in = self.pay_period.period_end + timezone.timedelta(hours=1)
        clock_out = self.pay_period.period_end + timezone.timedelta(hours=5)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user_1,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )

    def test_spanning_multiple_pay_periods(self):
        next_pay_period_start = self.pay_period.period_start + timezone.timedelta(days=14)
        next_pay_period = models.PayPeriod.objects.create(period_start=next_pay_period_start)

        clock_in = self.pay_period.period_end - timezone.timedelta(hours=1)
        clock_out = next_pay_period.period_start + timezone.timedelta(hours=1)

        test_shift = models.EmployeeShift.objects.create(
            employee=self.user_1,
            pay_period=self.pay_period,
            clock_in=clock_in,
            clock_out=clock_out,
        )
        self.assertTrue(test_shift.error_flag)


class RoomEventModelTests(TestCase):
    """
    Tests to ensure valid Room model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.room_type = cae_home_models.RoomType.objects.create(name='Test Room Type')
        cls.department = cae_home_models.Department.objects.create(name='Test Department')
        cls.room = cae_home_models.Room.objects.create(
            name='Test Room',
            room_type=cls.room_type,
            department=cls.department,
            capacity=30,
        )

    def setUp(self):
        self.end_time = timezone.now()
        self.start_time = self.end_time - timezone.timedelta(hours=1)
        self.test_room_event = models.RoomEvent.objects.create(
            room=self.room,
            event_type=models.RoomEvent.TYPE_CLASS,
            start_time=self.start_time,
            end_time=self.end_time,
            title='Test Title',
            description='Test Description',
            rrule='???',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_room_event.room, self.room)
        self.assertEqual(self.test_room_event.event_type, self.test_room_event.TYPE_CLASS)
        self.assertEqual(self.test_room_event.start_time, self.start_time)
        self.assertEqual(self.test_room_event.end_time, self.end_time)
        self.assertEqual(self.test_room_event.title, 'Test Title')
        self.assertEqual(self.test_room_event.description, 'Test Description')
        self.assertEqual(self.test_room_event.rrule, '???')

    def test_string_representation(self):
        self.assertEqual(
            str(self.test_room_event),
            'Test Room Class: {0} - {1}, Test Title'.format(self.start_time, self.end_time)
        )

    def test_plural_representation(self):
        self.assertEqual(str(self.test_room_event._meta.verbose_name), 'Room Event')
        self.assertEqual(str(self.test_room_event._meta.verbose_name_plural), 'Room Events')

#endregion Model Tests


#region View Tests

class CAEWebCoreViewTests(TestCase):
    """
    Tests to ensure valid CAEWeb Core views.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_index_view(self):
        response = self.client.get(reverse('cae_web_core:index'))
        self.assertEqual(response.status_code, 200)

    def test_employee_myHours_view(self):
        # Test unauthenticated.
        response = self.client.get(reverse('cae_web_core:my_hours'))
        self.assertEqual(response.status_code, 302)

        # Test authenticated.
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('cae_web_core:my_hours'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('json_pay_period' in response.context)
        self.assertTrue('json_shifts' in response.context)
        self.assertTrue('json_last_shift' in response.context)

#endregion View Tests


#region Misc Tests

class CAEWebCoreMiscTests(TestCase):
    """
    Misc CAE Web Core tests that don't fit into other classes.
    """

    @classmethod
    def setUpTestData(cls):
        cls.utc_timezone = pytz.timezone('UTC')
        cls.server_timezone = pytz.timezone('America/Detroit')

    def test_normalize_for_daylight_savings(self):
        # As long as we pass midnight, this should always return local time midnight.

        # Test naive time.
        date_holder = datetime.datetime.strptime('2015 05 25 00 00 00', '%Y %m %d %H %M %S')
        normalized_date = normalize_for_daylight_savings(date_holder)
        self.assertEqual(normalized_date.replace(tzinfo=None), date_holder)
        self.assertEqual(normalized_date, self.server_timezone.localize(date_holder))
        self.assertEqual(normalized_date.hour, 0)
        self.assertEqual(normalized_date.minute, 0)

        # Test local timezone aware time.
        current_time = timezone.now()
        date_holder = self.server_timezone.normalize(current_time.astimezone(self.server_timezone))
        date_holder = date_holder.replace(hour=0, minute=0, second=0, microsecond=0)
        normalized_date = normalize_for_daylight_savings(date_holder)
        self.assertEqual(normalized_date.replace(tzinfo=None), date_holder.replace(tzinfo=None))
        self.assertEqual(normalized_date, date_holder)
        self.assertEqual(normalized_date.hour, 0)
        self.assertEqual(normalized_date.minute, 0)

        # Test non-local timezone aware time. In this case, UTC.
        date_holder = parse_datetime('2015-05-25T04:00:00+0000')
        normalized_date = normalize_for_daylight_savings(date_holder, timezone_instance='UTC')
        self.assertEqual(normalized_date, date_holder)
        self.assertEqual(normalized_date.hour, 0)
        self.assertEqual(normalized_date.minute, 0)

    def test_populate_pay_periods(self):

        # Loop through twice.
        # First test generating with clean slate.
        # Then test generating with some periods already populated.
        index = 0
        deletion_count = 0
        while index < 2:
            if index is 1:
                # On second loop through, delete and recreate first 5 pay periods.
                while deletion_count < 5:
                    last_pay_period = models.PayPeriod.objects.first()
                    last_pay_period.delete()
                    deletion_count += 1
            index += 1

            # Auto create pay periods.
            populate_pay_periods()

            # Test first pay period.
            date_start = datetime.datetime.strptime('2015 05 25 00 00 00', '%Y %m %d %H %M %S')
            date_start = normalize_for_daylight_savings(date_start)
            date_end = date_start + timezone.timedelta(days=14) - timezone.timedelta(milliseconds=1)
            first_pay_period = models.PayPeriod.objects.last()
            self.assertEqual(first_pay_period.period_start, date_start)
            self.assertEqual(first_pay_period.period_end, date_end)
            # Test first pay period start values.
            self.assertEqual(first_pay_period.period_start.tzinfo, self.utc_timezone)
            pay_period_start = self.server_timezone.normalize(first_pay_period.period_start.astimezone(self.server_timezone))
            self.assertEqual(pay_period_start.tzinfo.zone, self.server_timezone.zone)
            self.assertEqual(pay_period_start.hour, 0)
            self.assertEqual(pay_period_start.minute, 0)
            self.assertEqual(pay_period_start.second, 0)
            self.assertEqual(pay_period_start.microsecond, 0)

            # Test current pay period.
            date_start = timezone.now()
            current_pay_period = models.PayPeriod.objects.get(period_start__lte=date_start, period_end__gte=date_start)
            self.assertIsNotNone(current_pay_period)
            self.assertIsNotNone(current_pay_period.period_start)
            self.assertIsNotNone(current_pay_period.period_end)
            # Test current pay period start values.
            self.assertEqual(current_pay_period.period_start.tzinfo, self.utc_timezone)
            pay_period_start = self.server_timezone.normalize(current_pay_period.period_start.astimezone(self.server_timezone))
            self.assertEqual(pay_period_start.tzinfo.zone, self.server_timezone.zone)
            self.assertEqual(pay_period_start.hour, 0)
            self.assertEqual(pay_period_start.minute, 0)
            self.assertEqual(pay_period_start.second, 0)
            self.assertEqual(pay_period_start.microsecond, 0)

            # Test last pay period (should be one after current).
            date_start = normalize_for_daylight_savings(
                current_pay_period.period_start + timezone.timedelta(days=14),
                timezone_instance='UTC',
            )
            date_end = normalize_for_daylight_savings(
                current_pay_period.period_end + timezone.timedelta(days=14),
                timezone_instance='UTC',
            )
            last_pay_period = models.PayPeriod.objects.first()
            current_pay_period_plus_1 = models.PayPeriod.objects.get(period_start=date_start, period_end=date_end)
            self.assertEqual(last_pay_period, current_pay_period_plus_1)
            # Test last pay period start values.
            self.assertEqual(last_pay_period.period_start.tzinfo, self.utc_timezone)
            pay_period_start = self.server_timezone.normalize(last_pay_period.period_start.astimezone(self.server_timezone))
            self.assertEqual(pay_period_start.tzinfo.zone, self.server_timezone.zone)
            self.assertEqual(pay_period_start.hour, 0)
            self.assertEqual(pay_period_start.minute, 0)
            self.assertEqual(pay_period_start.second, 0)
            self.assertEqual(pay_period_start.microsecond, 0)

            # Finally, check that there are at least 85 pay periods (this will only grow with time).
            # If 85 populate, then it's safe to assume the rest will too.
            pay_periods = models.PayPeriod.objects.all()
            self.assertGreater(len(pay_periods), 85)

#endregion Other Tests
