"""
Seeder command that initializes user models.
"""

from django.core.management.base import BaseCommand
from faker import Faker
from random import randint

from apps.CAE_Web.cae_web_core import models


class Command(BaseCommand):
    help = 'Seed database models with randomized data.'

    def add_arguments(self, parser):
        """
        Parser for command.
        """
        # Optional arguments.
        parser.add_argument(
            'model_count',
            type=int,
            nargs='?',
            default=100,
            help='Number of randomized models to create. Defaults to 100. Cannot exceed 10,000.',
        )

    def handle(self, *args, **kwargs):
        """
        The logic of the command.
        """
        model_count = kwargs['model_count']
        if model_count < 1:
            model_count = 100
        elif model_count > 10000:
            model_count = 100

        print('\nCAE_WEB_CORE: Seed command has been called.')

        print('CAE_WEB_CORE: Seeding complete.')
