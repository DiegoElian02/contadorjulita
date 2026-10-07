import json
import unittest

import pydeck as pdk

from journey import CITIES
from travel_map import _countries, build_map


class TravelMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maps = {
            key: json.loads(build_map(key, {}).to_json())
            for key in CITIES
        }

    def test_selection_keeps_camera_marker_and_country_in_sync(self):
        countries = {
            feature["properties"]["name"]: feature
            for feature in _countries()["features"]
        }
        for key, city in CITIES.items():
            with self.subTest(city=key):
                deck = self.maps[key]
                layers = {layer["id"]: layer for layer in deck["layers"]}
                camera = deck["initialViewState"]
                point = layers["selected-city-pin"]["data"][0]
                country = layers["selected-country"]["data"]
                self.assertEqual([camera["longitude"], camera["latitude"]], [city["lon"], city["lat"]])
                self.assertEqual(point["position"], [city["lon"], city["lat"]])
                self.assertEqual(point["name"], city["label"])
                self.assertEqual(country["properties"]["name"], city["country"])
                self.assertEqual(country["geometry"], countries[city["country_geojson"]]["geometry"])

    def test_all_city_markers_use_shared_journey_coordinates(self):
        expected = {(city["lon"], city["lat"]) for city in CITIES.values()}
        for key, deck in self.maps.items():
            with self.subTest(city=key):
                layers = {layer["id"]: layer for layer in deck["layers"]}
                markers = layers["selected-city-pin"]["data"] + layers["other-cities"]["data"]
                self.assertEqual({tuple(marker["position"]) for marker in markers}, expected)

    def test_map_uses_bundled_geometry_without_a_basemap(self):
        for key, deck in self.maps.items():
            with self.subTest(city=key):
                self.assertIsNone(deck.get("mapProvider"))
                # Omitting mapStyle or setting it to None causes Streamlit to
                # fetch its default Carto style. Pydeck's sentinel suppresses it.
                self.assertEqual(deck["mapStyle"], "__MAP_STYLE__")
                for layer in deck["layers"]:
                    self.assertIsInstance(layer["data"], (dict, list))

    def test_compact_transport_keeps_the_complete_pydeck_structure(self):
        deck = build_map("Monterrey", CITIES["Monterrey"])
        compact = deck.to_json()
        self.assertNotIn("\n", compact)
        self.assertLess(len(compact.encode("utf-8")), 4_000_000)
        self.assertEqual(json.loads(compact), json.loads(pdk.Deck.to_json(deck)))


if __name__ == "__main__":
    unittest.main()
