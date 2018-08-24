"""
Admin view for CAE Web Inventory App.
"""

from django.contrib import admin

from . import models


class ItemAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('name', 'current_quantity', 'email_threshold', 'active',)

    # Fields to filter by in admin list view.
    list_filter = ('active',)

    # Fields to search in admin list view.
    search_fields = ['name', 'description',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'current_quantity', 'email_threshold', 'active',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


class ItemAdjustmentAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('item', 'adjustment_amount', 'user',)

    # Fields to filter by in admin list view.
    list_filter = ('item',)

    # Fields to search in admin list view.
    search_fields = ['item',]

    # Read only fields for admin detail view.
    readonly_fields = ('date_created', 'date_modified')

    # Organize fieldsets for admin detail view.
    fieldsets = (
        (None, {
            'fields': ('item', 'adjustment_amount', 'user',)
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('date_created', 'date_modified',),
        }),
    )


admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.ItemAdjustment, ItemAdjustmentAdmin)
