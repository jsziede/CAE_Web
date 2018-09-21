"""
Seeder command that initializes user models.
"""

import datetime, pytz
from django.core.exceptions import ValidationError
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
        self.create_pay_periods(model_count)
        self.create_employee_shifts(model_count)
        self.create_room_events(model_count)

        print('CAE_WEB_CORE: Seeding complete.')

    def create_pay_periods(self, model_count):
        """
        Create Pay Period models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.PayPeriod.objects.all())

        # First pay period with valid shift data, in production database. Starting here for consistency.
        date_holder = datetime.datetime.strptime('2015 05 25 00 00 00', '%Y %m %d %H %M %S')

        # Check that time is daylight savings compliant.
        date_holder = self.normalize_for_daylight_savings(date_holder)

        # Generate models equal to model count.
        for i in range(model_count - pre_initialized_count):
            models.PayPeriod.objects.create(
                period_start=date_holder,
            )
            date_holder = date_holder + timezone.timedelta(days=14)
            date_holder = self.normalize_for_daylight_savings(date_holder)
        print('Populated pay period models.')

    def normalize_for_daylight_savings(self, date_holder):
        """
        Checks and normalizes for daylight savings.
        We want the date to always be midnight, regardless of time of year.
        """
        # First get local server timezone.
        server_timezone = pytz.timezone('America/Detroit')

        # Then localize the given date, ignoring timezone info if provided.
        # (We don't want the timezone adjustment for midnight. We want actual midnight, unconditionally.)
        date_holder_with_timezone = server_timezone.localize(date_holder.replace(tzinfo=None))

        return date_holder_with_timezone

    def create_employee_shifts(self, model_count):
        """
        Create Employee Shift models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.EmployeeShift.objects.all())

        # Get all related models.
        users = cae_home_models.User.objects.all()
        pay_periods = models.PayPeriod.objects.all()[:model_count/20]

        date_holder = timezone.now()
        # Generate models equal to model count.
        for i in range(model_count - pre_initialized_count):
            # Get User.
            index = randint(0, len(users) - 1)
            user = users[index]

            # Get pay period.
            index = randint(0, len(pay_periods) - 1)
            pay_period = pay_periods[index]

            # Calculate clock in/clock out times.
            clock_in = pay_period.period_start + timezone.timedelta(
                days=randint(0, 6),
                hours=randint(8, 16),
                minutes=randint(0,59)
            )
            clock_out = clock_in + timezone.timedelta(hours=randint(1, 4), minutes=randint(0, 59))

            try:
                models.EmployeeShift.objects.create(
                    employee=user,
                    pay_period=pay_period,
                    clock_in=clock_in,
                    clock_out=clock_out,
                )
            except ValidationError:
                # Likely due to overlapping shift times. Nothing can be done about this without removing the random
                # generation aspect. If we want that, we should use fixtures instead.
                pass

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
