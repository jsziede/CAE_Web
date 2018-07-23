"""
Admin views for CAE Web Core app.
"""

from django.contrib import admin

from . import models


class RoomEventInline(admin.TabularInline):
    model = models.RoomEvent


class RoomEventAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('room', 'event_type', 'start_time', 'end_time', 'title',)

    # Fields to filter by in admin list view.
    list_filter = ('room', 'event_type',)

    # Fields to search in admin list view.
    search_fields = ['title',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'room', 'event_type', 'start_time', 'end_time', 'title', 'description', 'rrule',
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )

admin.site.register(models.RoomEvent, RoomEventAdmin)
