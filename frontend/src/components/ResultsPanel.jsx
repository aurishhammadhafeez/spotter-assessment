import { Alert, Box, Chip, CircularProgress, Stack, Typography } from "@mui/material";
import { Clock3, Fuel, MapPinned, NotebookTabs, Route } from "lucide-react";

import { formatHours } from "../lib/formatters.js";
import { LogSheets } from "./LogSheets.jsx";
import { Metric } from "./Metric.jsx";
import { Timeline } from "./Timeline.jsx";

export function ResultsPanel({ plan, loading }) {
  // Keep the empty/loading/success states explicit so the first screen works
  // before any API request has completed.
  if (loading && !plan) {
    return (
      <Box className="results-shell loading-results">
        <CircularProgress />
        <Typography>Building the route, HOS timeline, and paper logs.</Typography>
      </Box>
    );
  }

  if (!plan) {
    return (
      <Box className="results-shell empty-results">
        <Box>
          <Typography variant="h2">Outputs</Typography>
          <Typography color="text.secondary">
            The completed plan will show route metrics, stops, a duty timeline, compliance notes, and daily log sheets.
          </Typography>
        </Box>
        <Box className="output-preview-grid">
          <Chip icon={<MapPinned size={16} />} label="Route map" />
          <Chip icon={<Fuel size={16} />} label="Fuel and rests" />
          <Chip icon={<NotebookTabs size={16} />} label="Daily logs" />
        </Box>
      </Box>
    );
  }

  const { summary } = plan;

  return (
    <Stack spacing={2}>
      <Box className="results-shell">
        <Box className="results-heading">
          <Box>
            <Typography variant="h2">Trip summary</Typography>
            <Typography color="text.secondary">Planned under property-carrying HOS assumptions.</Typography>
          </Box>
          <Chip label={`${summary.logSheets} log sheet${summary.logSheets === 1 ? "" : "s"}`} />
        </Box>

        <Box className="metrics-grid">
          <Metric label="Distance" value={`${summary.distanceMiles.toLocaleString()} mi`} />
          <Metric label="Drive time" value={formatHours(summary.drivingHours)} />
          <Metric label="Elapsed" value={formatHours(summary.totalElapsedHours)} />
          <Metric label="Cycle at end" value={`${summary.cycleHoursUsedAtEnd.toFixed(2)} hrs`} />
          <Metric label="Fuel stops" value={summary.fuelStops} />
          <Metric label="Rest stops" value={summary.restStops} />
        </Box>

        <Box className="attribution-row">
          <Route size={16} />
          <span>Routing by OSRM, geocoding by Nominatim with Photon fallback, map tiles by OpenStreetMap contributors.</span>
        </Box>
      </Box>

      {plan.warnings?.map((warning) => (
        // Warnings are produced by the HOS planner, for example when a restart
        // is needed because the 70-hour cycle is exhausted.
        <Alert key={warning} severity="warning">
          {warning}
        </Alert>
      ))}

      <Box className="results-shell">
        <Typography variant="h2">Stops</Typography>
        <Box className="stop-grid">
          {plan.stops.length === 0 ? (
            <Typography color="text.secondary">No intermediate stops required.</Typography>
          ) : (
            plan.stops.map((stop, index) => (
              <Box key={`${stop.type}-${index}-${stop.routeMile}`} className="stop-item">
                <Box className={`stop-icon stop-${stop.type}`}>
                  {stop.type === "fuel" ? <Fuel size={16} /> : <Clock3 size={16} />}
                </Box>
                <Box>
                  <Typography className="stop-title">{stop.label}</Typography>
                  <Typography color="text.secondary">
                    Route mile {stop.routeMile} · {formatHours(stop.durationHours)}
                  </Typography>
                </Box>
              </Box>
            ))
          )}
        </Box>
      </Box>

      <Box className="results-shell">
        <Timeline events={plan.events} />
      </Box>

      <LogSheets sheets={plan.logSheets} />
    </Stack>
  );
}
