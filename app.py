"""Las Machuqui-Aventuras: a small travel journal, built for Streamlit Cloud."""

import base64
from datetime import datetime
from html import escape
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
import streamlit as st

from journey import (
    CITIES, MILESTONES, NEXT_MEETING, TIMEZONE,
    countdown_parts, formatted_coordinates, route_position,
)
from travel_map import build_map

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
MONTHS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
_PLANE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#b9563e" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M17.8 8.2 20 6a2.83 2.83 0 0 0-4-4l-2.2 2.2-3-1-1.6 1.6 2 2-3.6 3.6-5-1-1.6 1.6 5 3-3.8 3.8a1 1 0 0 0 .7 1.7h1.4l4-4 3 5 1.6-1.6-1-5 3.6-3.6 2 2 1.6-1.6-1-3Z"/></svg>'
_ROUTE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 180 90" fill="none"><path d="M5 65C50 10 128 5 119 50S55 90 72 51 153 10 174 20" stroke="#b9563e88" stroke-width="1.5" stroke-dasharray="4 5"/></svg>'
PLANE = f'<img class="plane-icon" src="data:image/svg+xml;base64,{base64.b64encode(_PLANE_SVG.encode()).decode()}" alt="" aria-hidden="true">'
ROUTE = f'<img class="collage-route" src="data:image/svg+xml;base64,{base64.b64encode(_ROUTE_SVG.encode()).decode()}" alt="" aria-hidden="true">'
meeting_has_arrived = datetime.now(TIMEZONE) >= NEXT_MEETING

st.set_page_config(
    page_title="Las Machuqui-Aventuras · Un diario de viajes",
    page_icon="✈️", layout="wide", initial_sidebar_state="collapsed",
)
if "meeting_has_arrived" not in st.session_state:
    st.session_state.meeting_has_arrived = meeting_has_arrived
st.html(ROOT / "styles.css")


@st.cache_data(show_spinner=False)
def image_uri(relative_path: str) -> str:
    """Embed small cover images without remote hosting or changing originals."""
    with Image.open(IMAGES / relative_path) as original:
        photo = ImageOps.exif_transpose(original).convert("RGB")
        photo.thumbnail((1000, 1000))
        buffer = BytesIO()
        photo.save(buffer, format="JPEG", quality=86, optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def photo_paths(city_key: str) -> list[Path]:
    return sorted((IMAGES / city_key).glob("photo*.jpg"),
                  key=lambda path: int(path.stem.removeprefix("photo")))


st.html(f"""
<header class="journal-header">
  <a class="brand" href="#inicio" aria-label="Las Machuqui-Aventuras, inicio">
    <span class="brand-icon">{PLANE}</span>
    <span>las machuqui<span class="brand-second-line">aventuras</span></span>
  </a>
  <span class="header-note">UN PEQUEÑO DIARIO DE VIAJES</span>
  <a class="header-link" href="#atlas">Nuestros recuerdos <span aria-hidden="true">↗</span></a>
</header>
<section class="hero" id="inicio">
  <div class="hero-copy">
    <p class="eyebrow"><span class="tiny-star" aria-hidden="true">✷</span> LUGARES, ENCUENTROS Y RECUERDOS</p>
    <h1>Hay viajes que<br>se quedan <em>contigo.</em></h1>
    <p class="hero-description">Las ciudades cambian. Lo vivido se queda.<br>Y todavía hay lugares por descubrir.</p>
    <a class="text-link" href="#proximo-viaje">{'Una aventura más para recordar' if meeting_has_arrived else 'Una nueva aventura en el horizonte'} <span aria-hidden="true">↘</span></a>
  </div>
  <div class="hero-collage" aria-label="Recuerdos de Praga y París">
    <figure class="polaroid polaroid-back">
      <img src="{image_uri('Paris/photo1.jpg')}" alt="Un recuerdo de la visita a Disneyland París">
      <figcaption>un poquito de París</figcaption>
    </figure>
    <figure class="polaroid polaroid-front">
      <img src="{image_uri('Praga/photo1.jpg')}" alt="Julia y su compañero de viaje en Praga">
      <figcaption>Praga, para recordar.</figcaption>
    </figure>
    <div class="travel-stamp" aria-label="Eurotrip en Europa">{'RECUERDO DE VIAJE' if meeting_has_arrived else 'PRÓXIMA PARADA'}<strong>EUROPA</strong><span>12 · 11 · 2026</span></div>
    <span class="collage-spark" aria-hidden="true">✷</span>
    {ROUTE}
  </div>
</section>
""")


@st.fragment(run_every="1s")
def render_countdown():
    now = datetime.now(TIMEZONE)
    remaining = countdown_parts(now)
    departed = now >= NEXT_MEETING
    if departed != st.session_state.meeting_has_arrived:
        # Refresh the cover and itinerary once when the clock reaches the date.
        st.session_state.meeting_has_arrived = departed
        st.rerun()
    cells = "".join(
        f'<div class="clock-unit"><span class="clock-number">{value:02d}</span><span class="clock-label">{label}</span></div>'
        for value, label in zip(remaining, ("días", "horas", "minutos", "segundos"))
    )
    st.html(f"""
    <section class="boarding-pass" id="proximo-viaje" aria-label="Cuenta atrás hasta el 12 de noviembre de 2026, hora de Budapest">
      <div class="ticket-trip">
        <span class="eyebrow">{'EL ENCUENTRO' if departed else 'EL PRÓXIMO ENCUENTRO'}</span>
        <h2>Eurotrip <span class="ticket-plane">{PLANE}</span></h2>
        <p>Europa · un viaje con amigos</p>
      </div>
      <div class="ticket-clock">
        <span class="clock-title">{'Llegó el día. Buen viaje.' if departed else 'Nos vemos en'}</span>
        <div class="clock" role="timer" aria-live="off">{cells}</div>
      </div>
      <div class="ticket-date">
        <span class="eyebrow">GUARDA LA FECHA</span>
        <strong>12 NOV</strong><span class="ticket-year">2026</span>
        <span class="timezone-note">Hora de Budapest</span>
      </div>
    </section>
    """)


render_countdown()


@st.fragment(run_every="60s")
def render_timeline():
    now = datetime.now(TIMEZONE)
    position = route_position(now) * 100
    arrived = now >= NEXT_MEETING
    stops = []
    for index, milestone in enumerate(MILESTONES):
        future = milestone.date > now
        is_next = index == len(MILESTONES) - 1
        state = "next-stop" if is_next else ("future-stop" if future else "past-stop")
        stops.append(f"""
        <li class="route-stop {state}">
          <span class="stop-dot" aria-hidden="true"></span>
          <time datetime="{milestone.date.date().isoformat()}">{milestone.date.day:02d} {MONTHS[milestone.date.month - 1]} <span>{milestone.date.year}</span></time>
          <span class="stop-name">{escape(milestone.label)}</span>
          {'<span class="next-label">PRÓXIMA AVENTURA</span>' if is_next and not arrived else ''}
        </li>""")
    st.html(f"""
    <section class="timeline-card" id="ruta">
      <div class="timeline-heading">
        <div><p class="eyebrow">LA RUTA HASTA AQUÍ</p><h2>Cada encuentro cuenta.</h2></div>
        <span class="route-caption">Un recuerdo a la vez <span aria-hidden="true">↗</span></span>
      </div>
      <div class="route-scroll">
        <div class="flight-route" style="--flight-position:{position:.3f}%">
          <div class="route-track" aria-hidden="true"><span class="route-travelled"></span>
            <span class="route-airplane">{PLANE}{'' if arrived else '<span>en camino</span>'}</span>
          </div>
          <ol class="route-stops">{''.join(stops)}</ol>
        </div>
      </div>
      <p class="timeline-footnote">De aquel primer beso al próximo vuelo. Hay fechas que se quedan.</p>
    </section>
    """)


render_timeline()

st.html("""
<section class="section-heading" id="atlas">
  <div><p class="eyebrow">LOS LUGARES QUE NOS GUARDAN</p><h2>Un pequeño atlas de recuerdos.</h2></div>
  <span class="section-aside">03 ciudades <span aria-hidden="true">/</span> 02 continentes</span>
</section>
""")

with st.container(key="city_selector"):
    selected_city = st.radio(
        "Elige una ciudad para explorar sus recuerdos", options=list(CITIES), index=0,
        format_func=lambda city: CITIES[city]["label"], horizontal=True,
        label_visibility="collapsed", key="selected_city",
    )

city = CITIES[selected_city]
photos = photo_paths(selected_city)
with st.container(key="atlas_panels"):
    map_column, postcard_column = st.columns([1.7, 1], gap="large")

with map_column:
    with st.container(key="map_card"):
        st.html(f"""<div class="map-topline"><span class="eyebrow">EN EL MAPA</span><span class="map-location"><span aria-hidden="true">●</span> {escape(city['label'])}, {escape(city['country'])}</span></div>""")
        st.pydeck_chart(build_map(selected_city, city), height=350, width="stretch", key="travel_map")
        st.html("""<div class="map-bottomline"><span><i class="map-key" aria-hidden="true"></i> Un lugar en nuestra historia</span><span>Arrastra para explorar · rueda o pellizco para acercar</span></div>""")

with postcard_column:
    st.html(f"""
    <article class="destination-postcard" aria-label="Recuerdos de {escape(city['label'])}">
      <div class="postcard-photo"><img src="{image_uri(f'{selected_city}/photo1.jpg')}" alt="Una fotografía del álbum de {escape(city['label'])}"><span class="postcard-photo-label">DEL ÁLBUM DE VIAJE</span></div>
      <div class="postcard-body">
        <div class="postcard-title"><h3>{escape(city['label'])}</h3><span>{escape(city['country'])}</span></div>
        <p>{escape(city['description'])}</p>
        <div class="postcard-details"><span>{formatted_coordinates(selected_city)}</span><span>{len(photos):02d} recuerdos</span></div>
      </div>
    </article>
    """)

st.html(f"""
<div class="album-heading">
  <div><p class="eyebrow">PEQUEÑOS INSTANTES, GRANDES RECUERDOS</p><h2>El álbum de {escape(city['label'])}.</h2></div>
  <span class="album-count">{len(photos):02d} fotografías <span aria-hidden="true">↙</span></span>
</div>
""")

with st.container(key="photo_album"):
    for index, photo in enumerate(photos):
        st.image(str(photo), width="stretch", caption=f"{index + 1:02d} / {city['label']}")

st.html("""
<footer class="journal-footer">
  <div><span class="footer-star" aria-hidden="true">✷</span><p>Para los lugares que fuimos.<br><em>Y los que todavía nos esperan.</em></p></div>
  <span>Hecho de kilómetros y recuerdos.</span>
  <a href="#inicio" aria-label="Volver al inicio">Volver arriba <span aria-hidden="true">↑</span></a>
</footer>
""")
