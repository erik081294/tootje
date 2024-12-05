from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'start_time', 'end_time', 'status', 'total_cost')
    list_filter = ('status', 'start_time')
    search_fields = ('car__brand', 'car__model', 'user__username', 'user__email')
    date_hierarchy = 'start_time'
