"""
Seeder command that initializes user models.
"""

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import Q
from faker import Faker
from random import randint

from apps.CAE_Web.cae_web_work_log import models
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

        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_WORK_LOG: Seed command has been called.'))
        self.create_timeframe_types()
        self.create_log_sets()
        self.create_log_entries(model_count)

        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_WORK_LOG: Seeding complete.\n'))

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

    def create_log_entries(self, model_count):
        """
        Create Log Entry models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.WorkLogEntry.objects.all())

        # Get all related models.
        admin_group = Group.objects.get(name='CAE Admin')
        prog_group = Group.objects.get(name='CAE Programmer')
        complex_query = (
            Q(groups=admin_group) | Q(groups=prog_group)
        )
        users = cae_home_models.User.objects.filter(complex_query)

        # Generate models equal to model count.
        total_fail_count = 0
        for i in range(model_count - pre_initialized_count):
            fail_count = 0
            try_create_model = True

            # Loop attempt until 3 fails or model is created.
            # Model creation may fail due to randomness of log dates and overlapping logs per user being invalid.
            while try_create_model:
                # Generate timeframe.
                time_int = randint(0, 365)
                if time_int <= 1:
                    timeframe_int = models.TimeFrameType.get_int_from_name('Yearly')
                elif time_int <= 4:
                    timeframe_int = models.TimeFrameType.get_int_from_name('Quarterly')
                elif time_int <= 12:
                    timeframe_int = models.TimeFrameType.get_int_from_name('Monthly')
                elif time_int <= 26:
                    timeframe_int = models.TimeFrameType.get_int_from_name('Bi-Weekly')
                elif time_int <= 52:
                    timeframe_int = models.TimeFrameType.get_int_from_name('Weekly')
                else:
                    timeframe_int = models.TimeFrameType.get_int_from_name('Daily')
                timeframe = models.TimeFrameType.objects.get(name=timeframe_int)

                # Get User.
                index = randint(0, len(users) - 1)
                user = users[index]

                # Get log set.
                if admin_group in user.groups.all():
                    log_set = models.WorkLogSet.objects.get(timeframe_type=timeframe, group=admin_group)
                elif prog_group in user.groups.all():
                    log_set = models.WorkLogSet.objects.get(timeframe_type=timeframe, group=prog_group)

                # Get date.
                entry_date = faker_factory.past_datetime(start_date='-{0}d'.format(randint(0, 735)))

                # Generate description.
                description_type = randint(0, 2)
                if description_type is 0:
                    sentence_count = randint(1, 5)
                    description = faker_factory.paragraph(nb_sentences=sentence_count)

                elif description_type is 1:
                    description = '{0}:\n'.format(faker_factory.sentences(nb=1)[0][:-1])
                    bullet_count = randint(1, 5)
                    index = 0
                    while index < bullet_count:
                        description += '* {0}\n'.format(faker_factory.sentences(nb=1)[0])
                        index += 1

                else:
                    sentence_count = randint(1, 5)
                    description = faker_factory.paragraph(nb_sentences=sentence_count)
                    description += '\n\n{0}:\n'.format(faker_factory.sentences(nb=1)[0][:-1])
                    bullet_count = randint(1, 5)
                    index = 0
                    while index < bullet_count:
                        description += '* {0}\n'.format(faker_factory.sentences(nb=1)[0])
                        index += 1

                # Attempt to create model seed.
                try:
                    models.WorkLogEntry.objects.create(
                        user=user,
                        log_set=log_set,
                        entry_date=entry_date,
                        description=description,
                    )
                    try_create_model = False
                except (ValidationError, IntegrityError):
                    # Seed generation failed. Nothing can be done about this without removing the random generation
                    # aspect. If we want that, we should use fixtures instead.
                    fail_count += 1

                    # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                    if fail_count > 2:
                        try_create_model = False
                        total_fail_count += 1

        # Output if model instances failed to generate.
        if total_fail_count > 0:
            # Handle for all models failing to seed.
            if total_fail_count == model_count:
                raise ValidationError('Failed to generate any Log Entry seed instances.')

            if total_fail_count >= (model_count / 2):
                # Handle for a majority of models failing to seed (at least half).
                self.stdout.write(self.style.ERROR(
                    'Failed to generate {0}/{1} Log Entry seed instances.'.format(total_fail_count, model_count)
                ))
            else:
                # Handle for some models failing to seed (less than half, more than 0).
                self.stdout.write(self.style.WARNING(
                    'Failed to generate {0}/{1} Log Entry seed instances.'.format(total_fail_count, model_count)
                ))

        self.stdout.write('Populated ' + self.style.SQL_FIELD('Log Entry') + ' models.\n')
