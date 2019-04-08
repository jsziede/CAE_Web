"""
Test for CAE Web Core app.
"""
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase
from django.utils import timezone
import pytz

from .. import models
from ..views import populate_pay_periods


class PayPeriodTests(TestCase):
    """
    Tests to ensure valid Pay Period model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        populate_pay_periods()

        cls.date_start = timezone.now().date()
        midnight = datetime.time(0, 0, 0, 0, pytz.timezone('America/Detroit'))
        start_datetime = datetime.datetime.combine(cls.date_start, midnight)
        cls.date_end = (start_datetime + timezone.timedelta(days=13)).date()

    def setUp(self):
        try:
            self.test_pay_period = models.PayPeriod.objects.get(
                date_start__lte=self.date_start,
                date_end__gte=self.date_start,
            )
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
