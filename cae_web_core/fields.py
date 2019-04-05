"""CAE Web Core Fields"""
import datetime
import dateutil.parser

from django.core.exceptions import ValidationError
from django.db import models


class DatetimeListField(models.TextField):
    """
    Represents a list of Datetime objects.
    """
    class DatetimeList:
        """Represents a list of datetimes"""
        def __init__(self, array=None, text=None):
            self._dates = array or []
            if text:
                date_strings = text.split('\n')
                try:
                    self._dates = [
                        dateutil.parser.parse(x)
                        for x in date_strings
                    ]
                except ValueError:
                    raise ValidationError("Invalid date format")

        @property
        def value(self):
            """Return the underlying list of datetimes"""
            return self._dates

        def __str__(self):
            return '\n'.join([x.isoformat() for x in self._dates])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, self.DatetimeList):
            return value
        return self.DatetimeList(text=value)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        if not value:
            return ''

        return str(value)
