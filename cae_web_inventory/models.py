"""
Models for CAE Web Inventory app.
"""

from django.db import models
from django.core.exceptions import ValidationError


MAX_LENGTH = 255


class Item(models.Model):
    """
    An item to purchase.
    """
    # Model fields.
    name = models.CharField(max_length=MAX_LENGTH)
    description = models.TextField(blank=True, default='')
    current_quantity = models.IntegerField(default=0)
    email_threshold = models.IntegerField()
    active = models.BooleanField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    def __str__(self):
        return '{0}'.format(self.name)

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(Item, self).save(*args, **kwargs)


class ItemAdjustment(models.Model):
    """
    An adjustment to an item's count.
    """
    # Relationship keys.
    user = models.ForeignKey('cae_home.User', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)

    # Model fields.
    adjustment_amount = models.IntegerField()

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item Adjustment"
        verbose_name_plural = "Item Adjustments"

    def __str__(self):
        return '{0} adjusted by {1}'.format(self.item, self.adjustment_amount)

    def clean(self, *args, **kwargs):
        """
        Custom cleaning implementation. Includes validation, setting fields, etc.
        """
        # Check that adjustment amount is not 0.
        if self.adjustment_amount is 0:
            raise ValidationError('Adjustment amount must be positive or negative, not 0.')

    def save(self, *args, **kwargs):
        """
        Modify model save behavior.
        """
        # Save model.
        self.full_clean()
        super(ItemAdjustment, self).save(*args, **kwargs)
