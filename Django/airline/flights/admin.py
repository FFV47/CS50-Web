from django.contrib import admin
from flights.models import Airport, Flight, Passenger


# Register your models here.
class FlightAdmin(admin.ModelAdmin):
    list_display = ("id", "origin", "destination", "duration")
    list_display_links = ("id", "origin", "destination", "duration")


class PassengerAdmin(admin.ModelAdmin):
    list_display = ("id", "first", "last")
    list_display_links = ("id", "first", "last")
    filter_horizontal = ("flights",)


admin.site.register(Airport)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Passenger, PassengerAdmin)
