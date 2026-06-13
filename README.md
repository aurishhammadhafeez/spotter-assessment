# Spotter HOS Trip Planner

A full-stack Django + React assessment project for planning property-carrying truck trips, showing route stops, and generating ELD-style daily log sheets.

## Features

- Trip inputs for current location, pickup location, dropoff location, and current cycle hours
- Browser geolocation support for the current location
- Nominatim geocoding and OSRM routing
- Leaflet route map with pickup, dropoff, fuel, rest, and reset markers
- Hours of Service planner for property-carrying drivers
- Generated high-resolution paper-style daily log sheets
- Multiple log sheets for multi-day trips
- Downloadable log PNGs
- Backend and frontend tests

## Stack

- Backend: Django, Django REST Framework, Pillow, Requests
- Frontend: React, Vite, Material UI, Leaflet
- Maps: Nominatim geocoding with Photon fallback, OSRM routing, OpenStreetMap tiles

## Project Structure

```text
backend/   Django API, HOS planner, map service, log renderer, tests
frontend/  React UI, route map, timeline, log previews
docs/      Reviewer notes and logbook reference notes
```

## Local Setup

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Tests

Backend:

```bash
cd backend
source .venv/bin/activate
python manage.py test
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

## Deployment

Backend options:

- Render: use `render.yaml`, then set `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `MAP_USER_AGENT`.
- Railway: deploy the `backend/` folder and use the `Procfile` start command.

Frontend:

- Deploy `frontend/` to Vercel.
- Set `VITE_API_BASE_URL` to the hosted backend URL.
- Rebuild after setting the environment variable.

Recommended backend host: Render. Render currently offers free web services suitable for assessment/demo apps, with cold starts after inactivity. Railway is very smooth, but its current free option is closer to a trial/credit model and may require a paid Hobby plan later.

## API

`POST /api/trips/plan/`

```json
{
  "currentLocation": "Dallas, TX",
  "pickupLocation": "Austin, TX",
  "dropoffLocation": "Denver, CO",
  "currentCycleUsedHours": 12
}
```

The response includes route geometry, stop markers, HOS events, summary metrics, warnings, and generated log sheet images as data URLs.

`GET /api/trips/reverse-geocode/?lat=32.7767&lng=-96.797`

Returns a readable address for browser geolocation.

## Assessment Assumptions

- Property-carrying driver
- 70-hour/8-day cycle
- No adverse driving conditions
- 11-hour driving limit, 14-hour driving window
- 30-minute break after 8 cumulative driving hours
- 10-hour reset between driving shifts
- 34-hour restart when cycle hours are exhausted
- Fuel stop every 1,000 miles
- 1 hour for pickup and 1 hour for dropoff

This is a practical assessment implementation, not a certified ELD or legal compliance product.
