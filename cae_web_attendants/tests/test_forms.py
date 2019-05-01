"""
Tests for CAE Web Attendant app forms.
"""

from django.utils import timezone

from .. import forms
from .. import models
from cae_home import models as cae_home_models
from cae_home.tests.utils import IntegrationTestCase

class RoomCheckoutFormTests(IntegrationTestCase):
    """
    Tests to ensure valid Room Checkout Form validation.
    """
    def test_valid_data(self):
        room = cae_home_models.Room.create_dummy_model()
        employee = cae_home_models.User.create_dummy_model()
        student = cae_home_models.WmuUser.create_dummy_model()

        form = forms.RoomCheckoutForm({
            'room': room.id,
            'employee': employee.id,
            'student': student.id,
            'checkout_date': timezone.localdate()
        })

        self.assertTrue(form.is_valid())
        checkout = form.save()
        self.assertEqual(checkout.room, room)
        self.assertEqual(checkout.employee, employee)
        self.assertEqual(checkout.student, student)
        self.assertEqual(checkout.checkout_date, timezone.localdate())

    def test_old_date(self):
        room = cae_home_models.Room.create_dummy_model()
        employee = cae_home_models.User.create_dummy_model()
        student = cae_home_models.WmuUser.create_dummy_model()

        form = forms.RoomCheckoutForm({
            'room': room.id,
            'employee': employee.id,
            'student': student.id,
            'checkout_date': '2000-01-01'
        })

        self.assertFalse(form.is_valid())

    def test_blank_data(self):
        form = forms.RoomCheckoutForm()
        self.assertFalse(form.is_valid())


class ChecklistItemFormTests(IntegrationTestCase):
    """
    Tests to ensure valid Checklist Item Form validation.
    """
    def test_valid_data(self):
        form = forms.ChecklistItemForm({
            'item-task': 'Test Task',
            'item-completed': False,
        })

        self.assertTrue(form.is_valid())
        item = form.save()
        self.assertEqual(item.task, 'Test Task')
        self.assertEqual(item.completed, False)

    def test_blank_data(self):
        form = forms.ChecklistItemForm()
        self.assertFalse(form.is_valid())

class ChecklistTemplateFormTests(IntegrationTestCase):
    """
    Tests to ensure valid Checklist Template Form validation.
    """
    def test_valid_data(self):
        item = models.ChecklistItem.create_dummy_model()
        room = cae_home_models.Room.create_dummy_model()
        form = forms.ChecklistTemplateForm({
            'template-checklist_item': [item,],
            'template-title': 'Test Template',
            'template-room': room.id,
        })
        self.assertTrue(form.is_valid())
        template = form.save()
        self.assertEqual(template.title, 'Test Template')
        self.assertEqual(template.checklist_item.get(pk=item.id), item)
        self.assertEqual(template.room, room)

    def test_blank_data(self):
        form = forms.ChecklistTemplateForm()
        self.assertFalse(form.is_valid())

class ChecklistInstanceFormTests(IntegrationTestCase):
    """
    Tests to ensure valid Checklist Instance Form validation.
    """
    def test_valid_data(self):
        template = models.ChecklistTemplate.create_dummy_model()
        employee = cae_home_models.User.create_dummy_model()
        form = forms.ChecklistInstanceForm({
            'title': template.title,
            'employee': employee.id,
            'room': template.room.id,
            'template': template.id,
        })
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(instance.title, template.title)
        self.assertEqual(instance.room, template.room)
        self.assertEqual(instance.employee, employee)
        self.assertEqual(instance.template, template)

    def test_blank_data(self):
        form = forms.ChecklistInstanceForm()
        self.assertFalse(form.is_valid())