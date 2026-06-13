import { Box, Button, Stack, Typography } from "@mui/material";
import { Download } from "lucide-react";

import { downloadDataUrl } from "../lib/formatters.js";

export function LogSheets({ sheets }) {
  if (!sheets?.length) {
    return null;
  }

  return (
    <Box className="log-section">
      <Typography variant="h2">Daily log sheets</Typography>
      <Stack spacing={2}>
        {sheets.map((sheet) => (
          <Box key={sheet.day} className="log-sheet">
            <Box className="log-toolbar">
              <Box>
                <Typography variant="h3">{sheet.title}</Typography>
                <Typography color="text.secondary">
                  Active {sheet.totals.active.toFixed(2)} hrs · Total {sheet.totals.total.toFixed(2)} hrs
                </Typography>
              </Box>
              <Button
                variant="outlined"
                size="small"
                startIcon={<Download size={16} />}
                onClick={() => downloadDataUrl(sheet.image, `spotter-log-day-${sheet.day}.png`)}
              >
                Download
              </Button>
            </Box>
            <img src={sheet.image} alt={`${sheet.title} preview`} />
          </Box>
        ))}
      </Stack>
    </Box>
  );
}

