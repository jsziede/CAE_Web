"""
Seeder command that initializes user models.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from random import randint

from apps.CAE_Web.cae_web_core import models
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

        print('\nCAE_WEB_CORE: Seed command has been called.')
        self.create_assets(model_count)

        print('CAE_WEB_CORE: Seeding complete.')

    def create_assets(self, model_count):
        """
        Create Asset models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.RoomEvent.objects.all())

        rooms = cae_home_models.Room.objects.all()

        for i in range(model_count - pre_initialized_count):
            # Get Room.
            index = randint(0, len(rooms) - 1)
            room = rooms[index]

            # Calculate start/end times.
            start_time = timezone.make_aware(faker_factory.date_time_this_month())
            end_time = start_time + timezone.timedelta(hours=randint(1, 8))

            # Generate description.
            sentence_count = randint(1, 5)
            description = faker_factory.paragraph(nb_sentences=sentence_count)

            models.RoomEvent.objects.create(
                room=room,
                event_type=randint(0, 1),
                start_time=start_time,
                end_time=end_time,
                title=faker_factory.sentence(nb_words=2)[:-1],
                description=description,
                rrule='',
            )
        print('Populated room event models.')
