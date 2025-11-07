import streamlit as st
import datetime
import os
import time
import plotly.graph_objects as go
from PIL import Image
import pydeck as pdk
import json

st.set_page_config(page_title="Las Machuqui-Aventuras", page_icon="✈️", layout="wide")

# =========================
# Fechas importantes
# =========================
start_date = datetime.datetime(2025, 1, 4)   # Primer beso
prague_date = datetime.datetime(2025, 5, 10) # Visita Praga
monterrey_date = datetime.datetime(2025, 6, 6)  # Visita Monterrey
next_date = datetime.datetime(2025, 11, 14)  # Próxima visita

def get_time_remaining():
    now = datetime.datetime.now()
    time_left = next_date - now
    # Corrige negativos si ya pasó la fecha
    if time_left.total_seconds() < 0:
        return "¡Ya juntos! ❤️"
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} días, {hours:02d} horas, {minutes:02d} minutos, {seconds:02d} segundos"

MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
def fecha_corta(dt):
    return f"{dt.day} {MESES_ES[dt.month-1]}"

# =========================
# Título
# =========================
st.markdown("<h1 style='text-align: center;'>Las Machuqui-Aventuras</h1>", unsafe_allow_html=True)

# Rutas raíz
image_root = "images"
airplane_path = os.path.join(image_root, "airplane.png")
geojson_path = os.path.join(image_root, "countries.geojson")

# =========================
# Layout principal
# =========================
col1, col2, col3 = st.columns([0.8, 2.4, 0.8])

# ---------- Columna central: Timeline ----------
with col2:
    st.markdown("<h2 style='text-align: center;'>¡Cuenta regresiva para volver a vernos!</h2>", unsafe_allow_html=True)
    countdown_placeholder = st.empty()

    total_seg = (next_date - start_date).total_seconds()
    progreso = (datetime.datetime.now() - start_date).total_seconds() / total_seg if total_seg > 0 else 0
    progreso = max(0.0, min(1.0, progreso))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0.5, 0.5],
        mode='lines', line=dict(color='gray', width=8), showlegend=False
    ))

    hitos = [start_date, prague_date, monterrey_date, next_date]
    posiciones = [max(0.0, min(1.0, (d - start_date).total_seconds() / total_seg)) for d in hitos]
    etiquetas = [fecha_corta(d) for d in hitos]

    fig.add_trace(go.Scatter(
        x=posiciones,
        y=[0.5]*4,
        mode='markers+text',
        marker=dict(color='red', size=12),
        text=etiquetas,
        textposition="top center",
        showlegend=False
    ))

    airplane_img = Image.open(airplane_path)
    fig.add_layout_image(
        dict(
            source=airplane_img,
            x=progreso, y=0.56,
            xref="x", yref="y",
            sizex=1, sizey=1,
            xanchor="center", yanchor="middle"
        )
    )

    fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, fixedrange=True)
    fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, fixedrange=True)
    fig.update_layout(
        width=600, height=120,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig, use_container_width=True)

    # ===== Selector de ciudad (aquí: debajo del timeline, arriba del mapa) =====
    st.markdown("<h3 style='text-align: center;'>Nuestras ciudades</h3>", unsafe_allow_html=True)
    cities = {
        "Monterrey": {"lat": 25.6866, "lon": -100.3161, "country": "Mexico"},
        "Praga": {"lat": 50.0755, "lon": 14.4378, "country": "Czechia"},
        "Paris": {"lat": 48.8566, "lon": 2.3522, "country": "France"},
    }
    default_idx = list(cities.keys()).index("Monterrey")
    selected_city = st.selectbox(
        "Selecciona una ciudad para enfocarla en el mapa:",
        list(cities.keys()),
        index=default_idx
    )
    selected_data = cities[selected_city]
    city_folder = os.path.join(image_root, selected_city)

    # ---------- Mapa ----------
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    country_feature = next(
        (feat for feat in geojson_data["features"] if feat["properties"]["name"] == selected_data["country"]),
        None
    )

    geojson_layer = []
    if country_feature:
        geojson_layer = [
            pdk.Layer(
                "GeoJsonLayer",
                data=country_feature,
                get_fill_color='[0, 100, 200, 80]',
                get_line_color='[0, 0, 0]',
                line_width_min_pixels=1,
                pickable=False,
            )
        ]

    view_state = pdk.ViewState(
        latitude=selected_data["lat"],
        longitude=selected_data["lon"],
        zoom=5,
        pitch=0
    )

    city_data = [{"name": name, "lat": val["lat"], "lon": val["lon"]} for name, val in cities.items()]
    city_layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=city_data,
            get_position='[lon, lat]',
            get_fill_color='[200, 30, 0, 160]',
            get_radius=80000,
        ),
        pdk.Layer(
            "TextLayer",
            data=city_data,
            get_position='[lon, lat]',
            get_text='name',
            get_size=16,
            get_color=[0, 0, 0],
            get_angle=0,
            get_alignment_baseline="'bottom'"
        )
    ]
    
    st.pydeck_chart(pdk.Deck(
    map_provider="carto",
    map_style=pdk.map_styles.MAPBOX_LIGHT,     # LIGHT | DARK | ROAD | SATELLITE
    initial_view_state=view_state,
    layers=geojson_layer + city_layers
    ), height=400)
    
    
    # st.pydeck_chart(pdk.Deck(
    #     map_style="mapbox://styles/mapbox/light-v10",
    #     initial_view_state=view_state,
    #     layers=geojson_layer + city_layers
    # ), height=400)

    # ---------- Fotos centro (5 y 6) ----------
    st.markdown(f"<h4 style='text-align: center;'>Fotos de {selected_city}</h4>", unsafe_allow_html=True)
    mid_c1, mid_c2 = st.columns(2)
    with mid_c1:
        st.image(os.path.join(city_folder, "photo5.jpg"), use_container_width=True)
    with mid_c2:
        st.image(os.path.join(city_folder, "photo6.jpg"), use_container_width=True)

# ---------- Columna izquierda (1–4) y derecha (7–10) dependen del selected_city ----------
# Nota: estas van DESPUÉS del selectbox para que ya exista selected_city / city_folder.

with col1:
    city_folder = os.path.join(image_root, selected_city)
    for i in range(1, 5):
        st.image(os.path.join(city_folder, f"photo{i}.jpg"), use_container_width=True)

with col3:
    city_folder = os.path.join(image_root, selected_city)
    for i in range(7, 11):
        st.image(os.path.join(city_folder, f"photo{i}.jpg"), use_container_width=True)


# Contador en tiempo real 
while True: 
    countdown_placeholder.markdown(f"<h3 style='text-align: center;'> {get_time_remaining()} </h3>", unsafe_allow_html=True) 
    time.sleep(1)
