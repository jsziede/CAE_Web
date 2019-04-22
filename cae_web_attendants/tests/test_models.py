"""
Tests for CAE Web Attendant app models.
"""

from .. import models
from cae_home import models as cae_home_models
from cae_home.tests.utils import IntegrationTestCase

class RoomCheckoutModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Room Checkout model creation/logic.
    """
    def setUp(self):
        employee = cae_home_models.User.create_dummy_model()
        student = cae_home_models.WmuUser.create_dummy_model()
        room = cae_home_models.Room.create_dummy_model()

        self.test_checkout = models.RoomCheckout.objects.create(
            employee=employee,
            student=student,
            room=room,
            checkout_date="2019-01-01",
        )

    def test_string_representation(self):
        self.assertEqual(str(self.test_checkout), self.test_checkout.__str__())

    def test_plural_representation(self):
        self.assertEqual(str(self.test_checkout._meta.verbose_name), 'Room Checkout')
        self.assertEqual(str(self.test_checkout._meta.verbose_name_plural), 'Room Checkouts')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.RoomCheckout.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.RoomCheckout))

        # Test get.
        dummy_model_2 = models.RoomCheckout.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.RoomCheckout))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)

class ChecklistTemplateModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Checklist Template model creation/logic.
    """
    def setUp(self):
        room = cae_home_models.Room.create_dummy_model()
        tasks = models.ChecklistItem.create_dummy_tasks()

        self.test_template = models.ChecklistTemplate.objects.create(
            title="Test Checklist Template",
            room=room,
        )
        for task in tasks:
            self.test_template.checklist_item.add(task.pk)

    def test_string_representation(self):
        self.assertEqual(str(self.test_template), self.test_template.__str__())

    def test_plural_representation(self):
        self.assertEqual(str(self.test_template._meta.verbose_name), 'Checklist Template')
        self.assertEqual(str(self.test_template._meta.verbose_name_plural), 'Checklist Templates')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.ChecklistTemplate.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.ChecklistTemplate))

        # Test get.
        dummy_model_2 = models.ChecklistTemplate.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.ChecklistTemplate))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)

class ChecklistItemModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Checklist Item model creation/logic.
    """
    def setUp(self):
        self.test_item = models.ChecklistItem.objects.create(
            task="Perform unit tests",
            completed=False
        )

    def test_string_representation(self):
        self.assertEqual(str(self.test_item), self.test_item.__str__())

    def test_plural_representation(self):
        self.assertEqual(str(self.test_item._meta.verbose_name), 'Checklist Item')
        self.assertEqual(str(self.test_item._meta.verbose_name_plural), 'Checklist Items')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.ChecklistItem.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.ChecklistItem))

        # Test get.
        dummy_model_2 = models.ChecklistItem.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.ChecklistItem))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)

class ChecklistInstanceModelTests(IntegrationTestCase):
    """
    Tests to ensure valid Checklist Instance model creation/logic.
    """
    def setUp(self):
        template = models.ChecklistTemplate.create_dummy_model()
        employee = cae_home_models.User.create_dummy_model()
        tasks = models.ChecklistItem.create_dummy_tasks()

        self.test_instance = models.ChecklistInstance.objects.create(
            template=template,
            room=template.room,
            employee=employee,
            title="Test Checklist Instance",
        )

        for task in tasks:
            self.test_instance.task.add(task.pk)

    def test_string_representation(self):
        self.assertEqual(str(self.test_instance), self.test_instance.__str__())

    def test_plural_representation(self):
        self.assertEqual(str(self.test_instance._meta.verbose_name), 'Checklist Instance')
        self.assertEqual(str(self.test_instance._meta.verbose_name_plural), 'Checklist Instances')

    def test_dummy_creation(self):
        # Test create.
        dummy_model_1 = models.ChecklistInstance.create_dummy_model()
        self.assertIsNotNone(dummy_model_1)
        self.assertTrue(isinstance(dummy_model_1, models.ChecklistInstance))

        # Test get.
        dummy_model_2 = models.ChecklistInstance.create_dummy_model()
        self.assertIsNotNone(dummy_model_2)
        self.assertTrue(isinstance(dummy_model_2, models.ChecklistInstance))

        # Test both are the same model instance.
        self.assertEqual(dummy_model_1, dummy_model_2)
