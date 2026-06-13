from django.test import SimpleTestCase, override_settings

from trips.services.maps import MapClient


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append({"url": url, **kwargs})
        return self.responses.pop(0)


class MapClientFallbackTests(SimpleTestCase):
    @override_settings(PHOTON_BASE_URL="https://photon.test")
    def test_geocode_uses_photon_when_nominatim_rejects_request(self):
        session = FakeSession(
            [
                FakeResponse(403, {}),
                FakeResponse(
                    200,
                    {
                        "features": [
                            {
                                "geometry": {"coordinates": [-87.6244212, 41.8755616]},
                                "properties": {
                                    "name": "Chicago",
                                    "city": "Chicago",
                                    "state": "Illinois",
                                    "country": "United States",
                                },
                            }
                        ]
                    },
                ),
            ]
        )

        point = MapClient(session=session).geocode("Current", "Chicago, Illinois, USA")

        self.assertEqual(point.label, "Current")
        self.assertAlmostEqual(point.lat, 41.8755616)
        self.assertAlmostEqual(point.lng, -87.6244212)
        self.assertEqual(point.display_name, "Chicago, Illinois, United States")
        self.assertIn("photon.test/api/", session.calls[1]["url"])
        self.assertEqual(session.calls[1]["params"]["osm_tag"], "place:city")

    @override_settings(PHOTON_BASE_URL="https://photon.test")
    def test_reverse_geocode_uses_photon_when_nominatim_rejects_request(self):
        session = FakeSession(
            [
                FakeResponse(403, {}),
                FakeResponse(
                    200,
                    {
                        "features": [
                            {
                                "geometry": {"coordinates": [-87.629635, 41.8780428]},
                                "properties": {
                                    "name": "Intelligentsia Coffee",
                                    "city": "Chicago",
                                    "state": "IL",
                                    "country": "United States",
                                },
                            }
                        ]
                    },
                ),
            ]
        )

        location = MapClient(session=session).reverse_geocode(41.8781, -87.6298)

        self.assertEqual(location["location"], "Intelligentsia Coffee, Chicago, IL, United States")
        self.assertEqual(location["shortLocation"], "Chicago, IL")
        self.assertIn("photon.test/reverse", session.calls[1]["url"])
