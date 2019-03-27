from django.contrib import admin
from .models import RoomCheckout, ChecklistTemplate, ChecklistItem, ChecklistInstance

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

class ChecklistTemplateAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('pk', 'title', 'room', 'date_created', 'date_modified')

    # Fields to filter by in admin list view.
    list_filter = ('title', 'room')

    # Fields to search in admin list view.
    search_fields = ['title', 'room']

    # Read only fields for admin detail view.
    readonly_fields = ('pk', 'title', 'room', 'checklist_item', 'date_created', 'date_modified')

admin.site.register(ChecklistTemplate, ChecklistTemplateAdmin)

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

class ChecklistInstanceAdmin(admin.ModelAdmin):
    # Fields to display in admin list view.
    list_display = ('pk', 'template', 'room', 'employee', 'title', 'date_completed', 'date_created', 'date_modified')

    # Fields to filter by in admin list view.
    list_filter = ('template', 'room', 'employee', 'title', 'date_completed', )

    # Fields to search in admin list view.
    search_fields = ['pk', 'template', 'room', 'employee', 'title', 'date_completed']

    # Read only fields for admin detail view.
    readonly_fields = ('pk', 'date_created', 'date_modified')

admin.site.register(ChecklistInstance, ChecklistInstanceAdmin)
