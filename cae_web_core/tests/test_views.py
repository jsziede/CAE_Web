"""
Test for CAE Web Core app views.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .. import models
from ..views import populate_pay_periods
from cae_home.tests.utils import IntegrationTestCase


class CAEWebCoreViewTests(IntegrationTestCase):
    """
    Tests to ensure valid CAEWeb Core views.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('test', '', 'test')
        cls.current_date = timezone.localdate()
        populate_pay_periods()
        cls.pay_period = models.PayPeriod.objects.get(date_start__lte=cls.current_date, date_end__gte=cls.current_date)

    def test_index(self):
        """
        Tests CAE Web index view.
        """
        response = self.client.get(reverse('cae_web_core:index'))
        self.assertEqual(response.status_code, 200)

        # Quickly check template.
        self.assertContains(response, 'CAE Center Contact Info')

    def test_employee_my_hours(self):
        """
        Tests employee MyHours view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_web_core:my_hours'))
        self.assertRedirects(response, (reverse('cae_home:login') + '?next=' + reverse('cae_web_core:my_hours')))

        # Test authenticated.
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('cae_web_core:my_hours'))
        self.assertEqual(response.status_code, 200)

        # Quickly check template.
        self.assertContains(response, 'Worked Hours for {0}'.format(self.user.username))

    def test_employee_shift_manager(self):
        """
        Tests employee shift manager views.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_web_core:shift_manager_redirect'))
        self.assertRedirects(
            response,
            (reverse('cae_home:login') + '?next=' + reverse('cae_web_core:shift_manager_redirect'))
        )

        # Test authenticated.
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('cae_web_core:shift_manager_redirect'))
        self.assertEqual(response.status_code, 302)

        # Follow redirect url and quickly check template.
        response = self.client.get(reverse('cae_web_core:shift_manager', kwargs={ 'pk': self.pay_period.pk }))
        self.assertContains(
            response,
            '{0} through {1}'.format(
                self.pay_period.date_start.strftime('%b %d, %Y'),
                self.pay_period.date_end.strftime('%b %d, %Y'),
            ),
        )
        self.assertContains(response, 'Current Pay Period')
