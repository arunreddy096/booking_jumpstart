from django.contrib import admin
from .models import Customer, Booking, Event, Ticket


class EventsAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type')
    ordering = ['name']


# Register your models here.
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(Event, EventsAdmin)
admin.site.register(Ticket)
