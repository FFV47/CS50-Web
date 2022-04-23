from django import forms
from flights.models import Passenger


class NewPassenger(forms.Form):
    passenger = forms.ModelChoiceField(queryset=None)

    def __init__(self, flight_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["passenger"].queryset = Passenger.objects.exclude(flights=flight_id)
