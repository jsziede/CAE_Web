from django.contrib import admin
from .models import RoomCheckout

class RoomCheckoutAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('checkout', 'room', 'student', 'employee', 'checkout_date', 'date_created', 'date_modified')

    # Fields to filter by in admin list view.
    list_filter = ('room', 'student', 'employee')

    # Fields to search in admin list view.
    search_fields = ['room', 'student', 'employee']

    # Read only fields for admin detail view.
    readonly_fields = ('checkout', 'date_created', 'date_modified')

admin.site.register(RoomCheckout, RoomCheckoutAdmin)

class OpenCloseChecklistAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('checklist', 'employee', 'checklist_item', 'name', 'date_created', 'date_modified')

    # Fields to filter by in admin list view.
    list_filter = ('checklist', 'employee', 'name')

    # Fields to search in admin list view.
    search_fields = ['checklist', 'employee', 'name']

    # Read only fields for admin detail view.
    readonly_fields = ('checklist', 'date_created', 'date_modified')

admin.site.register(OpenCloseChecklist, OpenCloseChecklistAdmin)

class ChecklistItemAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('checklist_item', 'task', 'date_created', 'date_modified')

    # Fields to filter by in admin list view.
    list_filter = ('checklist_item', 'task')

    # Fields to search in admin list view.
    search_fields = ['checklist_item', 'task']

    # Read only fields for admin detail view.
    readonly_fields = ('checklist_item', 'date_created', 'date_modified')

admin.site.register(ChecklistItem, ChecklistItemAdmin)
