"""
Test for CAE Web Core app.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

from .. import models
from ..views import populate_pay_periods


class EmployeeShiftTests(TestCase):
    """
    Tests to ensure valid Employee Shift model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = get_user_model().objects.create_user('temporary_1', 'temporary@gmail.com', 'temporary')
        cls.user_2 = get_user_model().objects.create_user('temporary_2', 'temporary@gmail.com', 'temporary')
        populate_pay_periods()
        cls.current_pay_period = models.PayPeriod.objects.get(pk=(models.PayPeriod.objects.all().count() - 1))

    def setUp(self):
        self.clock_in = timezone.now()
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
