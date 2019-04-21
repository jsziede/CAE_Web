"""
CAE Web Core - Selenium Tests for Room Schedule views.
"""
import time

from django.contrib.auth.models import Group
from django.urls import reverse
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

from cae_home.tests.utils import LiveServerTestCase


class TestEmployeeSchedules(LiveServerTestCase):
    """
    Selenium Tests to verify things like javascript and sockets.
    """
    # Import fixtures.
    fixtures = [
        'availability_event_types',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Two browser windows, each with a different user.
        cls.driver1 = cls.create_driver()
        cls.driver2 = cls.create_driver()

    def setUp(self):
        super().setUp()

        # Create two users.
        self.user_1 = self.create_user('user_1', first_name='Bob')
        self.user_2 = self.create_user('user_2', first_name='Linda')

        # View is hardcoded to use 'CAE Admin' as default
        admin_group = Group.objects.create(name='CAE Admin')
        admin_group.user_set.add(self.user_1, self.user_2)

    def test_live_update(self):
        """
        Test that one user creating an event, is immediately seen by another user in the Employee Schedule.
        """

        # Log in the first user
        self.add_permission(self.user_1, "add_availabilityevent")
        self._login(self.driver1, self.user_1.username, self.user_1.password_string)
        self.driver1.get(self.live_server_url + reverse('cae_web_core:employee_schedule'))

        # Log in the second user
        self.add_permission(self.user_2, "add_availabilityevent")
        self._login(self.driver2, self.user_2.username, self.user_2.password_string)
        self.driver2.get(self.live_server_url + reverse('cae_web_core:employee_schedule'))

        # Wait for js to initialize the schedule
        self._wait_for_css(self.driver2, '.schedule-grid-line')

        # Ensure second user can't see the test event
        self._wait_for_css(self.driver2, '.schedule-event', "Second user should not already see created event!", wait_for_remove=True)

        # Have first user create an event
        grid_line = self.driver1.find_element_by_css_selector('.schedule-grid-line[data-resource-index="0"][data-time-offset="4"]')
        # Double click to open create event dialog
        ActionChains(self.driver1).double_click(grid_line).perform()
        # Change Event Type
        select = Select(self.driver1.find_element_by_id('id_event_type'))
        select.select_by_visible_text('Scheduled')
        # Click the save button
        self.driver1.find_element_by_css_selector('#div_event_dialog button.success').click()

        # Wait for second user to see the test event
        self._wait_for_css(self.driver2, '.schedule-event', "Second user can't find created event!")
