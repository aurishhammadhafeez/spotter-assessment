import L from "leaflet";
import { Box, CircularProgress, Typography } from "@mui/material";
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from "react-leaflet";

const fallbackCenter = [39.8283, -98.5795];

function markerIcon(type) {
  // Leaflet div icons let us style marker types with CSS instead of bundling
  // separate image assets.
  const classes = {
    current: "marker marker-current",
    pickup: "marker marker-pickup",
    dropoff: "marker marker-dropoff",
    fuel: "marker marker-fuel",
    break: "marker marker-break",
    reset: "marker marker-reset",
    restart: "marker marker-reset",
  };
  return L.divIcon({
    className: classes[type] || "marker marker-stop",
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });
}

function FitBounds({ data }) {
  const map = useMap();
  if (data?.geometry?.length) {
    // Fit the route after each successful plan so long trips remain visible.
    const bounds = L.latLngBounds(data.geometry.map((point) => [point.lat, point.lng]));
    map.fitBounds(bounds.pad(0.18), { animate: false });
  }
  return null;
}

export function RouteMap({ data, loading }) {
  // Backend geometry is already normalized to { lat, lng }; Leaflet needs
  // [lat, lng] tuples for polylines and markers.
  const line = data?.geometry?.map((point) => [point.lat, point.lng]) || [];
  const center = line[0] || fallbackCenter;
  const waypoints = data?.waypoints || [];
  const stops = data?.stops || [];

  return (
    <Box className="map-shell">
      <Box className="map-header">
        <Box>
          <Typography variant="h2">Route map</Typography>
          <Typography color="text.secondary">Pickup, dropoff, fuel, rest, and reset markers.</Typography>
        </Box>
        {loading && (
          <Box className="map-loading">
            <CircularProgress size={18} />
            <span>Routing</span>
          </Box>
        )}
      </Box>

      <Box className="map-frame">
        <MapContainer center={center} zoom={5} scrollWheelZoom className="map">
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {line.length > 0 && <Polyline positions={line} pathOptions={{ color: "#1d4ed8", weight: 5 }} />}
          {waypoints.map((point) => (
            <Marker
              key={`${point.type}-${point.lat}-${point.lng}`}
              position={[point.lat, point.lng]}
              icon={markerIcon(point.type)}
            >
              <Popup>
                <strong>{point.label}</strong>
                <br />
                {point.location}
              </Popup>
            </Marker>
          ))}
          {stops.map((stop, index) => (
            <Marker
              key={`${stop.type}-${index}-${stop.routeMile}`}
              position={[stop.lat, stop.lng]}
              icon={markerIcon(stop.type)}
            >
              <Popup>
                <strong>{stop.label}</strong>
                <br />
                {stop.location}
                <br />
                Route mile {stop.routeMile}
              </Popup>
            </Marker>
          ))}
          <FitBounds data={data} />
        </MapContainer>

        {!data && !loading && (
          <Box className="map-empty">
            <Typography variant="h3">Ready for dispatch</Typography>
            <Typography color="text.secondary">Submit the trip details to draw the route and stop plan.</Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
