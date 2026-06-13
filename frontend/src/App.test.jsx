import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ThemeProvider } from "@mui/material";

import App from "./App.jsx";
import { theme } from "./theme.js";

vi.mock("react-leaflet", () => ({
  MapContainer: ({ children }) => <div data-testid="map">{children}</div>,
  Marker: ({ children }) => <div>{children}</div>,
  Polyline: () => <div />,
  Popup: ({ children }) => <div>{children}</div>,
  TileLayer: () => <div />,
  useMap: () => ({ fitBounds: vi.fn() }),
}));

function renderApp() {
  return render(
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>,
  );
}

describe("App", () => {
  it("renders the planner as the first screen", () => {
    renderApp();

    expect(screen.getByRole("heading", { name: /spotter hos trip planner/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/current location/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /plan route and logs/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /route map/i })).toBeInTheDocument();
  });
});
