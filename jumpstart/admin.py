from django.contrib import admin
from .models import Customer, Event, Ticket


class EventsAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type')
    ordering = ['name']


class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'customer', 'reservation_date']
    ordering = ['reservation_date']


# Register your models here.
admin.site.register(Customer)
admin.site.register(Event, EventsAdmin)
admin.site.register(Ticket, TicketAdmin)
