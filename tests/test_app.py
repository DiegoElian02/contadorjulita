"""Exercise the city switch and departure state through Streamlit's runner."""

import json
import re
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from journey import CITIES, NEXT_MEETING


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class AppIntegrationTests(unittest.TestCase):
    def test_city_switch_updates_country_pin_and_photo_album(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        previous_photos = None
        saltillo_count = sum(
            path.is_file() and bool(re.fullmatch(r"photo\d+\.(?:jpg|jpeg|png|webp)", path.name, re.IGNORECASE))
            for path in (APP_PATH.parent / "images" / "Saltillo").iterdir()
        )
        for city_key, expected_count in (("Praga", 11), ("Paris", 10), ("Monterrey", 10), ("Saltillo", saltillo_count)):
            with self.subTest(city=city_key):
                app.radio[0].set_value(city_key).run()
                self.assertEqual(len(app.exception), 0)
                city = CITIES[city_key]
                deck = json.loads(app.get("deck_gl_json_chart")[0].proto.json)
                layers = {layer["id"]: layer for layer in deck["layers"]}
                self.assertEqual(
                    layers["selected-country"]["data"]["properties"]["name"],
                    city["country"],
                )
                self.assertEqual(
                    layers["selected-city-pin"]["data"][0]["position"],
                    [city["lon"], city["lat"]],
                )
                self.assertEqual(deck["initialViewState"]["latitude"], city["lat"])
                self.assertEqual(deck["initialViewState"]["longitude"], city["lon"])
                if city_key == "Saltillo" and expected_count == 0:
                    self.assertIn("Aún no hay fotos en este álbum.", [element.value for element in app.caption])
                images = [image for element in app.get("image") for image in element.proto.imgs]
                self.assertEqual(len(images), expected_count)
                self.assertTrue(all(image.caption.endswith(f"/ {city['label']}") for image in images))
                media_urls = {image.url for image in images}
                if previous_photos is not None:
                    self.assertTrue(media_urls.isdisjoint(previous_photos))
                previous_photos = media_urls

    def test_departure_day_renders_zero_countdown(self):
        class DepartureDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                target = NEXT_MEETING
                return target.astimezone(tz) if tz is not None else target.replace(tzinfo=None)

        with patch("datetime.datetime", DepartureDateTime):
            app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        ticket = next(
            element.proto.body
            for element in app.get("html")
            if 'id="proximo-viaje"' in element.proto.body
        )
        self.assertIn("Llegó el día", ticket)
        self.assertEqual(re.findall(r'class="clock-number">([^<]+)<', ticket), ["00"] * 4)


if __name__ == "__main__":
    unittest.main()
