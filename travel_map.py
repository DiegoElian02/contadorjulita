"""A self-contained atlas drawn from the repository's country outlines.

There is intentionally no tile provider: the map works on Streamlit Cloud with
the bundled GeoJSON alone. Country geometry is simplified once, in memory, to
keep the atlas responsive on phones without changing the original asset.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pydeck as pdk

from journey import CITIES


_GEOJSON_PATH = Path(__file__).resolve().parent / "images" / "countries.geojson"
_CITY_ZOOMS = {"Monterrey": 2.8, "Praga": 4.5, "Paris": 3.7}

_OCEAN = [232, 237, 229, 255]
_LAND = [239, 232, 216, 255]
_BORDER = [192, 190, 172, 255]
_ACCENT = [183, 92, 66, 255]
_INK = [60, 65, 52, 255]


class _AtlasDeck(pdk.Deck):
    """Use Pydeck's public serialization, with compact JSON for transport."""

    def to_json(self):
        return json.dumps(json.loads(super().to_json()), separators=(",", ":"))


def _simplify_ring(points: list, tolerance: float = 0.025) -> list:
    """Simplify a closed ring with iterative Ramer–Douglas–Peucker.

    The small tolerance preserves city/country context at the supported zooms.
    Tiny islands keep their original ring when simplification would collapse it.
    """
    if len(points) <= 4:
        return points

    keep = {0, len(points) - 1}
    sections = [(0, len(points) - 1)]
    tolerance_squared = tolerance * tolerance
    while sections:
        first, last = sections.pop()
        ax, ay = points[first][:2]
        bx, by = points[last][:2]
        dx, dy = bx - ax, by - ay
        length_squared = dx * dx + dy * dy
        farthest_distance = tolerance_squared
        farthest_index = None
        for index in range(first + 1, last):
            px, py = points[index][:2]
            fraction = (
                max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / length_squared))
                if length_squared
                else 0
            )
            distance = (px - ax - fraction * dx) ** 2 + (py - ay - fraction * dy) ** 2
            if distance > farthest_distance:
                farthest_distance, farthest_index = distance, index
        if farthest_index is not None:
            keep.add(farthest_index)
            sections.extend([(first, farthest_index), (farthest_index, last)])

    simplified = [points[index] for index in sorted(keep)]
    return simplified if len(simplified) >= 4 else points


@lru_cache(maxsize=1)
def _countries() -> dict:
    with _GEOJSON_PATH.open(encoding="utf-8") as source:
        original = json.load(source)

    features = []
    for feature in original["features"]:
        geometry = feature["geometry"]
        if geometry["type"] == "Polygon":
            coordinates = [_simplify_ring(ring) for ring in geometry["coordinates"]]
        elif geometry["type"] == "MultiPolygon":
            coordinates = [
                [_simplify_ring(ring) for ring in polygon]
                for polygon in geometry["coordinates"]
            ]
        else:
            coordinates = geometry["coordinates"]
        features.append(
            {
                "type": "Feature",
                "properties": {"name": feature["properties"]["name"]},
                "geometry": {"type": geometry["type"], "coordinates": coordinates},
            }
        )
    return {"type": "FeatureCollection", "features": features}


def build_map(city_key: str, city_data: dict) -> pdk.Deck:
    """Build the interactive atlas, focused on the selected city and country.

    ``city_data`` accepts ``label``, ``country``, ``country_geojson``, ``lat`` and
    ``lon``. ``country_geojson`` must match the asset's English country name.
    """
    selected = {**CITIES.get(city_key, {}), **city_data}
    country_name = selected.get("country_geojson", selected.get("country"))
    city_name = selected.get("label", city_key)
    display_country = selected.get("country", country_name)
    latitude, longitude = selected["lat"], selected["lon"]
    countries = _countries()
    country = next(
        (feature for feature in countries["features"] if feature["properties"]["name"] == country_name),
        None,
    )

    # This single flat polygon supplies the ocean color without a tile service.
    # Keeping longitudes away from the Mercator seam avoids wraparound artifacts.
    ocean = {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[-179.99, -85], [179.99, -85], [179.99, 85], [-179.99, 85], [-179.99, -85]]],
        },
    }
    layers = [
        pdk.Layer(
            "GeoJsonLayer",
            id="atlas-ocean",
            data=ocean,
            filled=True,
            stroked=False,
            get_fill_color=_OCEAN,
            pickable=False,
            parameters={"depthTest": False},
        ),
        pdk.Layer(
            "GeoJsonLayer",
            id="atlas-countries",
            data=countries,
            filled=True,
            stroked=True,
            get_fill_color=_LAND,
            get_line_color=_BORDER,
            line_width_min_pixels=0.7,
            pickable=False,
        ),
    ]

    if country:
        highlighted = {
            **country,
            "properties": {"name": str(display_country), "detail": f"Recuerdos de {city_name}"},
        }
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                id="selected-country",
                data=highlighted,
                filled=True,
                stroked=True,
                get_fill_color=[206, 151, 125, 230],
                get_line_color=_ACCENT,
                line_width_min_pixels=1.5,
                pickable=True,
            )
        )

    points = [
        {
            "name": metadata["label"],
            "detail": metadata["country"],
            "position": [metadata["lon"], metadata["lat"]],
        }
        for key, metadata in CITIES.items()
        if key != city_key
    ]
    selected_point = [{"name": str(city_name), "detail": str(display_country), "position": [longitude, latitude]}]
    layers.extend(
        [
            pdk.Layer(
                "ScatterplotLayer",
                id="other-cities",
                data=points,
                get_position="position",
                get_fill_color=[103, 116, 90, 255],
                get_line_color=[255, 251, 243, 255],
                get_radius=5,
                radius_units="'pixels'",
                stroked=True,
                line_width_min_pixels=2,
                pickable=True,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                id="selected-city-halo",
                data=selected_point,
                get_position="position",
                get_fill_color=[183, 92, 66, 38],
                get_line_color=[183, 92, 66, 115],
                get_radius=19,
                radius_units="'pixels'",
                stroked=True,
                line_width_min_pixels=1,
                pickable=False,
            ),
            pdk.Layer(
                "ScatterplotLayer",
                id="selected-city-pin",
                data=selected_point,
                get_position="position",
                get_fill_color=_ACCENT,
                get_line_color=[255, 251, 243, 255],
                get_radius=7,
                radius_units="'pixels'",
                stroked=True,
                line_width_min_pixels=2.5,
                pickable=True,
            ),
            pdk.Layer(
                "TextLayer",
                id="city-labels",
                data=points,
                get_position="position",
                get_text="name",
                get_size=13,
                get_color=_INK,
                get_pixel_offset=[0, -18],
                get_text_anchor="'middle'",
                get_alignment_baseline="'bottom'",
                font_family="'Arial, sans-serif'",
                font_weight=500,
                character_set="'auto'",
                billboard=True,
                pickable=False,
            ),
            pdk.Layer(
                "TextLayer",
                id="selected-city-label",
                data=selected_point,
                get_position="position",
                get_text="name",
                get_size=17,
                get_color=_INK,
                get_pixel_offset=[0, -27],
                get_text_anchor="'middle'",
                get_alignment_baseline="'bottom'",
                font_family="'Arial, sans-serif'",
                font_weight=600,
                character_set="'auto'",
                billboard=True,
                pickable=False,
            ),
        ]
    )

    return _AtlasDeck(
        layers=layers,
        map_provider=None,
        # Keep pydeck's default no-provider sentinel. Explicit map_style=None
        # asks Streamlit to choose its theme's Carto basemap and fetch tiles.
        initial_view_state=pdk.ViewState(
            latitude=latitude,
            longitude=longitude,
            zoom=selected.get("zoom", _CITY_ZOOMS.get(city_key, 4)),
            pitch=0,
            bearing=0,
            min_zoom=1.2,
            max_zoom=7,
        ),
        views=[pdk.View(type="MapView", controller=True)],
        height=390,
        tooltip={
            "html": "<b>{name}</b><br/><span>{detail}</span>",
            "style": {
                "backgroundColor": "#fffbf3",
                "color": "#3c4134",
                "fontFamily": "Arial, sans-serif",
                "fontSize": "12px",
                "padding": "10px 14px",
                "borderRadius": "10px",
                "boxShadow": "0 4px 18px rgba(60,65,52,.12)",
            },
        },
        parameters={"clearColor": [value / 255 for value in _OCEAN]},
    )
