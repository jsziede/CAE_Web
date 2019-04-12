"""
CAE Web Core - Selenium Tests for Room Schedule views.
"""
import time

from django.urls import reverse
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

from cae_home.tests.utils import LiveServerTestCase


class TestRoomSchedules(LiveServerTestCase):
    """
    Selenium Tests to verify things like javascript and sockets.
    """
    # Import fixtures.
    fixtures = [
        'full_models/room_types',
        'full_models/departments',
        'full_models/rooms',
        'room_event_types',
    ]

    # Two browser windows, each with a different user.
    NUM_DRIVERS = 2

    def test_live_update(self):
        """
        Test that one user creating an event, is immediately seen by another user in the Room Schedule.
        """
        # Create two users.
        self.user_1 = self.create_user('user_1')
        self.user_2 = self.create_user('user_2')

        # Log in the second user first, to ensure socket connects before event is created
        self._login(self.driver2, self.user_2.username, self.user_2.password_string)
        self.driver2.get(self.live_server_url + reverse('cae_web_core:room_schedule', args=['classroom']))

        time.sleep(1) # GAH!!? Hopefully this gives enough time for test to always pass

        # Wait for js to initialize the schedule
        self._wait_for_css(self.driver2, '.schedule-grid-line')

        # Log in the first user
        self.add_permission(self.user_1, "add_roomevent")
        self._login(self.driver1, self.user_1.username, self.user_1.password_string)
        self.driver1.get(self.live_server_url + reverse('cae_web_core:room_schedule', args=['classroom']))

        event_title = "Test Event"

        # Assert second user can NOT see the test event (hasn't been created yet)
        self.assertFalse(event_title in self.driver2.page_source, "Test Event should not have already been created!")

        # Have first user create an event
        grid_line = self.driver1.find_element_by_css_selector('.schedule-grid-line[data-resource-index="0"][data-time-offset="4"]')
        # Double click to open create event dialog
        ActionChains(self.driver1).double_click(grid_line).perform()
        # Edit Title
        text_title = self.driver1.find_element_by_id('id_title')
        text_title.clear()
        text_title.send_keys(event_title)
        # Change Event Type
        select = Select(self.driver1.find_element_by_id('id_event_type'))
        select.select_by_visible_text('Event')
        # Click the save button
        self.driver1.find_element_by_css_selector('#div_event_dialog button.success').click()

        # Wait for second user to see the test event
        self._wait_for_css(self.driver2, '.schedule-event', "Second user can't find created event!")
        # Assert second user CAN see the test event
        self.assertTrue(event_title in self.driver2.page_source, "Second user can't find created event!")
