"""
CAE Web Core - Selenium Tests for the MyHours view.
"""

from django.urls import reverse

from cae_home.tests.utils import LiveServerTestCase


class TestMyHoursView(LiveServerTestCase):
    """
    Selenium Tests to verify things like javascript and sockets.
    """
    # This test requires some fixture models
    fixtures = [
        'full_models/room_types',
        'full_models/departments',
        'full_models/rooms',
        'room_event_types',
    ]

    # Two browswer windows, each with a different user
    NUM_DRIVERS = 1

    def setUp(self):
        """
        Logic to reset state before each individual test.
        """
        self.create_default_users_and_groups(password='test')
        super().setUp()

    def test_clock_in_out(self):
        """
        Test that a user can clock in and out.
        """
        user_1 = self.get_user('cae_admin', password='test')

        # Login user.
        self._login(self.driver1, user_1.username, user_1.password_string)
        self.driver1.get(self.live_server_url + reverse('cae_web_core:my_hours'))

        # Test initial view.
        page_title = 'Worked Hours for {0}'.format(user_1.username)
        self.assertTrue(
            page_title in self.driver1.page_source,
            'Page Title does not exist. Did you load the correct url?',
        )

        # Wait until view fully loads.
        self._wait_for_css(self.driver1, '.pay-period')
        clock_form = self.driver1.find_element_by_class_name('panel')
        self.assertIsNotNone(clock_form)
        # Check that user cannot see "clocked in" values. Should currently be clocked out.
        clock_input = clock_form.find_element_by_tag_name('input')
        self.assertTrue('Clock In' in clock_input.get_attribute('value'))
        self.assertFalse('Clock Out' in clock_input.get_attribute('value'))

        # Attempt to clock in.
        clock_input.click()
        self._wait_for_xpath(self.driver1, '//div[@class="panel primary"]//p')
        # Grab refreshed elements.
        clock_form = self.driver1.find_element_by_class_name('panel')
        clock_input = clock_form.find_element_by_tag_name('input')
        clock_in_display = clock_form.find_element_by_xpath('//div[@class="panel primary"]//p[1]')
        shift_length_display = clock_form.find_element_by_xpath('//div[@class="panel primary"]//p[2]')
        # Now check that user is clocked in.
        self.assertTrue('Clock Out' in clock_input.get_attribute('value'))
        self.assertFalse('Clock In' in clock_input.get_attribute('value'))
        self.assertTrue('Clocked In' in clock_in_display.text)
        self.assertTrue('Shift Length' in shift_length_display.text)

        # Attempt to clock out.
        clock_input.click()
        self._wait_for_xpath(self.driver1, ('//div[@class="panel primary"]//p'), wait_for_remove=True)
        # Grab refreshed elements.
        clock_form = self.driver1.find_element_by_class_name('panel')
        clock_input = clock_form.find_element_by_tag_name('input')
        # Now check that user is clocked out.
        self.assertTrue('Clock In' in clock_input.get_attribute('value'))
        self.assertFalse('Clock Out' in clock_input.get_attribute('value'))
