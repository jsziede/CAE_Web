"""
Test for CAE Web Core app.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import TestCase
from django.utils import timezone

from . import models
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
        cls.user = get_user_model().objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        cls.period_start = timezone.now() - timezone.timedelta(days=2, hours=12)
        cls.pay_period = models.PayPeriod.objects.create(period_start=cls.period_start)

    def setUp(self):
        self.clock_in = timezone.now()
        self.clock_out = self.clock_in + timezone.timedelta(hours=5, minutes=30)
        self.test_employee_shift = models.EmployeeShift.objects.create(
            pay_period=self.pay_period,
            employee=self.user,
            clock_in=self.clock_in,
            clock_out=self.clock_out,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_employee_shift.pay_period, self.pay_period)
        self.assertEqual(self.test_employee_shift.employee, self.user)
        self.assertEqual(self.test_employee_shift.clock_in, self.clock_in)
        self.assertEqual(self.test_employee_shift.clock_out, self.clock_out)

    def test_string_representation(self):
        self.assertEqual(
            str(self.test_employee_shift),
            '{0}: {1} to {2}'.format(self.user, self.clock_in, self.clock_out)
        )

    def test_plural_representation(self):
        self.assertEqual(str(self.test_employee_shift._meta.verbose_name), 'Employee Shift')
        self.assertEqual(str(self.test_employee_shift._meta.verbose_name_plural), 'Employee Shifts')

    def test_clock_in_equal_to_clock_out(self):
        # Test clock in equal to clock out.
        clock_in = self.clock_out
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(employee=self.user, clock_in=clock_in, clock_out=self.clock_out)

    def test_clock_in_after_clock_out(self):
        # Test clock in of 1 minute after clock out.
        clock_in = self.clock_out + timezone.timedelta(minutes=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(employee=self.user, clock_in=clock_in, clock_out=self.clock_out)

    def test_overlapping_shifts(self):
        # Test clock in time between old shift.
        clock_in = self.clock_in + timezone.timedelta(minutes=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user,
                    pay_period=self.pay_period,
                    clock_in=clock_in
                )

        # Test clock out time between old shift.
        clock_in = self.clock_in - timezone.timedelta(minutes=1)
        clock_out = self.clock_in + timezone.timedelta(minutes=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out
                )

        # Test new shift entirely inside old shift.
        clock_in = self.clock_in + timezone.timedelta(minutes=1)
        clock_out = self.clock_out - timezone.timedelta(minutes=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out
                )

        # Test old shift entirely inside new shift.
        clock_in = self.clock_in - timezone.timedelta(minutes=1)
        clock_out = self.clock_out + timezone.timedelta(minutes=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out
                )

    def test_outside_of_pay_period(self):
        # Test before pay period.
        clock_in = self.pay_period.period_start - timezone.timedelta(hours=5)
        clock_out = self.pay_period.period_start - timezone.timedelta(hours=1)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                models.EmployeeShift.objects.create(
                    employee=self.user,
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
                    employee=self.user,
                    pay_period=self.pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )

    def test_spaning_multiple_pay_periods(self):
        next_pay_period_start = self.pay_period.period_start + timezone.timedelta(days=14)
        next_pay_period = models.PayPeriod.objects.create(period_start=next_pay_period_start)

        clock_in = self.pay_period.period_end - timezone.timedelta(hours=1)
        clock_out = next_pay_period.period_start + timezone.timedelta(hours=1)

        test_shift = models.EmployeeShift.objects.create(
            employee=self.user,
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

#endregion View Tests
