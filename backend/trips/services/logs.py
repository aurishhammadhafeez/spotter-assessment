import base64
import io
from collections import defaultdict
from datetime import date, timedelta

from PIL import Image, ImageDraw, ImageFont

from .locations import compact_city_state


CANVAS_WIDTH = 1700
CANVAS_HEIGHT = 1100
PAGE_MARGIN = 58
GRID_LEFT = 250
GRID_RIGHT = 1500
GRID_WIDTH = GRID_RIGHT - GRID_LEFT
GRID_TOP = 350
ROW_HEIGHT = 58
GRID_BOTTOM = GRID_TOP + ROW_HEIGHT * 4
TIME_BAND_TOP = 295
TIME_BAND_BOTTOM = GRID_TOP
TOTAL_LEFT = 1512
TOTAL_RIGHT = 1640
INK = "#111827"
MUTED = "#4b5563"
GRID = "#64748b"
LIGHT_GRID = "#d6dce7"
BLUE = "#2563eb"
ORANGE = "#f97316"
ROW_Y = {
    "off_duty": GRID_TOP + ROW_HEIGHT * 0.5,
    "sleeper": GRID_TOP + ROW_HEIGHT * 1.5,
    "driving": GRID_TOP + ROW_HEIGHT * 2.5,
    "on_duty": GRID_TOP + ROW_HEIGHT * 3.5,
}
STATUS_LABELS = {
    "off_duty": "Off duty",
    "sleeper": "Sleeper berth",
    "driving": "Driving",
    "on_duty": "On duty",
}
DEFAULT_LOG_DETAILS = {
    "driverName": "Assessment Driver",
    "truckTrailerNumber": "Truck 1042 / Trailer 2209",
    "carrierName": "Spotter Demo Carrier",
    "mainOfficeAddress": "Dallas, TX",
    "homeTerminalAddress": "Dallas, TX",
}


def _font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _hour_to_x(hour: float) -> float:
    return GRID_LEFT + (hour / 24.0) * GRID_WIDTH


def _draw_line_field(draw: ImageDraw.ImageDraw, label: str, value: str, x: int, y: int, width: int, label_font, value_font) -> None:
    draw.text((x, y), label, fill=MUTED, font=label_font)
    label_width = draw.textbbox((0, 0), label, font=label_font)[2]
    value_offset = max(92, label_width + 14)
    draw.line((x + value_offset, y + 28, x + width, y + 28), fill=INK, width=2)
    draw.text((x + value_offset + 6, y + 2), _clip_text(value, max(12, width // 12)), fill=INK, font=value_font)


def _draw_box_field(draw: ImageDraw.ImageDraw, label: str, value: str, x: int, y: int, width: int, height: int, label_font, value_font) -> None:
    draw.rectangle((x, y, x + width, y + height), outline=INK, width=2)
    draw.text((x + 10, y + 6), label, fill=MUTED, font=label_font)
    draw.text((x + 10, y + 28), _clip_text(value, max(10, width // 12)), fill=INK, font=value_font)


def _draw_template(
    log_date: date,
    from_location: str,
    to_location: str,
    daily_miles: float,
    cumulative_miles: float,
    log_details: dict,
) -> Image.Image:
    image = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), "#ffffff")
    draw = ImageDraw.Draw(image)
    title = _font(42)
    heading = _font(24)
    label = _font(18)
    small = _font(16)
    tiny = _font(13)

    draw.rectangle((24, 24, CANVAS_WIDTH - 24, CANVAS_HEIGHT - 24), outline=INK, width=3)
    draw.text((PAGE_MARGIN, 42), "Driver's Daily Log", fill=INK, font=title)
    draw.text((PAGE_MARGIN, 88), "(24 hours)", fill=MUTED, font=small)

    month_text = f"{log_date.month:02d}"
    day_text = f"{log_date.day:02d}"
    year_text = str(log_date.year)
    draw.text((620, 48), month_text, fill=INK, font=heading)
    draw.text((785, 48), day_text, fill=INK, font=heading)
    draw.text((925, 48), year_text, fill=INK, font=heading)
    draw.line((590, 88, 740, 88), fill=INK, width=2)
    draw.line((760, 88, 880, 88), fill=INK, width=2)
    draw.line((900, 88, 1030, 88), fill=INK, width=2)
    draw.text((642, 94), "month", fill=MUTED, font=tiny)
    draw.text((805, 94), "day", fill=MUTED, font=tiny)
    draw.text((922, 94), "year", fill=MUTED, font=tiny)

    draw.text((1165, 42), "Original - file at home terminal", fill=INK, font=small)
    draw.text((1165, 68), "Duplicate - driver retains possession for 8 days", fill=INK, font=small)

    _draw_line_field(draw, "From:", from_location, PAGE_MARGIN, 135, 690, label, small)
    _draw_line_field(draw, "To:", to_location, 850, 135, 1450 - 850, label, small)
    _draw_box_field(draw, "Total miles driving today", f"{daily_miles:,.1f} mi", PAGE_MARGIN, 215, 260, 54, tiny, small)
    _draw_box_field(draw, "Total mileage today", f"{cumulative_miles:,.1f} mi", 345, 215, 260, 54, tiny, small)
    _draw_line_field(draw, "Driver:", log_details["driverName"], PAGE_MARGIN, 178, 330, label, small)
    _draw_line_field(draw, "Truck/trailer:", log_details["truckTrailerNumber"], 420, 178, 330, label, small)
    _draw_line_field(draw, "Carrier:", log_details["carrierName"], 850, 178, 1450 - 850, label, small)
    _draw_line_field(draw, "Main office:", log_details["mainOfficeAddress"], 850, 220, 1450 - 850, label, small)
    _draw_line_field(draw, "Home terminal:", log_details["homeTerminalAddress"], 850, 262, 1450 - 850, label, small)

    draw.rectangle((GRID_LEFT, TIME_BAND_TOP, GRID_RIGHT, TIME_BAND_BOTTOM), fill=INK)
    draw.rectangle((TOTAL_LEFT, TIME_BAND_TOP, TOTAL_RIGHT, TIME_BAND_BOTTOM), fill=INK)
    draw.text((TOTAL_LEFT + 20, TIME_BAND_TOP + 8), "Total\nhours", fill="#ffffff", font=tiny)

    for row_index in range(5):
        y = GRID_TOP + row_index * ROW_HEIGHT
        draw.line((GRID_LEFT, y, GRID_RIGHT, y), fill=GRID, width=2)
        draw.line((TOTAL_LEFT, y, TOTAL_RIGHT, y), fill=GRID, width=2)

    for index in range(97):
        hour = index / 4
        x = _hour_to_x(hour)
        is_hour = index % 4 == 0
        is_half = index % 2 == 0
        line_color = GRID if is_hour else LIGHT_GRID
        line_width = 2 if is_hour else 1
        draw.line((x, GRID_TOP, x, GRID_BOTTOM), fill=line_color, width=line_width)
        tick_height = 24 if is_hour else 16 if is_half else 10
        draw.line((x, GRID_TOP, x, GRID_TOP + tick_height), fill=line_color, width=line_width)

        if is_hour and index < 96:
            display_hour = int(hour)
            if display_hour == 0:
                text = "Mid-\nnight"
            elif display_hour == 12:
                text = "Noon"
            else:
                shown = display_hour if display_hour < 12 else display_hour - 12
                text = str(shown)
            draw.text((x + 4, TIME_BAND_TOP + 16), text, fill="#ffffff", font=tiny)

    draw.text((GRID_RIGHT - 60, TIME_BAND_TOP + 8), "Mid-\nnight", fill="#ffffff", font=tiny)

    labels = [
        ("1. Off duty", "off_duty"),
        ("2. Sleeper berth", "sleeper"),
        ("3. Driving", "driving"),
        ("4. On duty\n(not driving)", "on_duty"),
    ]
    for text, status in labels:
        draw.text((PAGE_MARGIN, ROW_Y[status] - 17), text, fill=INK, font=small)

    draw.text((PAGE_MARGIN, 610), "Remarks", fill=INK, font=heading)
    draw.line((PAGE_MARGIN, 642, CANVAS_WIDTH - PAGE_MARGIN, 642), fill=INK, width=2)
    draw.text((PAGE_MARGIN, 800), "Shipping documents:", fill=INK, font=small)
    draw.line((PAGE_MARGIN, 842, 500, 842), fill=INK, width=2)
    draw.text((PAGE_MARGIN, 860), "DVL or manifest no.", fill=INK, font=tiny)
    draw.line((PAGE_MARGIN, 902, 500, 902), fill=INK, width=2)
    draw.text((PAGE_MARGIN, 920), "Shipper and commodity", fill=INK, font=tiny)
    draw.text((565, 920), "Enter each location and activity where a duty status changed.", fill=MUTED, font=small)
    draw.line((PAGE_MARGIN, 955, CANVAS_WIDTH - PAGE_MARGIN, 955), fill=INK, width=3)

    draw.text((PAGE_MARGIN, 980), "Recap", fill=INK, font=heading)
    draw.text((PAGE_MARGIN, 1014), "Daily totals must equal 24.00 hours.", fill=MUTED, font=small)
    draw.text((900, 980), "Active hours = Driving + On duty", fill=INK, font=heading)
    draw.text((900, 1014), "Use this as the daily HOS math check.", fill=MUTED, font=small)

    return image


def _clip_text(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: max(0, limit - 3)].rstrip() + "..."


def _remark_location(location: str) -> str:
    compact = _city_state(location)
    return compact.replace("Route mile", "mi")


def _city_state(location: str) -> str:
    return compact_city_state(location)


def _remark_label(label: str) -> str:
    replacements = {
        "30-minute rest break": "30-min break",
        "10-hour sleeper berth reset": "10hr sleeper reset",
        "Pickup loading paperwork": "Pickup paperwork",
        "Dropoff unloading and post-trip": "Dropoff/post-trip",
    }
    return replacements.get(label, label)


def _day_segments(events: list[dict], day_index: int) -> list[dict]:
    day_start = day_index * 24
    day_end = day_start + 24
    clipped = []
    for event in events:
        start = max(event["startHour"], day_start)
        end = min(event["endHour"], day_end)
        if end > start:
            clipped_event = {**event, "start": start - day_start, "end": end - day_start}
            if event["status"] == "driving" and event.get("distanceMiles"):
                event_start = event["startHour"]
                event_end = event["endHour"]
                event_duration = max(event_end - event_start, 0.01)
                start_ratio = (start - event_start) / event_duration
                end_ratio = (end - event_start) / event_duration
                full_distance = event["distanceMiles"]
                start_mile = event.get("startRouteMile", event["routeMile"] - full_distance)
                clipped_event["startRouteMile"] = round(start_mile + full_distance * start_ratio, 1)
                clipped_event["endRouteMile"] = round(start_mile + full_distance * end_ratio, 1)
                clipped_event["distanceMiles"] = round(full_distance * (end_ratio - start_ratio), 1)
            clipped.append(clipped_event)

    clipped.sort(key=lambda item: item["start"])
    normalized = []
    cursor = 0.0
    for event in clipped:
        if event["start"] > cursor:
            normalized.append(
                {
                    "status": "off_duty",
                    "type": "gap",
                    "label": "Off duty",
                    "location": "Not driving",
                    "start": cursor,
                    "end": event["start"],
                    "durationHours": event["start"] - cursor,
                }
            )
        normalized.append(event)
        cursor = max(cursor, event["end"])

    if cursor < 24:
        normalized.append(
            {
                "status": "off_duty",
                "type": "gap",
                "label": "Off duty",
                "location": "Not driving",
                "start": cursor,
                "end": 24,
                "durationHours": 24 - cursor,
            }
        )
    return normalized


def _totals(segments: list[dict]) -> dict:
    totals = defaultdict(float)
    for segment in segments:
        totals[segment["status"]] += segment["end"] - segment["start"]
    return {status: round(value, 2) for status, value in totals.items()}


def _mileage_totals(segments: list[dict]) -> tuple[float, float]:
    driving_segments = [segment for segment in segments if segment["status"] == "driving"]
    if not driving_segments:
        return 0.0, 0.0
    first_mile = min(segment.get("startRouteMile", 0) for segment in driving_segments)
    last_mile = max(segment.get("endRouteMile", 0) for segment in driving_segments)
    daily_miles = round(last_mile - first_mile, 1)
    cumulative_miles = round(max((segment.get("endRouteMile", 0) for segment in driving_segments), default=0), 1)
    return daily_miles, cumulative_miles


def _log_details(overrides: dict | None) -> dict:
    details = DEFAULT_LOG_DETAILS.copy()
    for key, value in (overrides or {}).items():
        if value:
            details[key] = value
    return details


def render_log_sheets(
    events: list[dict],
    route: dict,
    start_date: date | None = None,
    log_details: dict | None = None,
) -> list[dict]:
    if not events:
        return []

    last_hour = max(event["endHour"] for event in events)
    day_count = max(1, int((last_hour - 0.01) // 24) + 1)
    sheets = []
    base_date = start_date or date.today()
    from_location = route["waypoints"][0]["location"] if route.get("waypoints") else "Current"
    to_location = route["waypoints"][-1]["location"] if route.get("waypoints") else "Dropoff"
    header_details = _log_details(log_details)

    for day_index in range(day_count):
        log_date = base_date + timedelta(days=day_index)
        segments = _day_segments(events, day_index)
        totals = _totals(segments)
        daily_miles, cumulative_miles = _mileage_totals(segments)
        active_total = round(totals.get("driving", 0) + totals.get("on_duty", 0), 2)
        image = _draw_template(log_date, from_location, to_location, daily_miles, cumulative_miles, header_details)
        draw = ImageDraw.Draw(image)
        remarks_font = _font(18)
        totals_font = _font(22)
        bold = _font(24)

        prev_y = None
        prev_x = None
        for segment in segments:
            status = segment["status"]
            y = ROW_Y[status]
            start_x = _hour_to_x(segment["start"])
            end_x = _hour_to_x(segment["end"])
            if prev_y is not None and abs(prev_x - start_x) < 2 and prev_y != y:
                draw.line((start_x, prev_y, start_x, y), fill=BLUE, width=7)
            draw.line((start_x, y, end_x, y), fill=BLUE, width=7)
            if segment["type"] in {"pickup", "dropoff", "fuel", "inspection"}:
                bracket_y = GRID_BOTTOM + 24
                draw.line((start_x, bracket_y, end_x, bracket_y), fill=ORANGE, width=5)
                draw.line((start_x, bracket_y, start_x, bracket_y - 16), fill=ORANGE, width=5)
                draw.line((end_x, bracket_y, end_x, bracket_y - 16), fill=ORANGE, width=5)
            prev_y = y
            prev_x = end_x

        remark_count = 0
        for segment in segments:
            if segment["type"] == "gap" or remark_count >= 12:
                continue
            hour = int(segment["start"])
            minute = int(round((segment["start"] - hour) * 60))
            text = f"{hour:02d}:{minute:02d} {_remark_location(segment['location'])} - {_remark_label(segment['label'])}"
            column = remark_count // 6
            row = remark_count % 6
            x = PAGE_MARGIN if column == 0 else 870
            y = 660 + row * 25
            draw.text((x, y), _clip_text(text, 68), fill=INK, font=remarks_font)
            remark_count += 1

        total_positions = {
            "off_duty": ROW_Y["off_duty"],
            "sleeper": ROW_Y["sleeper"],
            "driving": ROW_Y["driving"],
            "on_duty": ROW_Y["on_duty"],
        }
        for status, y in total_positions.items():
            draw.text((TOTAL_LEFT + 25, y - 14), f"{totals.get(status, 0):.2f}", fill=INK, font=totals_font)

        draw.rectangle((1220, 792, 1605, 890), fill="#ffffff", outline=INK, width=3)
        draw.text((1242, 812), f"Active: {active_total:.2f} hrs", fill=INK, font=bold)
        draw.text((1242, 850), "Status totals: 24.00 hrs", fill=INK, font=bold)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        data = base64.b64encode(buffer.getvalue()).decode("ascii")
        sheets.append(
            {
                "day": day_index + 1,
                "title": f"Driver Daily Log - Day {day_index + 1}",
                "date": {
                    "iso": log_date.isoformat(),
                    "month": log_date.month,
                    "day": log_date.day,
                    "year": log_date.year,
                },
                "totals": {
                    "offDuty": totals.get("off_duty", 0),
                    "sleeper": totals.get("sleeper", 0),
                    "driving": totals.get("driving", 0),
                    "onDuty": totals.get("on_duty", 0),
                    "total": round(sum(totals.values()), 2),
                    "active": active_total,
                    "milesDrivingToday": daily_miles,
                    "cumulativeMileage": cumulative_miles,
                },
                "image": f"data:image/png;base64,{data}",
            }
        )

    return sheets
