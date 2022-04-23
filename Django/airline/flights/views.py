from django.http import HttpResponseBadRequest, Http404
from django.http.request import HttpRequest
from django.shortcuts import redirect, render

from .models import Flight, Passenger


# Create your views here.
def index(request: HttpRequest):
    return render(request, "flights/index.html", {"flights": Flight.objects.all()})


def flight(request: HttpRequest, flight_id: int):
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        raise Http404("Flight not found.")
    return render(
        request,
        "flights/flight.html",
        {
            "flight": flight,
            "passengers": flight.passengers.all(),
            "non_passengers": Passenger.objects.exclude(flights=flight).all(),
        },
    )


def book(request: HttpRequest, flight_id: int):
    if request.method == "POST":
        try:
            passenger = Passenger.objects.get(pk=int(request.POST["passenger"]))
            flight = Flight.objects.get(pk=flight_id)
        except KeyError:
            return HttpResponseBadRequest("Bad Request: no flight chosen")
        except Flight.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: flight does not exist")
        except Passenger.DoesNotExist:
            return HttpResponseBadRequest("Bad Request: passenger does not exist")
        passenger.flights.add(flight)
        return redirect("flights:flight", flight_id)
