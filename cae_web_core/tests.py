"""
Test for CAE Web Core app.
"""

import datetime, pytz
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import models
from .views import populate_pay_periods
from cae_home import models as cae_home_models


#region Model Tests

class PayPeriodTests(TestCase):
    """
    Tests to ensure valid Pay Period model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.date_start = datetime.datetime.now().date()
        midnight = datetime.time(0, 0, 0, 0, pytz.timezone('America/Detroit'))
        start_datetime = datetime.datetime.combine(cls.date_start, midnight)
        cls.date_end = (start_datetime + timezone.timedelta(days=13)).date()

    def setUp(self):
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

            # Test first pay period. Should start on May 25th, 2015 (5-25-2015).
            unaware_date = datetime.datetime.strptime('2015 05 25 00 00 00', '%Y %m %d %H %M %S')
            date_start = self.server_timezone.localize(unaware_date)
            date_end = (date_start + timezone.timedelta(days=13)).date()
            first_pay_period = models.PayPeriod.objects.last()
            self.assertIsNotNone(first_pay_period)
            self.assertEqual(first_pay_period.date_start, date_start.date())
            self.assertEqual(first_pay_period.date_end, date_end)

            # Test current pay period.
            date_start = datetime.datetime.now().date()
            current_pay_period = models.PayPeriod.objects.get(date_start__lte=date_start, date_end__gte=date_start)
            self.assertIsNotNone(current_pay_period)
            self.assertIsNotNone(current_pay_period.date_start)
            self.assertIsNotNone(current_pay_period.date_end)

            # Test last pay period (should be one after current).
            date_start = (current_pay_period.get_start_as_datetime() + timezone.timedelta(days=14)).date()
            date_end = (current_pay_period.get_end_as_datetime() + timezone.timedelta(days=14)).date()
            current_pay_period_plus_1 = models.PayPeriod.objects.get(date_start=date_start, date_end=date_end)
            last_pay_period = models.PayPeriod.objects.first()
            self.assertIsNotNone(current_pay_period_plus_1)
            self.assertEqual(current_pay_period_plus_1, last_pay_period)

            # Finally, check that there are at least 85 pay periods (this will only grow with time).
            # If 85 populate, then it's safe to assume the rest will too.
            pay_periods = models.PayPeriod.objects.all()
            self.assertGreater(len(pay_periods), 85)

#endregion Other Tests
