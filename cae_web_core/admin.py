"""
Admin views for CAE Web Core app.
"""

from django.contrib import admin

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
admin.site.register(models.RoomEvent, RoomEventAdmin)
admin.site.register(models.UploadedSchedule, UploadedScheduleAdmin)
