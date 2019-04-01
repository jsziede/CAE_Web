"""
Seeder command that initializes user models.
"""

import datetime, pytz
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.management import call_command
from random import randint

from apps.CAE_Web.cae_web_attendants import models
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

        print('\nCAE_WEB_ATTENDANTS: Seed command has been called.')
        self.create_checklists()
        self.create_room_checkouts(model_count)

        print('CAE_WEB_ATTENDANTS: Seeding complete.')

    def create_checklists(self):
        """
        Creates attendant checklists templates and tasks.
        """
        # Load preset fixtures. No need to create random models.
        call_command('loaddata', 'checklist_item')
        call_command('loaddata', 'checklist_template')
        call_command('loaddata', 'checklist_instance')

        print('Populated attendant checklist models.')

    def create_room_checkouts(self, model_count):
        """
        Create Room Checkout models.
        """
        # Count number of models already created.
        pre_initialized_count = len(models.RoomCheckout.objects.all())

        # Get all related models.
        employees = cae_home_models.User.objects.all()
        rooms = cae_home_models.Room.objects.all()
        students = cae_home_models.WmuUser.objects.all()

        # Generate models equal to model count.
        for i in range(model_count - pre_initialized_count):
            fail_count = 0
            try_create_model = True

            # Loop attempt until 3 fails or model is created.
            # Model creation may fail due to randomness of event times and overlapping times per room being invalid.
            while try_create_model:
                # Get employee.
                index = randint(0, len(employees) - 1)
                employee = employees[index]

                # Get room.
                index = randint(0, len(rooms) - 1)
                room = rooms[index]

                # Get student.
                index = randint(0, len(students) - 1)
                student = students[index]

                # Generate random date.
                day = randint(1, 25)
                month = randint(1, 12)
                year = randint(2015, 2019)
                random_date = datetime.date(year, month, day)

                # Push
                try:
                    models.RoomCheckout.objects.create(
                        employee=employee,
                        student=student,
                        room=room,
                        checkout_date=random_date,
                    )
                    try_create_model = False
                except ValidationError:
                    # Seed generation failed. Nothing can be done about this without removing the random generation
                    # aspect. If we want that, we should use fixtures instead.
                    fail_count += 1

                    # If failed 3 times, give up model creation and move on to next model, to prevent infinite loops.
                    if fail_count > 2:
                        try_create_model = False
                        print('Failed to generate room checkout seed instance.')

        print('Populated room checkout models.')
