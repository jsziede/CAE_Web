"""
Form views for CAE Web Core app.
"""

from django import forms

from . import models


class EmployeeShiftForm(forms.ModelForm):
    """
    Define form view for Employee Shift.
    """
    class Meta:
        model = models.EmployeeShift
        fields = {
            'employee',
            'pay_period',
            'clock_in',
            'clock_out',
        }
