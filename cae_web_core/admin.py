"""
Admin views for CAE Web Core app.
"""

from django.contrib import admin

from . import forms, models


class DepartmentAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)

    # Fields to search in admin list view.
    search_fields = ['name',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


class RoomTypeAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name',)

    # Fields to search in admin list view.
    search_fields = ['name',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )

class RoomAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name', 'capacity', 'room_type',)

    # Fields to filter by in admin list view.
    list_filter = ('room_type', 'department',)

    # Fields to search in admin list view.
    search_fields = ['name', 'capacity',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name', 'room_type', 'department', 'capacity',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.RoomType, RoomTypeAdmin)
admin.site.register(models.Room, RoomAdmin)
