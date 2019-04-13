"""
Test for CAE Web Core app Schedule models.
"""

from django.utils import timezone

from .. import models
from cae_home import models as cae_home_models
from cae_home.tests.utils import IntegrationTestCase


class RoomEventTypeModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Room Event Type model creation/logic.
    """
    def setUp(self):
        self.test_event_type = models.RoomEventType.objects.create(
            name='Test Name',
            fg_color='#000000',
            bg_color='#ffffff'
        )

    def test_model_creation(self):
        self.assertEqual(self.test_event_type.name, 'Test Name')
        self.assertEqual(self.test_event_type.fg_color, '#000000')
        self.assertEqual(self.test_event_type.bg_color, '#ffffff')

    def test_string_representation(self):
        self.assertEqual(str(self.test_event_type), self.test_event_type.name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_event_type._meta.verbose_name), 'Room Event Type')
        self.assertEqual(str(self.test_event_type._meta.verbose_name_plural), 'Room Event Types')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.RoomEventType.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.RoomEventType))

        # Test get.
        dummy_model_2 = models.RoomEventType.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.RoomEventType))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class RoomEventModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Room model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.room = cae_home_models.Room.create_dummy_model()
        cls.event_type = models.RoomEventType.create_dummy_model()

    def setUp(self):
        self.start_time = timezone.localtime()
        self.end_time = self.start_time + timezone.timedelta(hours=2)
        self.test_room_event = models.RoomEvent.objects.create(
            room=self.room,
            event_type=self.event_type,
            start_time=self.start_time,
            end_time=self.end_time,
            title='Test Title',
            description='Test Description',
            rrule='???',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_room_event.room, self.room)
        self.assertEqual(self.test_room_event.event_type, self.event_type)
        self.assertEqual(self.test_room_event.start_time, self.start_time)
        self.assertEqual(self.test_room_event.end_time, self.end_time)
        self.assertEqual(self.test_room_event.title, 'Test Title')
        self.assertEqual(self.test_room_event.description, 'Test Description')
        self.assertEqual(self.test_room_event.rrule, '???')

    def test_string_representation(self):
        self.assertEqual(
            str(self.test_room_event),
            '{0} {1}: {2} - {3}, Test Title'.format(self.room, self.event_type, self.start_time, self.end_time)
        )

    def test_plural_representation(self):
        self.assertEqual(str(self.test_room_event._meta.verbose_name), 'Room Event')
        self.assertEqual(str(self.test_room_event._meta.verbose_name_plural), 'Room Events')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.RoomEvent.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.RoomEvent))

        # Test get.
        dummy_model_2 = models.RoomEvent.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.RoomEvent))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class AvailabilityEventTypeModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Availability Event Type model creation/logic.
    """
    def setUp(self):
        self.test_event_type = models.AvailabilityEventType.objects.create(
            name='Test Name',
            fg_color='#000000',
            bg_color='#ffffff'
        )

    def test_model_creation(self):
        self.assertEqual(self.test_event_type.name, 'Test Name')
        self.assertEqual(self.test_event_type.fg_color, '#000000')
        self.assertEqual(self.test_event_type.bg_color, '#ffffff')

    def test_string_representation(self):
        self.assertEqual(str(self.test_event_type), self.test_event_type.name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_event_type._meta.verbose_name), 'Availability Event Type')
        self.assertEqual(str(self.test_event_type._meta.verbose_name_plural), 'Availability Event Types')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.AvailabilityEventType.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.AvailabilityEventType))

        # Test get.
        dummy_model_2 = models.AvailabilityEventType.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.AvailabilityEventType))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class AvailabilityEventModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Availability Event model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.employee = cae_home_models.User.create_dummy_model()
        cls.event_type = models.AvailabilityEventType.create_dummy_model()

    def setUp(self):
        self.start_time = timezone.localtime()
        self.end_time = self.start_time + timezone.timedelta(hours=2)
        self.test_availability_event = models.AvailabilityEvent.objects.create(
            employee=self.employee,
            event_type=self.event_type,
            start_time=self.start_time,
            end_time=self.end_time,
            rrule='???',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_availability_event.employee, self.employee)
        self.assertEqual(self.test_availability_event.event_type, self.event_type)
        self.assertEqual(self.test_availability_event.start_time, self.start_time)
        self.assertEqual(self.test_availability_event.end_time, self.end_time)
        self.assertEqual(self.test_availability_event.rrule, '???')

    def test_string_representation(self):
        self.assertEqual(
            str(self.test_availability_event),
            '{0} {1}: {2} - {3}'.format(self.employee, self.event_type, self.start_time, self.end_time)
        )

    def test_plural_representation(self):
        self.assertEqual(str(self.test_availability_event._meta.verbose_name), 'Availability Event')
        self.assertEqual(str(self.test_availability_event._meta.verbose_name_plural), 'Availability Events')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.AvailabilityEvent.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.AvailabilityEvent))

        # Test get.
        dummy_model_2 = models.AvailabilityEvent.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.AvailabilityEvent))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)


class UploadedScheduleModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Uploaded Schedule model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.event = models.RoomEvent.create_dummy_model()

    def setUp(self):
        self.test_uploaded_schedule = models.UploadedSchedule.objects.create(
            name='Test Name',
        )
        self.test_uploaded_schedule.events.add(self.event)
        self.test_uploaded_schedule.save()

    def test_model_creation(self):
        self.assertEqual(self.test_uploaded_schedule.name, 'Test Name')
        self.assertEqual(self.test_uploaded_schedule.events.all()[0], self.event)

    def test_string_representation(self):
        self.assertEqual(str(self.test_uploaded_schedule), 'Test Name')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_uploaded_schedule._meta.verbose_name), 'Uploaded Schedule')
        self.assertEqual(str(self.test_uploaded_schedule._meta.verbose_name_plural), 'Uploaded Schedules')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.UploadedSchedule.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.UploadedSchedule))

        # Test get.
        dummy_model_2 = models.UploadedSchedule.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.UploadedSchedule))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)
