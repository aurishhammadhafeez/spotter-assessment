"""Shared location helpers for keeping UI and logbook text readable."""

US_STATE_ABBREVIATIONS = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def compact_city_state(location: str) -> str:
    """Convert verbose geocoder names into logbook-friendly city/state text.

    Nominatim and Photon can return long names such as
    "Chicago Public Schools Headquarters, Chicago, IL, United States". The paper
    log only needs the city/state remark, so this keeps the generated log clean.
    """

    parts = [part.strip() for part in location.split(",") if part.strip()]
    while parts and parts[-1] in {"United States", "USA", "US"}:
        parts.pop()

    if len(parts) < 2:
        return location[:48]

    state = parts[-1]
    normalized_state = US_STATE_ABBREVIATIONS.get(state, state)
    if len(normalized_state) != 2:
        return ", ".join(parts[:2])

    previous = parts[-2]
    # Some Nominatim results include county/township between city and state.
    # In that shape, the actual city is usually the first part.
    previous_is_region = any(token in previous.lower() for token in ["county", "township", "municipality"])
    city = parts[0] if previous_is_region else previous
    return f"{city}, {normalized_state}"
