"""
Seeder command that initializes user models.
"""

from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from faker import Faker
from random import randint

from apps.CAE_Web.cae_work_log import models
from cae_home import models as cae_home_models


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

        print('\nCAE_WEB_WORK_LOG: Seed command has been called.')
        self.create_timeframe_types()
        self.create_log_sets()
        self.create_log_entries(model_count)

        print('CAE_WEB_WORK_LOG: Seeding complete.')

    def create_timeframe_types(self):
        """
        Create Timeframe Type models.
        """
        call_command('loaddata', 'full_models/timeframe_types')
        print('Populated timeframe type models.')

    def create_log_sets(self):
        """
        Create Log Set models.
        """
        call_command('loaddata', 'full_models/work_log_sets')

        print('Populated log set models.')

    def create_log_entries(self, model_count):
        """
        Create Log Entry models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.WorkLogEntry.objects.all())

        # Get all related models.
        complex_query = (
            Q(groups__name='CAE Admin') | Q(groups__name='CAE Programmer') |
            Q(groups__name='CAE Admin GA') | Q(groups__name='CAE Programmer GA')
        )
        users = cae_home_models.User.objects.filter(complex_query)

        # Generate models equal to model count.
        for i in range(model_count - pre_initialized_count):
            fail_count = 0
            try_create_model = True

            # Loop attempt until 3 fails or model is created.
            # Model creation may fail due to randomness of log dates and overlapping logs per user being invalid.
            while try_create_model:
                # Get User.
                index = randint(0, len(users) - 1)
                user = users[index]

                # Get date.
                entry_date = faker_factory.past_datetime(start_date='-{0}d'.format(randint(0, 735)))

                # Generate description.
                sentence_count = randint(1, 5)
                description = faker_factory.paragraph(nb_sentences=sentence_count)

                # Attempt to create model seed.
                try:
                    models.WorkLogEntry.objects.create(
                        user=user,
                        entry_date=entry_date,
                        description=description,
                    )
                    try_create_model = False
                except ValidationError:
                    # Seed generation failed. Nothing can be done about this without removing the random generation
                    # aspect. If we want that, we should use fixtures instead.
                    fail_count += 1

                    # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                    if fail_count > 2:
                        try_create_model = False
                        print('Failed to generate log entry seed instance.')

        print('Populated log entry models.')
