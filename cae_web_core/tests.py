"""
Test for CAE Web Core app.
"""

from django.test import TestCase
from django.utils import timezone

from . import models
from cae_home import models as cae_home_models


class RoomEventModelTests(TestCase):
    """
    Tests to ensure valid Room model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.room_type = cae_home_models.RoomType.objects.create(name='Test Room Type')
        cls.department = cae_home_models.Department.objects.create(name='Test Department')
        cls.room = cae_home_models.Room.objects.create(
            name='Test Room',
            room_type=cls.room_type,
            department=cls.department,
            capacity=30,
        )

    def setUp(self):
        self.end_time = timezone.now()
        self.start_time = self.end_time - timezone.timedelta(hours=1)
        self.test_room_event = models.RoomEvent.objects.create(
            room=self.room,
            event_type=models.RoomEvent.TYPE_CLASS,
            start_time=self.start_time,
            end_time=self.end_time,
            title='Test Title',
            description='Test Description',
            rrule='???',
        )

    def test_model_creation(self):
        self.assertEqual(self.test_room_event.room, self.room)
        self.assertEqual(self.test_room_event.event_type, self.test_room_event.TYPE_CLASS)
        self.assertEqual(self.test_room_event.start_time, self.start_time)
        self.assertEqual(self.test_room_event.end_time, self.end_time)
        self.assertEqual(self.test_room_event.title, 'Test Title')
        self.assertEqual(self.test_room_event.description, 'Test Description')
        self.assertEqual(self.test_room_event.rrule, '???')

    def test_string_representation(self):
        self.assertEqual(
            str(self.test_room_event),
            'Test Room Class: {0} - {1}, Test Title'.format(self.start_time, self.end_time)
        )

    def test_plural_representation(self):
        self.assertEqual(str(self.test_room_event._meta.verbose_name), 'Room Event')
        self.assertEqual(str(self.test_room_event._meta.verbose_name_plural), 'Room Events')
