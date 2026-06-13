from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ReverseGeocodeRequestSerializer, TripPlanRequestSerializer
from .services.hos import HosPlanner
from .services.logs import render_log_sheets
from .services.maps import MapClient, MapServiceError


class PlanTripView(APIView):
    def post(self, request):
        # The endpoint intentionally stays stateless: every request contains all
        # trip/log details, and the response contains the complete plan.
        serializer = TripPlanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            # MapClient owns all third-party map API details so the view stays
            # focused on request orchestration.
            route = MapClient().build_trip_route(
                data["currentLocation"],
                data["pickupLocation"],
                data["dropoffLocation"],
            )
        except MapServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        # The HOS planner produces structured events/stops; the log renderer
        # turns those same events into paper-style PNG log sheets.
        plan = HosPlanner(route, data["currentCycleUsedHours"]).build()
        log_sheets = render_log_sheets(
            plan["events"],
            route,
            log_details={
                "driverName": data.get("driverName"),
                "truckTrailerNumber": data.get("truckTrailerNumber"),
                "carrierName": data.get("carrierName"),
                "mainOfficeAddress": data.get("mainOfficeAddress"),
                "homeTerminalAddress": data.get("homeTerminalAddress"),
            },
        )

        return Response(
            {
                # The frontend needs route geometry for Leaflet and the
                # summary/stops/events/logSheets for the results panels.
                "route": {
                    "geometry": route["geometry"],
                    "waypoints": route["waypoints"],
                    "distanceMiles": plan["summary"]["distanceMiles"],
                    "durationHours": plan["summary"]["drivingHours"],
                },
                "summary": {
                    **plan["summary"],
                    "logSheets": len(log_sheets),
                    "assumptions": [
                        "Property-carrying driver",
                        "70-hour/8-day cycle",
                        "No adverse driving conditions",
                        "Fuel at least once every 1,000 miles",
                        "1 hour each for pickup and dropoff",
                    ],
                },
                "stops": plan["stops"],
                "events": plan["events"],
                "logSheets": log_sheets,
                "warnings": plan["warnings"],
                "attribution": {
                    "geocoding": "OpenStreetMap Nominatim with Photon fallback",
                    "routing": "OSRM public demo server",
                    "tiles": "OpenStreetMap contributors",
                },
            }
        )


class ReverseGeocodeView(APIView):
    def get(self, request):
        # Used by the "Use browser location" button to convert browser GPS
        # coordinates into a readable address before trip planning.
        serializer = ReverseGeocodeRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            location = MapClient().reverse_geocode(data["lat"], data["lng"])
        except MapServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(location)
