from django.urls import path

from .views import PlanTripView, ReverseGeocodeView


urlpatterns = [
    path("plan/", PlanTripView.as_view(), name="trip-plan"),
    path("reverse-geocode/", ReverseGeocodeView.as_view(), name="reverse-geocode"),
]
