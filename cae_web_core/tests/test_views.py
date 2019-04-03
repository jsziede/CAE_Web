"""
Test for CAE Web Core app.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CAEWebCoreViewTests(TestCase):
    """
    Tests to ensure valid CAEWeb Core views.

    TODO: If this class gets big, it would be better to break it up into subfiles.
    E.g. test_feature1_view.py, test_feature2_view.py, etc.
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
