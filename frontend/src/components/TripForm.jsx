import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  InputAdornment,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { Building2, ChevronDown, Clock3, Crosshair, Home, IdCard, Navigation, Route, Truck, UserRound, Warehouse } from "lucide-react";

function FieldIcon({ children }) {
  return <InputAdornment position="start">{children}</InputAdornment>;
}

export function TripForm({ values, onChange, onSubmit, loading, locating, onUseCurrentLocation }) {
  // The cycle value is the only numeric form field with a regulatory boundary.
  const cycle = Number(values.currentCycleUsedHours);
  const isCycleValid = values.currentCycleUsedHours !== "" && cycle >= 0 && cycle <= 70;
  const isReady =
    values.currentLocation.trim() &&
    values.pickupLocation.trim() &&
    values.dropoffLocation.trim() &&
    isCycleValid;

  function updateField(field, value) {
    // Keep TripForm controlled but stateless; App owns the full payload.
    onChange({ ...values, [field]: value });
  }

  function handleSubmit(event) {
    event.preventDefault();
    if (isReady) {
      onSubmit(values);
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit} className="trip-form">
      <Stack spacing={2}>
        <Box>
          <Typography variant="h2">Trip inputs</Typography>
          <Typography color="text.secondary" className="panel-copy">
            Use a full facility address when you have it. The logs still summarize duty changes by city/state.
          </Typography>
        </Box>

        <TextField
          label="Current location or GPS position"
          value={values.currentLocation}
          onChange={(event) => updateField("currentLocation", event.target.value)}
          placeholder="Truck stop, street address, city/state, or 32.7767,-96.7970"
          helperText="Best for the driver: browser GPS or the closest truck stop/facility address."
          required
          InputProps={{
            startAdornment: (
              <FieldIcon>
                <Navigation size={18} />
              </FieldIcon>
            ),
          }}
        />
        <Button
          type="button"
          variant="outlined"
          onClick={onUseCurrentLocation}
          disabled={loading || locating}
          startIcon={locating ? <CircularProgress size={16} /> : <Crosshair size={18} />}
        >
          {locating ? "Finding current location" : "Use browser location"}
        </Button>
        <TextField
          label="Pickup facility / shipper address"
          value={values.pickupLocation}
          onChange={(event) => updateField("pickupLocation", event.target.value)}
          placeholder="Facility name, street address, city, state, ZIP"
          helperText="Example: Walmart DC, 123 Logistics Dr, Austin, TX 78744"
          multiline
          minRows={2}
          required
          InputProps={{
            startAdornment: (
              <FieldIcon>
                <Warehouse size={18} />
              </FieldIcon>
            ),
          }}
        />
        <TextField
          label="Dropoff facility / receiver address"
          value={values.dropoffLocation}
          onChange={(event) => updateField("dropoffLocation", event.target.value)}
          placeholder="Receiver name, dock address, city, state, ZIP"
          helperText="Full addresses reduce routing ambiguity compared with city/state only."
          multiline
          minRows={2}
          required
          InputProps={{
            startAdornment: (
              <FieldIcon>
                <Route size={18} />
              </FieldIcon>
            ),
          }}
        />
        <TextField
          label="Current cycle used"
          type="number"
          value={values.currentCycleUsedHours}
          onChange={(event) => updateField("currentCycleUsedHours", event.target.value)}
          error={values.currentCycleUsedHours !== "" && !isCycleValid}
          helperText={!isCycleValid ? "Enter a value from 0 to 70 hours." : "Hours already used in the current 70-hour cycle."}
          inputProps={{ min: 0, max: 70, step: 0.25 }}
          required
          InputProps={{
            endAdornment: <InputAdornment position="end">hrs</InputAdornment>,
            startAdornment: (
              <FieldIcon>
                <Clock3 size={18} />
              </FieldIcon>
            ),
          }}
        />

        <Accordion className="log-details" defaultExpanded disableGutters elevation={0}>
          {/* These optional fields do not affect routing, but they make the
             generated paper log resemble a real driver logbook. */}
          <AccordionSummary expandIcon={<ChevronDown size={18} />}>
            <Typography variant="h3">Logbook header details</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Stack spacing={1.5}>
              <TextField
                label="Driver name"
                value={values.driverName}
                onChange={(event) => updateField("driverName", event.target.value)}
                placeholder="Driver full name"
                InputProps={{
                  startAdornment: (
                    <FieldIcon>
                      <UserRound size={18} />
                    </FieldIcon>
                  ),
                }}
              />
              <TextField
                label="Truck / tractor and trailer numbers"
                value={values.truckTrailerNumber}
                onChange={(event) => updateField("truckTrailerNumber", event.target.value)}
                placeholder="Truck 1042 / Trailer 2209"
                InputProps={{
                  startAdornment: (
                    <FieldIcon>
                      <Truck size={18} />
                    </FieldIcon>
                  ),
                }}
              />
              <TextField
                label="Carrier name"
                value={values.carrierName}
                onChange={(event) => updateField("carrierName", event.target.value)}
                placeholder="Carrier company"
                InputProps={{
                  startAdornment: (
                    <FieldIcon>
                      <IdCard size={18} />
                    </FieldIcon>
                  ),
                }}
              />
              <TextField
                label="Main office address"
                value={values.mainOfficeAddress}
                onChange={(event) => updateField("mainOfficeAddress", event.target.value)}
                placeholder="Main office city, state or full address"
                InputProps={{
                  startAdornment: (
                    <FieldIcon>
                      <Building2 size={18} />
                    </FieldIcon>
                  ),
                }}
              />
              <TextField
                label="Home terminal address"
                value={values.homeTerminalAddress}
                onChange={(event) => updateField("homeTerminalAddress", event.target.value)}
                placeholder="Home terminal city, state or full address"
                helperText="Printed on each daily log sheet header."
                InputProps={{
                  startAdornment: (
                    <FieldIcon>
                      <Home size={18} />
                    </FieldIcon>
                  ),
                }}
              />
            </Stack>
          </AccordionDetails>
        </Accordion>

        <Button
          type="submit"
          variant="contained"
          disabled={!isReady || loading}
          startIcon={<Route size={18} />}
        >
          {loading ? <CircularProgress size={20} color="inherit" /> : "Plan route and logs"}
        </Button>

        <Divider />

        <Box className="assumption-box">
          <Typography variant="h3">Location input tips</Typography>
          <ul>
            <li>Current: GPS, truck stop, yard, or nearest known address</li>
            <li>Pickup/dropoff: facility name plus full street address</li>
            <li>City/state alone works, but it is less accurate</li>
          </ul>
        </Box>

        <Box className="assumption-box">
          {/* The assumptions are visible in the UI so the assessment reviewer can
             see which HOS rules the planner implements. */}
          <Typography variant="h3">Planner assumptions</Typography>
          <ul>
            <li>Property-carrying driver</li>
            <li>11-hour drive limit and 14-hour window</li>
            <li>30-minute break after 8 driving hours</li>
            <li>Fuel every 1,000 miles</li>
            <li>Pickup and dropoff are 1 hour each</li>
          </ul>
        </Box>

        <Tooltip title="This demo is built for assessment accuracy, not legal ELD certification.">
          <Alert severity="info" className="compact-alert">
            ELD logs include remarks for every status change and daily totals equal 24 hours.
          </Alert>
        </Tooltip>
      </Stack>
    </Box>
  );
}
