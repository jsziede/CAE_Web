"""
Tests for CAE Web Attendant app views.
"""

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from os import devnull

from .. import models
from cae_home.management.commands.seeders.user import create_groups
from cae_home.tests.utils import IntegrationTestCase

class CAEWebAttendantViewTests(IntegrationTestCase):
    @classmethod
    def setUpTestData(cls):
        # Load all relevant fixtures.
        create_groups()
        with open(devnull, 'a') as null:
            call_command('loaddata', 'full_models/site_themes', stdout=null)

        # Create models.
        cls.user = cls.create_user(cls, 'test', password='test')
        cls.user.groups.add(Group.objects.get(name='CAE Attendant'))

    def test_checkout(self):
        """
        Tests room checkout view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_web_attendants:checkout'))
        self.assertRedirects(response, (reverse('cae_home:login') + '?next=' + reverse('cae_web_attendants:checkout')))

        # Test authenticated.
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('cae_web_attendants:checkout'))
        self.assertEqual(response.status_code, 200)

        # Quickly check template.
        self.assertContains(response, 'Room Checkouts')

    def test_checklist(self):
        """
        Tests checklist view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_web_attendants:checklist'))
        self.assertRedirects(response, (reverse('cae_home:login') + '?next=' + reverse('cae_web_attendants:checklist')))

        # Test authenticated.
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('cae_web_attendants:checklist'))
        self.assertEqual(response.status_code, 200)

        # Quickly check template.
        self.assertContains(response, 'Attendants Checklists')