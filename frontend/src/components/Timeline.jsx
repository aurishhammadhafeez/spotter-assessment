import { Box, Chip, Typography } from "@mui/material";

import { formatClock, formatHours } from "../lib/formatters.js";

const statusLabel = {
  off_duty: "Off duty",
  sleeper: "Sleeper",
  driving: "Driving",
  on_duty: "On duty",
};

export function Timeline({ events }) {
  if (!events?.length) {
    return null;
  }

  return (
    <Box className="timeline-section">
      <Typography variant="h2">Duty timeline</Typography>
      <Box className="timeline-list">
        {events.map((event, index) => (
          <Box key={`${event.startHour}-${event.type}-${index}`} className="timeline-row">
            <Box className={`timeline-dot status-${event.status}`} />
            <Box className="timeline-content">
              <Box className="timeline-main">
                <Typography className="timeline-title">{event.label}</Typography>
                <Chip size="small" label={statusLabel[event.status]} className={`status-chip status-${event.status}`} />
              </Box>
              <Typography color="text.secondary">
                {formatClock(event.startHour)} to {formatClock(event.endHour)} · {formatHours(event.durationHours)}
              </Typography>
              <Typography color="text.secondary">{event.location}</Typography>
            </Box>
          </Box>
        ))}
      </Box>
    </Box>
  );
}

