"""
Seeder command that initializes user models.
"""

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
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
        self.create_room_types()
        self.create_departments(model_count)
        self.create_rooms(model_count)

        print('CAE_WEB_CORE: Seeding complete.')

    def create_room_types(self):
        """
        Create Room Type models.
        """
        models.RoomType.objects.create(name=models.RoomType.CLASS)
        models.RoomType.objects.create(name=models.RoomType.COMPUTER)
        models.RoomType.objects.create(name=models.RoomType.BREAKOUT)
        models.RoomType.objects.create(name=models.RoomType.SPECIAL)
        print('Populated room type models.')

    def create_departments(self, model_count):
        """
        Create Department models.
        """
        # Generate random data.
        faker_factory = Faker()

        for i in range(model_count):
            models.Department.objects.create(name=faker_factory.job())

        print('Populated department models.')

    def create_rooms(self, model_count):
        """
        Create Room models.
        """
        # Generate random data.
        faker_factory = Faker()

        room_types = models.RoomType.objects.all()
        departments = models.Department.objects.all()

        for i in range(model_count):

            # Get Room Type.
            index = randint(0, len(room_types) - 1)
            room_type = room_types[index]

            # Get Department.
            index = randint(0, len(departments) - 1)
            department = departments[index]

            # Generate room name.
            name = '{0}-{1}'.format(chr(randint(65, 90)), randint(100, 299))

            models.Room.objects.create(
                name=name,
                capacity=randint(15, 200),
                room_type=room_type,
                department=department,
            )

        print('Populated department models.')
