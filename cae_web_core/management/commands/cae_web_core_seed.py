"""
Seeder command that initializes user models.
"""

import datetime, pytz
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from faker import Faker
from random import randint

from apps.CAE_Web.cae_web_core import models
from apps.CAE_Web.cae_web_core.views import populate_pay_periods
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
        self.create_pay_periods()
        self.create_employee_shifts(model_count)
        self.create_room_events(model_count)

        print('CAE_WEB_CORE: Seeding complete.')

    def create_pay_periods(self):
        """
        Create Pay Period models.
        Uses "auto population" method in views. Should create from 5-25-2015 up to a pay period after current date.
        """
        populate_pay_periods()
        print('Populated pay period models.')

    def create_employee_shifts(self, model_count):
        """
        Create Employee Shift models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.EmployeeShift.objects.all())

        # Get all related models.
        date_holder = timezone.now()
        complex_query = (
            (
                Q(groups__name='CAE Attendant') | Q(groups__name='CAE Admin') | Q(groups__name='CAE Programmer')
            )
            & Q(is_active=True)
        )
        users = get_user_model().objects.filter(complex_query)
        pay_periods = models.PayPeriod.objects.filter(date_start__lte=date_holder)[:model_count/20]

        # Generate models equal to model count.
        for i in range(model_count - pre_initialized_count):
            fail_count = 0
            try_create_model = True

            # Loop attempt until 3 fails or model is created.
            # Model creation may fail due to randomness of shift values and overlapping shifts being invalid.
            while try_create_model:
                # Get User.
                index = randint(0, len(users) - 1)
                user = users[index]

                # Get pay period.
                index = randint(0, len(pay_periods) - 1)
                pay_period = pay_periods[index]

                # Calculate clock in/clock out times.
                clock_in = pay_period.get_start_as_datetime() + timezone.timedelta(
                    days=randint(0, 13),
                    hours=randint(8, 16),
                    minutes=randint(0,59)
                )
                clock_out = clock_in + timezone.timedelta(hours=randint(1, 7), minutes=randint(0, 59))

                # If random clock_out time happened to go past pay period, then set to period end.
                if clock_out > pay_period.get_end_as_datetime():
                    clock_out = pay_period.get_end_as_datetime()

                try:
                    models.EmployeeShift.objects.create(
                        employee=user,
                        pay_period=pay_period,
                        clock_in=clock_in,
                        clock_out=clock_out,
                    )
                    try_create_model = False
                except ValidationError:
                    # Likely due to overlapping shift times. Nothing can be done about this without removing the random
                    # generation aspect. If we want that, we should use fixtures instead.
                    fail_count += 1

                    # If failed 3 times, give up model creation and move on to next user/pay_period combination.
                    if fail_count > 3:
                        try_create_model = False

        print('Populated employee shift models.')

    def create_room_events(self, model_count):
        """
        Create Room Event models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.RoomEvent.objects.all())

        # Get all related models.
        rooms = cae_home_models.Room.objects.all()

        # Generate models equal to model count.
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
