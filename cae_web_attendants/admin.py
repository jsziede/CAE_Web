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