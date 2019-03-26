from django.contrib import admin
from .models import RoomCheckout, OpenCloseChecklist, ChecklistItem

class RoomCheckoutAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('pk', 'room', 'student', 'employee', 'checkout_date', 'date_created', 'date_modified')

    # Fields to filter by in admin list view.
    list_filter = ('room', 'student', 'employee')

    # Fields to search in admin list view.
    search_fields = ['room', 'student', 'employee']

    # Read only fields for admin detail view.
    readonly_fields = ('pk', 'date_created', 'date_modified')

admin.site.register(RoomCheckout, RoomCheckoutAdmin)

class OpenCloseChecklistAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('pk', 'employee', 'checklist_item', 'name', 'date_created', 'date_modified')

    # Fields to filter by in admin list view.
    list_filter = ('employee', 'name')

    # Fields to search in admin list view.
    search_fields = ['pk', 'employee', 'name']

    # Read only fields for admin detail view.
    readonly_fields = ('pk', 'date_created', 'date_modified')

admin.site.register(OpenCloseChecklist, OpenCloseChecklistAdmin)

class ChecklistItemAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('pk', 'task', 'date_created', 'date_modified')

    # Fields to filter by in admin list view.
    list_filter = ('task', )

    # Fields to search in admin list view.
    search_fields = ['pk', 'task']

    # Read only fields for admin detail view.
    readonly_fields = ('pk', 'date_created', 'date_modified')

admin.site.register(ChecklistItem, ChecklistItemAdmin)
