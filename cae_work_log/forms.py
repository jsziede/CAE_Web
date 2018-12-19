"""
Form views for CAE Work Log app.
"""

from django import forms
from django.forms.widgets import HiddenInput

from . import models


class LogEntryForm(forms.ModelForm):
    """
    Define form view for Log Entry.
    """
    def __init__(self, *args, **kwargs):
        super(LogEntryForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = HiddenInput()

    class Meta:
        model = models.WorkLogEntry
        fields = {
            'user',
            'log_set',
            'entry_date',
            'description',
        }
