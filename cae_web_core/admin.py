"""
Admin views for CAE Web Core app.
"""

from django.contrib import admin
from django.utils.html import format_html

from . import models


class RoomEventInline(admin.TabularInline):
    model = models.RoomEvent


class PayPeriodAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('date_start', 'date_end',)

    # Fields to search in admin list view.
    search_fields = ['date_start', 'date_end', ]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified',)

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'date_start', 'date_end',
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


class EmployeeShiftAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('pay_period', 'employee', 'clock_in', 'clock_out', 'error_flag',)

    # Fields to filter by in admin list view.
    list_filter = ('error_flag', 'employee', 'pay_period',)

    # Fields to search in admin list view.
    search_fields = ['id', 'clock_in', 'clock_out',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified',)

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'pay_period', 'employee', 'clock_in', 'clock_out', 'error_flag',
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


class EventTypeAdmin(admin.ModelAdmin):
    """
    Used for both RoomEventType and AvailabilityEventType
    """
    list_display = ('name', 'fg_color_span', 'bg_color_span')

    def fg_color_span(self, instance):
        """Show preview of colors"""
        return format_html('<span style="display: inline-block; padding: 5px; color: {0}; background-color: {1}; border: 1px solid gray;">{0}</span>', instance.fg_color, instance.bg_color)
    fg_color_span.admin_order_field = 'fg_color'
    fg_color_span.short_description = 'FG Color'

    def bg_color_span(self, instance):
        """Show preview of colors"""
        return format_html('<span style="display: inline-block; padding: 5px; color: {0}; background-color: {1}; border: 1px solid gray;">{1}</span>', instance.fg_color, instance.bg_color)
    bg_color_span.admin_order_field = 'bg_color'
    bg_color_span.short_description = 'BG Color'


class RoomEventAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('room', 'event_type', 'start_time', 'end_time', 'title',)

    # Fields to filter by in admin list view.
    list_filter = ('room__room_type', 'event_type',)

    # Fields to search in admin list view.
    search_fields = ['title',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified',)

    # Allow filtering by event start
    date_hierarchy = 'start_time'

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'room', 'event_type', 'start_time', 'end_time', 'title', 'description', 'rrule', 'duration'
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )

class AvailabilityEventAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('employee', 'event_type', 'start_time', 'end_time')

    # Fields to filter by in admin list view.
    list_filter = ['event_type', 'employee']

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Allow filtering by event start
    date_hierarchy = 'start_time'

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': (
                'employee', 'event_type', 'start_time', 'end_time', 'rrule', 'duration'
            )
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


class UploadedScheduleRoomEventInline(admin.TabularInline):
    model = models.UploadedSchedule.events.through
    extra = 0
    raw_id_fields = ['roomevent']


class UploadedScheduleAdmin(admin.ModelAdmin):
    model = models.UploadedSchedule
    list_display = ['name']
    inlines = [UploadedScheduleRoomEventInline]
    exclude = ['events']


admin.site.register(models.PayPeriod, PayPeriodAdmin)
admin.site.register(models.EmployeeShift, EmployeeShiftAdmin)
admin.site.register(models.AvailabilityEventType, EventTypeAdmin)
admin.site.register(models.AvailabilityEvent, AvailabilityEventAdmin)
admin.site.register(models.RoomEventType, EventTypeAdmin)
admin.site.register(models.RoomEvent, RoomEventAdmin)
admin.site.register(models.UploadedSchedule, UploadedScheduleAdmin)
