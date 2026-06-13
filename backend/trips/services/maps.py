import math
import re
from dataclasses import dataclass

import requests
from django.conf import settings


class MapServiceError(Exception):
    pass


@dataclass(frozen=True)
class GeoPoint:
    label: str
    lat: float
    lng: float
    display_name: str


def haversine_miles(a: dict, b: dict) -> float:
    radius_miles = 3958.8
    lat1 = math.radians(a["lat"])
    lat2 = math.radians(b["lat"])
    dlat = lat2 - lat1
    dlng = math.radians(b["lng"] - a["lng"])
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return 2 * radius_miles * math.asin(math.sqrt(h))


def interpolate_point(points: list[dict], target_miles: float) -> dict:
    if not points:
        return {"lat": 0.0, "lng": 0.0}
    if target_miles <= 0:
        return points[0]

    traveled = 0.0
    for start, end in zip(points, points[1:]):
        segment = haversine_miles(start, end)
        if traveled + segment >= target_miles and segment > 0:
            ratio = (target_miles - traveled) / segment
            return {
                "lat": start["lat"] + (end["lat"] - start["lat"]) * ratio,
                "lng": start["lng"] + (end["lng"] - start["lng"]) * ratio,
            }
        traveled += segment
    return points[-1]


class MapClient:
    def __init__(self, session=None):
        self.session = session or requests.Session()
        self.headers = {"User-Agent": settings.MAP_USER_AGENT}

    def geocode(self, label: str, query: str) -> GeoPoint:
        coordinate_match = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$", query)
        if coordinate_match:
            lat = float(coordinate_match.group(1))
            lng = float(coordinate_match.group(2))
            return GeoPoint(label=label, lat=lat, lng=lng, display_name=f"{lat:.5f}, {lng:.5f}")

        response = self.session.get(
            f"{settings.NOMINATIM_BASE_URL}/search",
            params={"q": query, "format": "json", "limit": 1, "addressdetails": 1},
            headers=self.headers,
            timeout=15,
        )
        if response.status_code >= 400:
            raise MapServiceError(f"Unable to geocode {label}.")

        results = response.json()
        if not results:
            raise MapServiceError(f"No map result found for {label}: {query}")

        match = results[0]
        return GeoPoint(
            label=label,
            lat=float(match["lat"]),
            lng=float(match["lon"]),
            display_name=match.get("display_name", query),
        )

    def reverse_geocode(self, lat: float, lng: float) -> dict:
        response = self.session.get(
            f"{settings.NOMINATIM_BASE_URL}/reverse",
            params={"lat": lat, "lon": lng, "format": "json", "zoom": 18, "addressdetails": 1},
            headers=self.headers,
            timeout=15,
        )
        if response.status_code >= 400:
            raise MapServiceError("Unable to identify current location.")

        payload = response.json()
        address = payload.get("address") or {}
        city = address.get("city") or address.get("town") or address.get("village") or address.get("hamlet")
        state = address.get("state")
        state_code = address.get("state_code")
        location_parts = [part for part in [city, state_code or state] if part]
        short_location = ", ".join(location_parts)

        return {
            "location": payload.get("display_name") or f"{lat:.5f}, {lng:.5f}",
            "shortLocation": short_location or f"{lat:.5f}, {lng:.5f}",
            "lat": lat,
            "lng": lng,
        }

    def route(self, points: list[GeoPoint]) -> dict:
        coordinate_path = ";".join(f"{point.lng},{point.lat}" for point in points)
        response = self.session.get(
            f"{settings.OSRM_BASE_URL}/route/v1/driving/{coordinate_path}",
            params={"overview": "full", "geometries": "geojson", "steps": "false"},
            headers=self.headers,
            timeout=25,
        )
        if response.status_code >= 400:
            raise MapServiceError("Unable to build route from OSRM.")

        payload = response.json()
        routes = payload.get("routes") or []
        if not routes:
            raise MapServiceError("OSRM did not return a route.")

        route = routes[0]
        geometry = [
            {"lat": lat, "lng": lng}
            for lng, lat in route["geometry"]["coordinates"]
        ]
        legs = [
            {
                "distanceMiles": leg["distance"] / 1609.344,
                "durationHours": leg["duration"] / 3600,
            }
            for leg in route.get("legs", [])
        ]

        return {
            "geometry": geometry,
            "distanceMiles": route["distance"] / 1609.344,
            "durationHours": route["duration"] / 3600,
            "legs": legs,
        }

    def build_trip_route(self, current: str, pickup: str, dropoff: str) -> dict:
        waypoints = [
            self.geocode("Current", current),
            self.geocode("Pickup", pickup),
            self.geocode("Dropoff", dropoff),
        ]
        route = self.route(waypoints)
        route["waypoints"] = [
            {
                "type": waypoint.label.lower(),
                "label": waypoint.label,
                "location": waypoint.display_name,
                "lat": waypoint.lat,
                "lng": waypoint.lng,
            }
            for waypoint in waypoints
        ]
        return route
