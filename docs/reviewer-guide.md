# Reviewer Guide

## What This App Does

This project plans a property-carrying truck trip and produces:

- Route map with pickup, dropoff, fuel, rest, and reset markers
- Hours of Service timeline
- Generated paper-style daily log sheets
- Multiple daily logs when the trip spans more than one day

## Key Abbreviations

- HOS (Hours of Service)
- ELD (Electronic Logging Device)
- FMCSA (Federal Motor Carrier Safety Administration)
- CMV (Commercial Motor Vehicle)
- API (Application Programming Interface)
- DRF (Django REST Framework)
- UI (User Interface)

## Demo Route

Use the pre-filled example:

- Current location: Dallas, TX
- Pickup location: Austin, TX
- Dropoff location: Denver, CO
- Current cycle used: 12 hours

Expected output:

- Around 1,111 miles
- Two generated daily logs
- Fuel/rest/reset events
- Daily totals equal 24.00 hours

## Notes

The application is designed for assessment-grade trip planning accuracy. It is not certified ELD software or legal advice.

