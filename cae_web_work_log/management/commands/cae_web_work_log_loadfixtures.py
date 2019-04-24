"""
Fixture loader command that initializes user models.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed database models with fixture data.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_WORK_LOG: Load Fixtures command has been called.'))
        self.create_timeframe_types()
        self.create_log_sets()

        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_WORK_LOG: Fixture loading complete.\n'))

    def create_timeframe_types(self):
        """
        Create Timeframe Type models.
        """
        call_command('loaddata', 'full_models/timeframe_types')
        self.stdout.write('Populated ' + self.style.SQL_FIELD('Timeframe Type') + ' models.\n')

    def create_log_sets(self):
        """
        Create Log Set models.
        """
        call_command('loaddata', 'full_models/work_log_sets')

        self.stdout.write('Populated ' + self.style.SQL_FIELD('Log Set') + ' models.\n')
