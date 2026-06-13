from datetime import date

from django.test import SimpleTestCase

from trips.services.hos import HosPlanner
from trips.services.logs import render_log_sheets
from trips.tests.helpers import fake_route


class HosPlannerTests(SimpleTestCase):
    def test_short_trip_generates_pickup_dropoff_and_single_log(self):
        route = fake_route(distance_miles=520, duration_hours=8)
        plan = HosPlanner(route, current_cycle_used_hours=12).build()
        event_types = [event["type"] for event in plan["events"]]
        sheets = render_log_sheets(plan["events"], route)

        self.assertIn("pickup", event_types)
        self.assertIn("dropoff", event_types)
        self.assertEqual(len(sheets), 1)
        self.assertEqual(sheets[0]["totals"]["total"], 24.0)

    def test_long_trip_adds_fuel_breaks_resets_and_multiple_logs(self):
        route = fake_route(distance_miles=1800, duration_hours=32)
        plan = HosPlanner(route, current_cycle_used_hours=8).build()
        stop_types = [stop["type"] for stop in plan["stops"]]
        sheets = render_log_sheets(plan["events"], route)

        self.assertIn("fuel", stop_types)
        self.assertIn("break", stop_types)
        self.assertIn("reset", stop_types)
        self.assertGreaterEqual(len(sheets), 2)
        self.assertTrue(all(sheet["totals"]["total"] == 24.0 for sheet in sheets))

    def test_cycle_near_limit_schedules_restart(self):
        route = fake_route(distance_miles=300, duration_hours=6)
        plan = HosPlanner(route, current_cycle_used_hours=69.75).build()

        self.assertTrue(any("34-hour restart" in warning for warning in plan["warnings"]))
        self.assertIn("restart", [event["type"] for event in plan["events"]])

    def test_pickup_and_dropoff_are_one_hour_each(self):
        route = fake_route(distance_miles=400, duration_hours=7)
        plan = HosPlanner(route, current_cycle_used_hours=10).build()
        pickup = next(event for event in plan["events"] if event["type"] == "pickup")
        dropoff = next(event for event in plan["events"] if event["type"] == "dropoff")

        self.assertEqual(pickup["durationHours"], 1.0)
        self.assertEqual(dropoff["durationHours"], 1.0)

    def test_log_sheet_dates_increment_from_start_date(self):
        route = fake_route(distance_miles=1800, duration_hours=32)
        plan = HosPlanner(route, current_cycle_used_hours=8).build()
        sheets = render_log_sheets(plan["events"], route, start_date=date(2026, 6, 12))

        self.assertGreaterEqual(len(sheets), 2)
        self.assertEqual(sheets[0]["date"], {"iso": "2026-06-12", "month": 6, "day": 12, "year": 2026})
        self.assertEqual(sheets[1]["date"], {"iso": "2026-06-13", "month": 6, "day": 13, "year": 2026})

    def test_log_sheet_mileage_splits_driving_across_midnight(self):
        route = fake_route(distance_miles=400, duration_hours=8)
        events = [
            {
                "status": "driving",
                "type": "driving",
                "label": "Driving",
                "location": "Route mile 0",
                "startHour": 20,
                "endHour": 28,
                "durationHours": 8,
                "routeMile": 400,
                "startRouteMile": 0,
                "endRouteMile": 400,
                "distanceMiles": 400,
            }
        ]

        sheets = render_log_sheets(events, route, start_date=date(2026, 6, 12))

        self.assertEqual(sheets[0]["totals"]["milesDrivingToday"], 200.0)
        self.assertEqual(sheets[0]["totals"]["cumulativeMileage"], 200.0)
        self.assertEqual(sheets[1]["totals"]["milesDrivingToday"], 200.0)
        self.assertEqual(sheets[1]["totals"]["cumulativeMileage"], 400.0)
