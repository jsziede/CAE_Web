"""
Models for CAE Web Attendants app.
"""
from datetime import datetime
from django.db import models

class RoomCheckout(models.Model):
    # Primary key
    checkout = models.AutoField(primary_key=True)

    # Foreign keys
    # check if these are supposed to be cascaded
    room = models.ForeignKey('cae_home.Room', on_delete=models.CASCADE)
    employee = models.ForeignKey('cae_home.User', on_delete=models.CASCADE)
    student = models.ForeignKey('cae_home.WmuUser', on_delete=models.CASCADE)

    # Fields specific to RoomCheckout model
    checkout_date = models.DateTimeField(default=datetime.now)

    # Self-setting/Non-user-editable fields.
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Room Checkout"
        verbose_name_plural = "Room Checkouts"
        # check if this needs to be ordered by date or not
        ordering = ('-checkout_date',)
