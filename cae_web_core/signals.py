"""CAE Web Core Django Signals"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save, post_delete

from . import models
from .consumers import GROUP_UPDATE_ROOM_EVENT


channel_layer = get_channel_layer()


def on_room_event_changed(sender, **kwargs):
    """Notify channels through redis that a room changed"""
    instance = kwargs.get('instance')
    if instance:
        # NOTE: if deleted, insance is no longer in database
        async_to_sync(channel_layer.group_send)(
            GROUP_UPDATE_ROOM_EVENT,
            {
                "type": "on_update_room_event",
                "pk": instance.pk,
                "start_time": instance.start_time.isoformat(),
                "end_time": instance.end_time.isoformat(),
                "room": instance.room_id,
            },
        )

post_save.connect(on_room_event_changed, sender=models.RoomEvent)
post_delete.connect(on_room_event_changed, sender=models.RoomEvent)
