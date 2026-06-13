const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Thin API helpers keep fetch/error handling out of the UI components.
export async function planTrip(payload) {
  const response = await fetch(`${API_BASE_URL}/api/trips/plan/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || "Unable to plan the trip. Check the locations and try again.";
    throw new Error(detail);
  }
  return data;
}

export async function reverseGeocode({ lat, lng }) {
  const params = new URLSearchParams({ lat: String(lat), lng: String(lng) });
  const response = await fetch(`${API_BASE_URL}/api/trips/reverse-geocode/?${params.toString()}`);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || "Unable to identify your current location.";
    throw new Error(detail);
  }
  return data;
}
