"""CAE Web Core Django Signals"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from . import models
from .consumers import GROUP_UPDATE_ROOM_EVENT, GROUP_UPDATE_AVAILABILITY_EVENT


channel_layer = get_channel_layer()


@receiver([post_save, post_delete], sender=models.RoomEvent, dispatch_uid="room_event")
def on_room_event_changed(sender, **kwargs):
    """Notify channels through redis that a room event changed"""
    instance = kwargs.get('instance')
    if instance:
        # NOTE: if deleted, instance is no longer in database
        async_to_sync(channel_layer.group_send)(
            GROUP_UPDATE_ROOM_EVENT,
            {
                "type": "on_update_room_event",
                "pk": instance.pk,
                "start_time": instance.start_time.isoformat(),
                "end_time": instance.end_time.isoformat() if instance.end_time else None,
                "room": instance.room_id,
            },
        )


@receiver([post_save, post_delete], sender=models.AvailabilityEvent, dispatch_uid="availability_event")
def on_availability_event_changed(sender, **kwargs):
    """Notify channels through redis that an availability event changed"""
    instance = kwargs.get('instance')
    if instance:
        # NOTE: if deleted, instance is no longer in database
        async_to_sync(channel_layer.group_send)(
            GROUP_UPDATE_AVAILABILITY_EVENT,
            {
                "type": "on_update_availability_event",
                "pk": instance.pk,
                "start_time": instance.start_time.isoformat(),
                "end_time": instance.end_time.isoformat() if instance.end_time else None,
                "employee": instance.employee_id,
            },
        )
