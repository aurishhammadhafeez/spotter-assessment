def fake_route(distance_miles=520, duration_hours=8):
    first_leg_miles = distance_miles * 0.3
    second_leg_miles = distance_miles - first_leg_miles
    first_leg_hours = duration_hours * 0.3
    second_leg_hours = duration_hours - first_leg_hours
    return {
        "geometry": [
            {"lat": 32.7767, "lng": -96.7970},
            {"lat": 30.2672, "lng": -97.7431},
            {"lat": 39.7392, "lng": -104.9903},
        ],
        "distanceMiles": distance_miles,
        "durationHours": duration_hours,
        "legs": [
            {"distanceMiles": first_leg_miles, "durationHours": first_leg_hours},
            {"distanceMiles": second_leg_miles, "durationHours": second_leg_hours},
        ],
        "waypoints": [
            {"type": "current", "label": "Current", "location": "Dallas, TX", "lat": 32.7767, "lng": -96.7970},
            {"type": "pickup", "label": "Pickup", "location": "Austin, TX", "lat": 30.2672, "lng": -97.7431},
            {"type": "dropoff", "label": "Dropoff", "location": "Denver, CO", "lat": 39.7392, "lng": -104.9903},
        ],
    }

