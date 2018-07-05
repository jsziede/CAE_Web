"""CAE Web Admin"""
from django.contrib import admin

from .models import Room

# TODO: Each pluggable app should have it's own admin?


class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'capacity', 'room_type']
    list_filter = ['room_type']

admin.site.register(Room, RoomAdmin)
