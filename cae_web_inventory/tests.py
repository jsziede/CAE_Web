"""
Tests for CAE_Home App.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from . import models
from cae_home import models as cae_home_models


#region Model Tests

class ItemModelTests(TestCase):
    """
    Tests to ensure valid Item Model creation/logic.
    """
    def setUp(self):
        self.test_item = models.Item.objects.create(
            name='Test Name',
            description='Test Description',
            current_quantity=1,
            email_threshold=1,
            active=False,
        )

    def test_model_creation(self):
        self.assertEqual(self.test_item.name, 'Test Name')
        self.assertEqual(self.test_item.description, 'Test Description')
        self.assertEqual(self.test_item.current_quantity, 1)
        self.assertEqual(self.test_item.email_threshold, 1)
        self.assertEqual(self.test_item.active, False)

    def test_string_representation(self):
        self.assertEqual(str(self.test_item), 'Test Name')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_item._meta.verbose_name), 'Item')
        self.assertEqual(str(self.test_item._meta.verbose_name_plural), 'Items')


class ItemAdjustmentModelTests(TestCase):
    """
    Tests to ensure valid Item Adjustment Model creation/logic.
    """
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        cls.item = models.Item.objects.create(
            name='Test Name',
            description='Test Description',
            current_quantity=1,
            email_threshold=1,
            active=False,
        )

    def setUp(self):
        self.test_adjustment = models.ItemAdjustment.objects.create(user=self.user, item=self.item, adjustment_amount=1)

    def test_model_creation(self):
        self.assertEqual(self.test_adjustment.user, self.user)
        self.assertEqual(self.test_adjustment.item, self.item)
        self.assertEqual(self.test_adjustment.adjustment_amount, 1)

    def test_string_representation(self):
        self.assertEqual(str(self.test_adjustment), 'Test Name adjusted by 1')

    def test_plural_representation(self):
        self.assertEqual(str(self.test_adjustment._meta.verbose_name), 'Item Adjustment')
        self.assertEqual(str(self.test_adjustment._meta.verbose_name_plural), 'Item Adjustments')

#endregion Model Tests
