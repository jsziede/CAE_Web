from django import forms

from . import models

class RoomCheckoutForm(forms.ModelForm):
    class Meta:
        model = models.RoomCheckout
        fields = [
            'room',
            'employee',
            'student',
            'checkout_date'
        ]
