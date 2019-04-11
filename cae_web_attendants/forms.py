from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.forms import ModelForm, TextInput, HiddenInput

from datetime import datetime

from . import models
from cae_home import forms as cae_home_forms
from cae_home import models as cae_home_models

class RoomCheckoutForm(ModelForm):
    class Meta:
        model = models.RoomCheckout
        fields = [
            'room',
            'employee',
            'student',
            'checkout_date'
        ]
        widgets = {
            'student': cae_home_forms.Select2Widget(),
            'room': cae_home_forms.SelectButtonsSideWidget(),
        }

    # checks if room is checked out for a past date and that the room has not already been checked out for that day
    def clean(self):
        cleaned_data = super(RoomCheckoutForm, self).clean()
        input_date = cleaned_data['checkout_date']
        input_room = cleaned_data['room']

        # allows a room checkout if it is from the current day or in the future, even if the time has passed
        # simply comment out or remove this block of code if retroactive checkouts are allowed
        if input_date < timezone.localdate():
            raise ValidationError(
                _('Invalid date %(date)s: date cannot be from the past'),
                code='invalid',
                params={'date': input_date},
            )

        current_room_checkouts = models.RoomCheckout.objects.filter(
            Q(room__exact=input_room) &
            Q(checkout_date__year=input_date.year) &
            Q(checkout_date__month=input_date.month) &
            Q(checkout_date__day=input_date.day))

        if current_room_checkouts:
            raise ValidationError(
                _('Invalid room: %(room_name)s has already been checked out on %(month)s/%(day)s/%(year)s'),
                code='invalid',
                params={'room_name': input_room,
                'month': input_date.month,
                'day': input_date.day,
                'year': input_date.year}
            )

        return cleaned_data

class ChecklistTemplateForm(ModelForm):
    class Meta:
        model = models.ChecklistTemplate

        fields = [
            'title',
            'checklist_item',
            'room',
        ]
        widgets = {
            'title': TextInput(),
            'checklist_item': HiddenInput()
        }

    prefix = 'template'

class ChecklistInstanceForm(ModelForm):
    class Meta:
        model = models.ChecklistInstance

        fields = [
            'title',
            'employee',
            'room',
            'template',
        ]
        widgets = {
            'title': TextInput(),
        }

class ChecklistItemForm(ModelForm):
    class Meta:
        model = models.ChecklistItem

        fields = [
            'task',
            'completed',
        ]

        widgets = {
            'completed': HiddenInput(),
            'task':  TextInput()
        }
    
    prefix = 'item'
