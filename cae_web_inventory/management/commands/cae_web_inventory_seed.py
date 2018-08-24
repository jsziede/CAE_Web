"""
Seeder command that initializes user models.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from random import randint

from apps.CAE_Web.cae_web_inventory import models
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

        print('\nCAE_WEB_INVENTORY: Seed command has been called.')
        self.create_items(model_count)
        self.create_item_adjustments(model_count)

        print('CAE_WEB_INVENTORY: Seeding complete.')

    def create_items(self, model_count):
        """
        Create Asset models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Count number of models already created.
        pre_initialized_count = len(models.Item.objects.all())

        for i in range(model_count - pre_initialized_count):
            # Generate name.
            name = faker_factory.word()

            # Generate description.
            sentence_count = randint(1, 5)
            description = faker_factory.paragraph(nb_sentences=sentence_count)

            # Generate quantity.
            current_quantity = randint(0, 9)

            # Generate threshold.
            email_threshold = randint(0, 9)

            # Determine if active. 70% chance of being true.
            if randint(0, 9) < 7:
                active = True
            else:
                active = False

            models.Item.objects.create(
                name=name,
                description=description,
                current_quantity=current_quantity,
                email_threshold=email_threshold,
                active=active,
            )
        print('Populated item models.')

    def create_item_adjustments(self, model_count):
        """
        Create Asset models.
        """
        # Generate random data.
        faker_factory = Faker()

        # Get all related models.
        users = cae_home_models.User.objects.all()
        items = models.Item.objects.all()

        # Count number of models already created.
        pre_initialized_count = len(models.ItemAdjustment.objects.all())

        # Generate models equal to model count.
        for i in range(model_count - pre_initialized_count):
            # Get User.
            index = randint(0, len(users) - 1)
            user = users[index]

            # Get Item.
            index = randint(0, len(items) - 1)
            item = items[index]

            # Generate adjustment amount. 50% chance of being positive or negative, but is never 0.
            if randint(0, 1) is 1:
                adjustment_amount = randint(-9, -1)
            else:
                adjustment_amount = randint(1, 9)

            models.ItemAdjustment.objects.create(
                user=user,
                item=item,
                adjustment_amount=adjustment_amount,
            )
        print('Populated item adjustment models.')
