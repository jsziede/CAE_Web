"""
Test for CAE Web Core app.
"""

from django.test import TestCase

from . import models


class RoomTypeModelTests(TestCase):
    """
    Tests to ensure valid Room Type model creation/logic.
    """
    def setUp(self):
        self.test_room_type = models.RoomType.objects.create(name=models.RoomType.CLASS)

    def test_model_creation(self):
        self.assertEqual(self.test_room_type.name, models.RoomType.CLASS)

    def test_string_representation(self):
        self.assertEqual(str(self.test_room_type), 'Classroom')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_room_type._meta.verbose_name), 'Room Type')
        self.assertEqual(str(self.test_room_type._meta.verbose_name_plural), 'Room Types')


class DepartmentModelTests(TestCase):
    """
    Tests to ensure valid Department model creation/logic.
    """
    def setUp(self):
        self.test_department = models.Department.objects.create(name='Test Department')

    def test_model_creation(self):
        self.assertEqual(self.test_department.name, 'Test Department')

    def test_string_representation(self):
        self.assertEqual(str(self.test_department), self.test_department.name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_department._meta.verbose_name), 'Department')
        self.assertEqual(str(self.test_department._meta.verbose_name_plural), 'Departments')


class RoomModelTests(TestCase):
    """
    Tests to ensure valid Room model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.room_type = models.RoomType.objects.create(name=models.RoomType.CLASS)
        cls.department = models.Department.objects.create(name='Department')

    def setUp(self):
        self.test_room = models.Room.objects.create(
            name='Test Room',
            room_type=self.room_type,
            department=self.department,
            capacity=30,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_room.name, 'Test Room')
        self.assertEqual(self.test_room.room_type, self.room_type)
        self.assertEqual(self.test_room.department, self.department)
        self.assertEqual(self.test_room.capacity, 30)

    def test_string_representation(self):
        self.assertEqual(str(self.test_room), self.test_room.name)

    def test_plural_representation(self):
        self.assertEqual(str(self.test_room._meta.verbose_name), 'Room')
        self.assertEqual(str(self.test_room._meta.verbose_name_plural), 'Rooms')
