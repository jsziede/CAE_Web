"""
Fixture loader command that initializes CaeWeb Core models.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.CAE_Web.cae_web_core.views import populate_pay_periods


class Command(BaseCommand):
    help = 'Seed database models with fixture data.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_CORE: Load Fixture command has been called.'))
        self.create_pay_periods()
        self.create_availability_event_types()
        self.create_room_event_types()

        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_CORE: Fixture Loading complete.\n'))

    def create_pay_periods(self):
        """
        Create Pay Period models.
        Uses "auto population" method in views. Should create from 5-25-2015 up to a pay period after current date.
        """
        populate_pay_periods()
        self.stdout.write('Populated ' + self.style.SQL_FIELD('Pay Period') + ' models.')

    def create_availability_event_types(self):
        """
        Create Availability Event Types
        """
        call_command('loaddata', 'availability_event_types')
        self.stdout.write('Populated ' + self.style.SQL_FIELD('Availability Event Type') + ' models.')

    def create_room_event_types(self):
        """
        Create Room Event Types
        """
        call_command('loaddata', 'room_event_types')
        self.stdout.write('Populated ' + self.style.SQL_FIELD('Room Event Type') + ' models.')
