"""
Test for CAE Web Core app shift models.
"""

import datetime
import pytz
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import transaction
from django.utils import timezone

from .. import models
from ..views import populate_pay_periods
from cae_home.tests.utils import IntegrationTestCase


class PayPeriodTests(IntegrationTestCase):
    """
    Tests to ensure valid Pay Period model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        populate_pay_periods()

        cls.date_start = timezone.localdate()
        midnight = datetime.time(0, 0, 0, 0, pytz.timezone('America/Detroit'))
        start_datetime = datetime.datetime.combine(cls.date_start, midnight)
        cls.date_end = (start_datetime + timezone.timedelta(days=13)).date()

    def setUp(self):
        try:
            self.test_pay_period = models.PayPeriod.objects.get(
                date_start__lte=self.date_start,
                date_end__gte=self.date_start,
            )
            # Since we did not make a new pay period, we must make sure our "date_start" and the found period's
            # "date_start" values match up.
            if self.date_start != self.test_pay_period.date_start:
                self.date_start = self.test_pay_period.date_start
                self.date_end = self.date_start + datetime.timedelta(days=13)

        except ObjectDoesNotExist:
            self.test_pay_period = models.PayPeriod.objects.create(
                date_start=self.date_start,
            )

    def test_model_creation(self):
        self.assertEqual(self.test_pay_period.date_start, self.date_start)
        self.assertEqual(self.test_pay_period.date_end, self.date_end)

    def test_string_representation(self):
        self.assertEqual(str(self.test_pay_period), '{0} - {1}'.format(self.date_start, self.date_end))

    def test_plural_representation(self):
        self.assertEqual(str(self.test_pay_period._meta.verbose_name), 'Pay Period')
        self.assertEqual(str(self.test_pay_period._meta.verbose_name_plural), 'Pay Periods')

    def test_known_daylight_savings_change(self):
        before_start_date = datetime.datetime.strptime('2019-02-25', '%Y-%m-%d').date()
        before_end_date = datetime.datetime.strptime('2019-03-10', '%Y-%m-%d').date()
        after_start_date = datetime.datetime.strptime('2019-03-11', '%Y-%m-%d').date()
        after_end_date = datetime.datetime.strptime('2019-03-24', '%Y-%m-%d').date()
        local_timezone = pytz.timezone('America/Detroit')
        period_before_daylight_savings = models.PayPeriod.objects.get(
            date_start=before_start_date,
            date_end=before_end_date,
        )
        period_after_daylight_savings = models.PayPeriod.objects.get(
            date_start=after_start_date,
            date_end=after_end_date,
        )

        # Check model field values.
        self.assertIsNotNone(period_before_daylight_savings)
        self.assertIsNotNone(period_after_daylight_savings)
        self.assertEqual(period_before_daylight_savings.date_start, before_start_date)
        self.assertEqual(period_before_daylight_savings.date_end, before_end_date)
        self.assertEqual(period_after_daylight_savings.date_start, after_start_date)
        self.assertEqual(period_after_daylight_savings.date_end, after_end_date)

        # Check computed model datetime values.
        before_start_date = datetime.datetime.strptime('2019-02-25 00:00:00', '%Y-%m-%d %H:%M:%S')
        before_start_date = local_timezone.localize(before_start_date)
        before_end_date = datetime.datetime.strptime('2019-03-10 23:59:59', '%Y-%m-%d %H:%M:%S')
        before_end_date = local_timezone.localize(before_end_date)
        after_start_date = datetime.datetime.strptime('2019-03-11 00:00:00', '%Y-%m-%d %H:%M:%S')
        after_start_date = local_timezone.localize(after_start_date)
        after_end_date = datetime.datetime.strptime('2019-03-24 23:59:59', '%Y-%m-%d %H:%M:%S')
        after_end_date = local_timezone.localize(after_end_date)

        self.assertEqual(
            period_before_daylight_savings.get_start_as_datetime(),
            before_start_date,
        )
        self.assertEqual(
            period_before_daylight_savings.get_end_as_datetime(),
            before_end_date,
        )
        self.assertEqual(
            period_after_daylight_savings.get_start_as_datetime(),
            after_start_date,
        )
        self.assertEqual(
            period_after_daylight_savings.get_end_as_datetime(),
            after_end_date,
        )


class EmployeeShiftTests(IntegrationTestCase):
    """
    Tests to ensure valid Employee Shift model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = cls.create_user(cls, 'test_1')
        cls.user_2 = cls.create_user(cls, 'test_2')
        populate_pay_periods()
        current_date = timezone.localdate()
        cls.current_time = timezone.localtime()
        cls.current_pay_period = models.PayPeriod.objects.get(
            date_start__lte=current_date,
            date_end__gte=current_date,
        )

    def setUp(self):
        self.clock_in = self.current_time
        self.clock_out = self.clock_in + timezone.timedelta(hours=5, minutes=30)

        # Check if clock out is too close to (or past) pay period end time.
        if (self.clock_out + timezone.timedelta(hours=1, minutes=1)) >= self.current_pay_period.get_end_as_datetime():
            self.clock_out = self.current_pay_period.get_end_as_datetime()
            self.clock_out = self.clock_out - timezone.timedelta(hours=1, minutes=1)
            self.clock_in = self.clock_out - timezone.timedelta(hours=5, minutes=30)

        self.test_employee_shift = models.EmployeeShift.objects.create(
            pay_period=self.current_pay_period,
            employee=self.user_1,
            clock_in=self.clock_in,
            clock_out=self.clock_out,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_employee_shift.pay_period, self.current_pay_period)
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
        # Test clock in 1 minute after clock out.
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
            pay_period=self.current_pay_period,
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
                    pay_period=self.current_pay_period,
                    clock_in=clock_in,
                )

    def test_overlapping_shifts_clockin_same_clockout_between(self):
        # Test clock in time is same. Clock out time between old shift.
        clock_out = self.clock_in + timezone.timedelta(minutes=1)

        # Different users. Should be okay.
        shift = models.EmployeeShift.objects.create(
            employee=self.user_2,
            pay_period=self.current_pay_period,
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
                    pay_period=self.current_pay_period,
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
            pay_period=self.current_pay_period,
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
                    pay_period=self.current_pay_period,
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
            pay_period=self.current_pay_period,
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
                    pay_period=self.current_pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )

    def test_outside_of_pay_period(self):
        # Test before pay period.
        clock_in = self.current_pay_period.get_start_as_datetime() - timezone.timedelta(hours=5)
        clock_out = self.current_pay_period.get_start_as_datetime() - timezone.timedelta(hours=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user_1,
                    pay_period=self.current_pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )

        # Test after pay period.
        clock_in = self.current_pay_period.get_end_as_datetime() + timezone.timedelta(hours=1)
        clock_out = self.current_pay_period.get_end_as_datetime() + timezone.timedelta(hours=5)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user_1,
                    pay_period=self.current_pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )

    def test_spanning_multiple_pay_periods(self):
        next_pay_date_start = self.current_pay_period.get_start_as_datetime() + timezone.timedelta(days=14)
        next_pay_period = models.PayPeriod.objects.get(date_start=next_pay_date_start)

        clock_in = self.current_pay_period.get_end_as_datetime() - timezone.timedelta(hours=1)
        clock_out = next_pay_period.get_start_as_datetime() + timezone.timedelta(hours=1)

        test_shift = models.EmployeeShift.objects.create(
            employee=self.user_1,
            pay_period=self.current_pay_period,
            clock_in=clock_in,
            clock_out=clock_out,
        )
        self.assertTrue(test_shift.error_flag)

