from dataclasses import dataclass

from .maps import interpolate_point


DRIVE_LIMIT_HOURS = 11.0
DUTY_WINDOW_HOURS = 14.0
BREAK_AFTER_DRIVING_HOURS = 8.0
BREAK_HOURS = 0.5
FULL_RESET_HOURS = 10.0
RESTART_HOURS = 34.0
CYCLE_LIMIT_HOURS = 70.0
FUEL_INTERVAL_MILES = 1000.0
FUEL_DURATION_HOURS = 0.5
PICKUP_DURATION_HOURS = 1.0
DROPOFF_DURATION_HOURS = 1.0
PRETRIP_HOURS = 0.25
START_HOUR = 6.0


@dataclass
class ScheduleState:
    clock: float = START_HOUR
    route_miles: float = 0.0
    cycle_used: float = 0.0
    shift_elapsed: float = 0.0
    shift_driving: float = 0.0
    driving_since_break: float = 0.0


def _round(value: float, digits: int = 2) -> float:
    return round(value + 1e-9, digits)


def _display_location(value: str) -> str:
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if len(parts) >= 2:
        return ", ".join(parts[:2])
    return value[:48]


class HosPlanner:
    def __init__(self, route: dict, current_cycle_used_hours: float):
        self.route = route
        self.state = ScheduleState(cycle_used=float(current_cycle_used_hours))
        self.events: list[dict] = []
        self.stops: list[dict] = []
        self.warnings: list[str] = []
        self.next_fuel_mile = FUEL_INTERVAL_MILES
        self.geometry = route.get("geometry", [])
        self.waypoints = route.get("waypoints", [])

    def build(self) -> dict:
        if self.state.cycle_used >= CYCLE_LIMIT_HOURS:
            self._add_restart("Cycle already at 70 hours before dispatch")

        self._add_active(
            "on_duty",
            PRETRIP_HOURS,
            "Pre-trip inspection",
            self._waypoint_location(0),
            "inspection",
        )

        legs = self.route.get("legs") or [
            {
                "distanceMiles": self.route["distanceMiles"],
                "durationHours": self.route["durationHours"],
            }
        ]
        leg_targets = ["pickup", "dropoff"]

        for index, leg in enumerate(legs[:2]):
            self._drive_leg(leg, leg_targets[index])
            if leg_targets[index] == "pickup":
                self._add_active("on_duty", PICKUP_DURATION_HOURS, "Pickup loading paperwork", self._waypoint_location(1), "pickup")
            else:
                self._add_active("on_duty", DROPOFF_DURATION_HOURS, "Dropoff unloading and post-trip", self._waypoint_location(2), "dropoff")

        total_elapsed = self.state.clock - START_HOUR
        return {
            "events": self.events,
            "stops": self.stops,
            "summary": {
                "distanceMiles": _round(self.route["distanceMiles"], 1),
                "drivingHours": _round(self.route["durationHours"], 2),
                "totalElapsedHours": _round(total_elapsed, 2),
                "estimatedDays": max(1, int((self.state.clock // 24) + 1)),
                "cycleHoursUsedAtEnd": _round(min(self.state.cycle_used, CYCLE_LIMIT_HOURS), 2),
                "startedAtHour": START_HOUR,
                "fuelStops": len([stop for stop in self.stops if stop["type"] == "fuel"]),
                "restStops": len([stop for stop in self.stops if stop["type"] in {"break", "reset", "restart"}]),
            },
            "warnings": self.warnings,
        }

    def _drive_leg(self, leg: dict, target_type: str) -> None:
        remaining_hours = float(leg["durationHours"])
        remaining_miles = float(leg["distanceMiles"])
        mph = remaining_miles / remaining_hours if remaining_hours > 0 else 50.0

        while remaining_hours > 0.01:
            self._ensure_can_drive()

            miles_until_fuel = self.next_fuel_mile - self.state.route_miles
            hours_until_fuel = miles_until_fuel / mph if mph > 0 else remaining_hours

            drive_chunk = min(
                remaining_hours,
                DRIVE_LIMIT_HOURS - self.state.shift_driving,
                DUTY_WINDOW_HOURS - self.state.shift_elapsed,
                BREAK_AFTER_DRIVING_HOURS - self.state.driving_since_break,
                max(hours_until_fuel, 0.01),
                CYCLE_LIMIT_HOURS - self.state.cycle_used,
            )

            if drive_chunk <= 0.01:
                self._ensure_can_drive(force=True)
                continue

            miles_chunk = drive_chunk * mph
            label = "Driving to pickup" if target_type == "pickup" else "Driving to dropoff"
            self._add_driving(drive_chunk, miles_chunk, label)
            remaining_hours -= drive_chunk
            remaining_miles -= miles_chunk

            if remaining_hours <= 0.01:
                break
            if self.state.route_miles + 0.01 >= self.next_fuel_mile:
                self._add_fuel_stop()
                self.next_fuel_mile += FUEL_INTERVAL_MILES
            elif self.state.driving_since_break + 0.01 >= BREAK_AFTER_DRIVING_HOURS:
                self._add_break()
            elif self.state.shift_driving + 0.01 >= DRIVE_LIMIT_HOURS or self.state.shift_elapsed + 0.01 >= DUTY_WINDOW_HOURS:
                self._add_reset("10-hour sleeper berth reset")
            elif self.state.cycle_used + 0.01 >= CYCLE_LIMIT_HOURS:
                self._add_restart("70-hour/8-day cycle limit reached")

    def _ensure_can_drive(self, force: bool = False) -> None:
        if self.state.cycle_used >= CYCLE_LIMIT_HOURS - 0.01:
            self._add_restart("70-hour/8-day cycle limit reached")
            return
        if self.state.shift_driving >= DRIVE_LIMIT_HOURS - 0.01:
            self._add_reset("11-hour driving limit reached")
            return
        if self.state.shift_elapsed >= DUTY_WINDOW_HOURS - 0.01:
            self._add_reset("14-hour duty window reached")
            return
        if self.state.driving_since_break >= BREAK_AFTER_DRIVING_HOURS - 0.01:
            self._add_break()
            return
        if force:
            self._add_reset("Hours of service reset")

    def _add_event(self, status: str, duration: float, label: str, location: str, event_type: str, miles: float | None = None) -> dict:
        start = self.state.clock
        end = start + duration
        event = {
            "status": status,
            "type": event_type,
            "label": label,
            "location": location,
            "startHour": _round(start),
            "endHour": _round(end),
            "durationHours": _round(duration),
            "routeMile": _round(self.state.route_miles if miles is None else miles, 1),
        }
        self.events.append(event)
        self.state.clock = end
        return event

    def _add_active(self, status: str, duration: float, label: str, location: str, event_type: str) -> None:
        if self.state.cycle_used + duration > CYCLE_LIMIT_HOURS + 0.01:
            self._add_restart("70-hour/8-day cycle limit would be exceeded")
        event = self._add_event(status, duration, label, location, event_type)
        self.state.shift_elapsed += duration
        self.state.cycle_used += duration
        if event_type in {"pickup", "dropoff", "fuel"}:
            self._add_stop_from_event(event)

    def _add_driving(self, duration: float, miles: float, label: str) -> None:
        start_mile = self.state.route_miles
        location = f"Route mile {_round(self.state.route_miles, 1)}"
        event = self._add_event("driving", duration, label, location, "driving")
        self.state.route_miles += miles
        self.state.shift_elapsed += duration
        self.state.shift_driving += duration
        self.state.driving_since_break += duration
        self.state.cycle_used += duration
        event["startRouteMile"] = _round(start_mile, 1)
        event["endRouteMile"] = _round(self.state.route_miles, 1)
        event["distanceMiles"] = _round(miles, 1)
        event["routeMile"] = _round(self.state.route_miles, 1)

    def _add_break(self) -> None:
        event = self._add_event("off_duty", BREAK_HOURS, "30-minute rest break", f"Route mile {_round(self.state.route_miles, 1)}", "break")
        self.state.shift_elapsed += BREAK_HOURS
        self.state.driving_since_break = 0.0
        self._add_stop_from_event(event)

    def _add_reset(self, label: str) -> None:
        event = self._add_event("sleeper", FULL_RESET_HOURS, label, f"Route mile {_round(self.state.route_miles, 1)}", "reset")
        self.state.shift_elapsed = 0.0
        self.state.shift_driving = 0.0
        self.state.driving_since_break = 0.0
        self._add_stop_from_event(event)

    def _add_restart(self, label: str) -> None:
        event = self._add_event("off_duty", RESTART_HOURS, label, f"Route mile {_round(self.state.route_miles, 1)}", "restart")
        self.state.cycle_used = 0.0
        self.state.shift_elapsed = 0.0
        self.state.shift_driving = 0.0
        self.state.driving_since_break = 0.0
        self.warnings.append(f"{label}; scheduled a 34-hour restart.")
        self._add_stop_from_event(event)

    def _add_fuel_stop(self) -> None:
        self._add_active("on_duty", FUEL_DURATION_HOURS, "Fuel stop", f"Route mile {_round(self.state.route_miles, 1)}", "fuel")

    def _add_stop_from_event(self, event: dict) -> None:
        point = interpolate_point(self.geometry, event["routeMile"])
        self.stops.append(
            {
                "type": event["type"],
                "label": event["label"],
                "location": event["location"],
                "lat": point["lat"],
                "lng": point["lng"],
                "routeMile": event["routeMile"],
                "startHour": event["startHour"],
                "durationHours": event["durationHours"],
            }
        )

    def _waypoint_location(self, index: int) -> str:
        if index < len(self.waypoints):
            return _display_location(self.waypoints[index]["location"])
        return f"Route mile {_round(self.state.route_miles, 1)}"
