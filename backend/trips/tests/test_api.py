from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from trips.services.maps import MapServiceError
from trips.tests.helpers import fake_route


class TripPlanApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payload = {
            "currentLocation": "Dallas, TX",
            "pickupLocation": "Austin, TX",
            "dropoffLocation": "Denver, CO",
            "currentCycleUsedHours": 12,
        }

    @patch("trips.views.MapClient.build_trip_route")
    def test_plan_endpoint_returns_route_events_and_logs(self, mock_route):
        mock_route.return_value = fake_route()

        response = self.client.post("/api/trips/plan/", self.payload, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("route", response.data)
        self.assertGreater(len(response.data["events"]), 0)
        self.assertEqual(response.data["logSheets"][0]["totals"]["total"], 24.0)

    @patch("trips.views.MapClient.build_trip_route")
    def test_plan_endpoint_accepts_logbook_header_details(self, mock_route):
        mock_route.return_value = fake_route()

        response = self.client.post(
            "/api/trips/plan/",
            {
                **self.payload,
                "driverName": "Aurish Hammad",
                "truckTrailerNumber": "Truck 77 / Trailer 88",
                "carrierName": "Spotter Demo Carrier",
                "mainOfficeAddress": "Dallas, TX",
                "homeTerminalAddress": "Dallas Terminal, Dallas, TX",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["logSheets"][0]["totals"]["total"], 24.0)

    def test_plan_endpoint_rejects_invalid_cycle_hours(self):
        response = self.client.post(
            "/api/trips/plan/",
            {**self.payload, "currentCycleUsedHours": 71},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    @patch("trips.views.MapClient.build_trip_route")
    def test_plan_endpoint_returns_bad_gateway_for_map_failure(self, mock_route):
        mock_route.side_effect = MapServiceError("Unable to build route from OSRM.")

        response = self.client.post("/api/trips/plan/", self.payload, format="json")

        self.assertEqual(response.status_code, 502)
        self.assertIn("detail", response.data)

    @patch("trips.views.MapClient.reverse_geocode")
    def test_reverse_geocode_endpoint_returns_location(self, mock_reverse):
        mock_reverse.return_value = {
            "location": "Dallas, Dallas County, Texas, United States",
            "shortLocation": "Dallas, TX",
            "lat": 32.7767,
            "lng": -96.797,
        }

        response = self.client.get("/api/trips/reverse-geocode/?lat=32.7767&lng=-96.797")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["shortLocation"], "Dallas, TX")

    def test_reverse_geocode_endpoint_validates_coordinates(self):
        response = self.client.get("/api/trips/reverse-geocode/?lat=123&lng=-96.797")

        self.assertEqual(response.status_code, 400)
