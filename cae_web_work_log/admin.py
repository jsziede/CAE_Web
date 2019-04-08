"""
Admin views for CAE Work Log app.
"""

from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models import Q

from . import models


class TimeframeTypeAdmin(admin.ModelAdmin):

    # Fields to display in admin list view.
    list_display = (
        'name',
    )

    # Read only fields for admin detail view.
    readonly_fields = (
        'id', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        ('', {
            'fields': ('name',)
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('id', 'date_created', 'date_modified', )
        }),
    )


class WorkLogSetAdmin(admin.ModelAdmin):

    # Fields to display in admin list view.
    list_display = (
        'group', 'timeframe_type',
    )

    # Read only fields for admin detail view.
    readonly_fields = (
        'id', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        ('', {
            'fields': ('group', 'timeframe_type',)
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('id', 'date_created', 'date_modified', )
        }),
    )


class LogEntryToGroupFilter(admin.SimpleListFilter):
    """
    Filter for WorkLogEntries to show by User Group.
    """
    title = ('User Group')
    parameter_name = 'group'

    def lookups(self, request, model_admin):
        return (
            # ('', ('All')),
            ('cae-admin', ('CAE Admin')),
            ('cae-programmer', ('CAE Programmer'))
        )

    def queryset(self, request, queryset):
        if self.value() == 'cae-admin':
            return queryset.filter(log_set__group__name='CAE Admin')
        if self.value() == 'cae-programmer':
            return queryset.filter(log_set__group__name='CAE Programmer')


class WorkLogEntryAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = (
        'user', 'log_set', 'entry_date',
    )

    # Fields to search in admin list view.
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
    ]

    # Fields to filter by in admin list view.
    list_filter = (
        LogEntryToGroupFilter,
        'log_set__timeframe_type',
    )

    # Read only fields for admin detail view.
    readonly_fields = (
        'id', 'date_created', 'date_modified',
    )

    # Fieldset organization for admin detail view.
    fieldsets = (
        ('', {
            'fields': ('user', 'log_set', 'entry_date', 'description',)
        }),
        ('Advanced', {
            'classes': ('collapse', ),
            'fields': ('id', 'date_created', 'date_modified', )
        }),
    )


admin.site.register(models.TimeFrameType, TimeframeTypeAdmin)
admin.site.register(models.WorkLogSet, WorkLogSetAdmin)
admin.site.register(models.WorkLogEntry, WorkLogEntryAdmin)
