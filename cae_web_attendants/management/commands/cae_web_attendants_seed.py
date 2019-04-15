"""
Seeder command that initializes user models.
"""

import datetime, pytz
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
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

        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_ATTENDANTS: Seed command has been called.'))
        self.create_checklist_items()
        self.create_checklist_templates()
        self.create_checklist_instances()
        self.create_room_checkouts(model_count)

        self.stdout.write(self.style.HTTP_INFO('CAE_WEB_ATTENDANTS: Seeding complete.\n'))

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

    def create_checklist_instances(self):
        """
        Creates Checklists Instance models.
        """
        # Load preset fixtures. No need to create random models.
        call_command('loaddata', 'checklist_instance')
        self.stdout.write('Populated ' + self.style.SQL_FIELD('Checklist Instance') + ' models.\n')

    def create_room_checkouts(self, model_count):
        """
        Create Room Checkout models.
        """
        # Count number of models already created.
        pre_initialized_count = len(models.RoomCheckout.objects.all())

        # Get all related models.
        complex_query = (
            (
                Q(room_type__slug='classroom') | Q(room_type__slug='computer-classroom')
            )
            & Q(department__name='CAE Center')
        )
        employees = cae_home_models.User.objects.all()
        rooms = cae_home_models.Room.objects.filter(complex_query)
        students = cae_home_models.WmuUser.objects.all()

        # Generate models equal to model count.
        total_fail_count = 0
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

                # Generate random date. Can be any date in the last 2 years.
                current_date = timezone.localdate()
                days = randint(1, 730)
                random_date = current_date - datetime.timedelta(days=days)

                # Attempt to create model seed.
                try:
                    models.RoomCheckout.objects.create(
                        employee=employee,
                        student=student,
                        room=room,
                        checkout_date=random_date,
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
                raise ValidationError('Failed to generate any Room Checkout seed instances.')

            if total_fail_count >= (model_count / 2):
                # Handle for a majority of models failing to seed (at least half).
                self.stdout.write(self.style.ERROR(
                    'Failed to generate {0}/{1} Room Checkout seed instances.'.format(total_fail_count, model_count)
                ))
            else:
                # Handle for some models failing to seed (less than half, more than 0).
                self.stdout.write(self.style.WARNING(
                    'Failed to generate {0}/{1} Room Checkout seed instances.'.format(total_fail_count, model_count)
                ))

        self.stdout.write('Populated ' + self.style.SQL_FIELD('Room Checkout') + ' models.\n')
