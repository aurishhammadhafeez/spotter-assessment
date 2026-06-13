# YouTube Logbook Reference Notes

Source: Schneider driver instructor walkthrough, https://www.youtube.com/watch?v=whxe41XYXS8

## Four Duty Status Lines

- Line 1: Off Duty - time not working, driving, or performing job duties.
- Line 2: Sleeper Berth - time resting inside the sleeper cab.
- Line 3: Driving - time actively behind the wheel or controlling the commercial motor vehicle.
- Line 4: On Duty (Not Driving) - non-driving work such as inspections, loading, unloading, or fueling.

## Manual Logbook Process

1. Fill out header details before the trip: date, driver number, initials/signature, tractor/trailer numbers, shipper, commodity, and load ID. Use `N/A` for no co-driver.
2. Draw Off Duty across to the start time, then drop vertically to On Duty for pre-trip inspection.
3. Add a remark for each duty-status change with city/state and activity.
4. Use a bracket at the bottom of the grid during stopped/non-movement time.
5. Move to Driving when the vehicle is moving.
6. Move to On Duty (Not Driving) for scale, fueling, loading, unloading, inspection, or similar work.
7. Move to Off Duty for the required 30-minute rest break and note the break in remarks.
8. End the day with post-trip inspection, then move to Off Duty or Sleeper Berth for the 10-hour reset.
9. Total the four duty status rows; the total must equal exactly 24 hours.
10. Add Driving plus On Duty hours and show the active working-hours total.

## Implementation Notes

- Every vertical duty-status transition should have a matching remark.
- Fueling, pickup, dropoff, and inspection should render as Line 4.
- Rest breaks and resets should render as Off Duty or Sleeper Berth.
- Daily totals must sum to 24.0 hours.

