import { useMemo, useState } from "react";
import { Alert, Box, Container, Stack, Typography } from "@mui/material";

import { TripForm } from "./components/TripForm.jsx";
import { RouteMap } from "./components/RouteMap.jsx";
import { ResultsPanel } from "./components/ResultsPanel.jsx";
import { planTrip, reverseGeocode } from "./lib/api.js";

// Demo defaults keep the first screen usable immediately during a reviewer demo.
const initialValues = {
  currentLocation: "Dallas, TX",
  pickupLocation: "Austin, TX",
  dropoffLocation: "Denver, CO",
  currentCycleUsedHours: "12",
  driverName: "Assessment Driver",
  truckTrailerNumber: "Truck 1042 / Trailer 2209",
  carrierName: "Spotter Demo Carrier",
  mainOfficeAddress: "Dallas, TX",
  homeTerminalAddress: "Dallas, TX",
};

export default function App() {
  // App owns the request/result state; presentational components receive the
  // current form values and generated plan through props.
  const [formValues, setFormValues] = useState(initialValues);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [locating, setLocating] = useState(false);

  const mapData = useMemo(() => {
    if (!plan) {
      return null;
    }
    return {
      geometry: plan.route.geometry,
      waypoints: plan.route.waypoints,
      stops: plan.stops,
    };
  }, [plan]);

  async function handleSubmit(values) {
    setLoading(true);
    setError("");
    try {
      // Keep form state string-friendly, but send numeric cycle hours to DRF.
      const response = await planTrip({
        ...values,
        currentCycleUsedHours: Number(values.currentCycleUsedHours),
      });
      setPlan(response);
    } catch (caught) {
      setError(caught.message);
      setPlan(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleUseCurrentLocation() {
    if (!navigator.geolocation) {
      setError("Browser geolocation is not available. Enter a full current address manually.");
      return;
    }

    setLocating(true);
    setError("");
    try {
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          maximumAge: 60000,
          timeout: 12000,
        });
      });
      const { latitude, longitude } = position.coords;
      // Reverse geocoding gives the driver a readable current address while
      // still falling back to raw coordinates if a public geocoder fails.
      const location = await reverseGeocode({ lat: latitude, lng: longitude });
      setFormValues((current) => ({
        ...current,
        currentLocation: location.location || `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`,
      }));
    } catch (caught) {
      const message =
        caught.code === 1
          ? "Location permission was denied. Enter a current address manually."
          : caught.message || "Unable to fetch browser location. Enter a current address manually.";
      setError(message);
    } finally {
      setLocating(false);
    }
  }

  return (
    <Box className="app-shell">
      <Container maxWidth={false} className="app-container">
        <Box component="header" className="app-header">
          <Box>
            <Typography component="h1" variant="h1">
              Spotter HOS Trip Planner
            </Typography>
            <Typography color="text.secondary">
              Route planning, stops, and ELD-style daily logs for the assessment scenario.
            </Typography>
          </Box>
          <Box className="header-badge">70 hrs / 8 days</Box>
        </Box>

        <Box className="workspace-grid">
          <Box component="aside" className="planner-panel">
            <TripForm
              values={formValues}
              onChange={setFormValues}
              onSubmit={handleSubmit}
              loading={loading}
              locating={locating}
              onUseCurrentLocation={handleUseCurrentLocation}
            />
          </Box>

          <Stack spacing={2} className="main-panel">
            {error && <Alert severity="error">{error}</Alert>}
            <RouteMap data={mapData} loading={loading} />
            <ResultsPanel plan={plan} loading={loading} />
          </Stack>
        </Box>
      </Container>
    </Box>
  );
}
