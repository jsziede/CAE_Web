"""
Test for CAE Web Core app.
"""
import datetime

from django.test import TestCase
from django.utils import timezone
import pytz

from .. import models
from ..utils import excel
from ..views import populate_pay_periods


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
            date_start = timezone.now().date()
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

    def test_excel_add_minutes(self):
        """Test excel.add_minutes() works as expected."""
        t1 = datetime.time(hour=0, minute=0)

        t2 = excel.add_minutes(t1, 59)
        self.assertEqual(0, t2.hour)
        self.assertEqual(59, t2.minute)

        t2 = excel.add_minutes(t1, 60)
        self.assertEqual(1, t2.hour)
        self.assertEqual(0, t2.minute)

        t2 = excel.add_minutes(t1, 61)
        self.assertEqual(1, t2.hour)
        self.assertEqual(1, t2.minute)

        t1 = datetime.time(hour=0, minute=30)

        t2 = excel.add_minutes(t1, 29)
        self.assertEqual(0, t2.hour)
        self.assertEqual(59, t2.minute)

        t2 = excel.add_minutes(t1, 30)
        self.assertEqual(1, t2.hour)
        self.assertEqual(0, t2.minute)

        t2 = excel.add_minutes(t1, 31)
        self.assertEqual(1, t2.hour)
        self.assertEqual(1, t2.minute)

        t2 = excel.add_minutes(t1, 60)
        self.assertEqual(1, t2.hour)
        self.assertEqual(30, t2.minute)

        t2 = excel.add_minutes(t1, 120)
        self.assertEqual(2, t2.hour)
        self.assertEqual(30, t2.minute)

        # Now check it wraps around when going after midnight
        t1 = datetime.time(hour=23, minute=30)

        t2 = excel.add_minutes(t1, 29)
        self.assertEqual(23, t2.hour)
        self.assertEqual(59, t2.minute)

        t2 = excel.add_minutes(t1, 30)
        self.assertEqual(0, t2.hour)
        self.assertEqual(0, t2.minute)

        t2 = excel.add_minutes(t1, 31)
        self.assertEqual(0, t2.hour)
        self.assertEqual(1, t2.minute)
