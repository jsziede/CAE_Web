"""
Fixture loader command that initializes CaeWeb Attendants models.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seed database models with fixture data.'

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_ATTENDANTS: Load Fixtures command has been called.'))
        self.create_checklist_items()
        self.create_checklist_templates()

        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_ATTENDANTS: Fixture Loading complete.\n'))

    def create_checklist_items(self):
        """
        Creates Checklist Item models.
        """
        # Load preset fixtures. No need to create random models.
        call_command('loaddata', 'checklist_item')
        self.stdout.write('Populated ' + self.style.SQL_FIELD('Checklist Item') + ' models.\n')

    def create_checklist_templates(self):
        """
        Creates Checklist Templates models.
        """
        # Load preset fixtures. No need to create random models.
        call_command('loaddata', 'checklist_template')
        self.stdout.write('Populated ' + self.style.SQL_FIELD('Checklist Template') + ' models.\n')
