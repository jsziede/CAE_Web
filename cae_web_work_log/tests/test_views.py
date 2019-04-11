"""
Tests for CAE Work Log app views.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone
from os import devnull

from .. import models
from cae_home.management.commands.seeders.user import create_groups
from cae_home.tests.utils import IntegrationTestCase


class CAEWebWorkLogViewTests(IntegrationTestCase):
    @classmethod
    def setUpTestData(cls):
        # Load all relevant fixtures.
        create_groups()
        with open(devnull, 'a') as null:
            call_command('loaddata', 'full_models/site_themes', stdout=null)
            call_command('loaddata', 'full_models/timeframe_types', stdout=null)
            call_command('loaddata', 'full_models/work_log_sets', stdout=null)

        # Create models.
        cls.user = get_user_model().objects.create_user('test', '', 'test')
        cls.user.groups.add(Group.objects.get(name='CAE Admin'))
        cls.log = models.WorkLogEntry.objects.create(user=cls.user, description='test', entry_date=timezone.localdate())

    def test_index(self):
        """
        Tests work log main/index view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_web_work_log:index'))
        self.assertRedirects(response, (reverse('cae_home:login') + '?next=' + reverse('cae_web_work_log:index')))

        # Test authenticated.
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('cae_web_work_log:index'))
        self.assertEqual(response.status_code, 200)

        # Quickly check template.
        self.assertContains(response, 'CAE Work Log')
        self.assertContains(response, 'Filter Logs')

    def test_log_create(self):
        """
        Tests work log creation view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_web_work_log:create_entry'))
        self.assertRedirects(response, (reverse('cae_home:login') + '?next=' + reverse('cae_web_work_log:create_entry')))

        # Test authenticated.
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('cae_web_work_log:create_entry'))
        self.assertEqual(response.status_code, 200)

        # Quickly check template.
        self.assertContains(response, 'Create Log Entry')

    def test_log_edit(self):
        """
        Tests work log edit view.
        """
        # Test unauthenticated.
        response = self.client.get(reverse('cae_web_work_log:edit_entry', kwargs={ 'pk': 1 }))
        self.assertRedirects(
            response,
            (reverse('cae_home:login') + '?next=' + reverse('cae_web_work_log:edit_entry', kwargs={ 'pk': 1 }))
        )

        # Test authenticated.
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('cae_web_work_log:edit_entry', kwargs={ 'pk': 1 }))
        self.assertEqual(response.status_code, 200)

        # Quickly check template.
        self.assertContains(response, 'Edit Log Entry')
