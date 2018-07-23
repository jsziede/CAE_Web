"""
Admin views for CAE Web Core app.
"""

from django.contrib import admin

from . import models


class RoomEventInline(admin.TabularInline):
    model = models.RoomEvent


admin.site.register(models.RoomEvent)
