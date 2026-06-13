import { Box, Typography } from "@mui/material";

export function Metric({ label, value }) {
  return (
    <Box className="metric">
      <Typography color="text.secondary">{label}</Typography>
      <Typography className="metric-value">{value}</Typography>
    </Box>
  );
}

