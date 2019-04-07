"""
Form views for CAE Work Log app.
"""

import datetime
from django import forms
from django.forms.widgets import HiddenInput

from . import models
from cae_home import forms as cae_home_forms


class LogFilterForm(forms.Form):
    """
    Form to allow log filtering.
    """
    group = forms.ChoiceField()
    timeframe = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        # Get filter values from view.
        groups = kwargs.pop('groups', None)
        timeframes = kwargs.pop('timeframes', None)

        # Setup filter values for choice field widgets.
        self.groups = [('All', 'All')]
        for group in groups:
            self.groups.append((str(group), str(group)))
        self.timeframes = [('All', 'All')]
        for timeframe in timeframes:
            self.timeframes.append((str(timeframe), str(timeframe)))

        # Call default form logic.
        super(LogFilterForm, self).__init__(*args, **kwargs)

        # Pass filter values to form fields.
        self.fields['group'].choices = self.groups
        self.fields['timeframe'].choices = self.timeframes


class LogEntryForm(forms.ModelForm):
    """
    Define form view for Log Entry.
    """
    def __init__(self, *args, **kwargs):
        super(LogEntryForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = HiddenInput()

    class Meta:
        model = models.WorkLogEntry
        fields = [
            'user',
            'log_set',
            'entry_date',
            'description',
        ]
