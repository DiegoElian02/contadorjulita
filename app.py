import streamlit as st
import datetime
import os
import time
import plotly.graph_objects as go
from PIL import Image
import pydeck as pdk
import json

st.set_page_config(page_title="Cuenta Regresiva", page_icon="✈️", layout="wide")

# Fechas importantes
start_date = datetime.datetime(2025, 1, 4)  # Primer beso
past_event = datetime.datetime(2025, 5, 10)  # Visita pasada
event_date = datetime.datetime(2025, 6, 6)   # Próximo reencuentro


def get_time_remaining():
    now = datetime.datetime.now()
    time_left = event_date - now
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} días, {hours:02d} horas, {minutes:02d} minutos, {seconds:02d} segundos"

# Título principal centrado
st.markdown("""
    <h1 style='text-align: center;'>Cuenta regresiva para volver a vernos</h1>
""", unsafe_allow_html=True)

# Diseño de la página
image_folder = "images"

col1, col2, col3 = st.columns([0.8, 2.4, 0.8])

with col1:
    for i in range(3):
        st.image(os.path.join(image_folder, f"photo{i+1}.jpg"), use_container_width=True)

with col2:
    st.markdown("""
        <h2 style='text-align: center;'> Te extraño!!</h2>
    """, unsafe_allow_html=True)
    countdown_placeholder = st.empty()
    
    # Línea del tiempo actualizada
    progress = (datetime.datetime.now() - start_date).total_seconds() / (event_date - start_date).total_seconds()
    progress = max(0, min(1, progress))  # asegurar que esté entre 0 y 1
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            x=[0, 1], y=[0.5, 0.5],
            mode='lines', line=dict(color='gray', width=8), showlegend=False
        ))
    
    # Puntos de fechas clave
    # Puntos de fechas clave
    fig.add_trace(go.Scatter(
        x=[
            0,
            (past_event - start_date).total_seconds() / (event_date - start_date).total_seconds(),
            1
        ],
        y=[0.5, 0.5, 0.5],
        mode='markers+text',
        marker=dict(color='red', size=12),
        text=["4 Ene", "10 Mayo", "6 Jun"],
        textposition="top center",
        showlegend=False
    ))
    
    # Avión avanzando
    airplane_img = Image.open(os.path.join(image_folder, "airplane.png"))
    fig.add_layout_image(
        dict(
            source=airplane_img,
            x=progress, y=0.56,
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
    
        # Selección de ciudad
    st.markdown("<h3 style='text-align: center;'>Nuestras ciudades</h3>", unsafe_allow_html=True)
    cities = {
        "Monterrey": {"lat": 25.6866, "lon": -100.3161, "country": "Mexico"},
        "Praga": {"lat": 50.0755, "lon": 14.4378, "country": "Czechia"},
        "Paris": {"lat": 48.8566, "lon": 2.3522, "country": "France"},
    }
    selected_city = st.selectbox("Selecciona una ciudad para enfocarla en el mapa:", list(cities.keys()))
    selected_data = cities[selected_city]

    # Cargar GeoJSON mundial (usa uno general como https://geojson-maps.ash.ms/)
    geojson_path = os.path.join(image_folder, "countries.geojson")
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Filtrar al país seleccionado
    country_feature = next((f for f in geojson_data["features"]
                            if f["properties"]["name"] == selected_data["country"]), None)

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

    # Datos de ciudades
    city_data = [{"name": name, "lat": val["lat"], "lon": val["lon"]} for name, val in cities.items()]
    city_layer = [
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
        map_style="mapbox://styles/mapbox/light-v10",
        initial_view_state=view_state,
        layers=geojson_layer + city_layer
    ), height=400)

    # Imágenes según la ciudad seleccionada
    st.markdown(f"<h4 style='text-align: center;'>Fotos de {selected_city}</h4>", unsafe_allow_html=True)
    photo1 = os.path.join(image_folder, f"{selected_city()}1.jpg")
    photo2 = os.path.join(image_folder, f"{selected_city()}2.jpg")
    img_col1, img_col2 = st.columns(2)
    with img_col1:
        st.image(photo1, use_container_width=True)
    with img_col2:
        st.image(photo2, use_container_width=True)

# Columna derecha
with col3:
    for i in range(4, 7):
        st.image(os.path.join(image_folder, f"photo{i}.jpg"), use_container_width=True)

# Contador en tiempo real
while True:
    countdown_placeholder.markdown(f"<h3 style='text-align: center;'> {get_time_remaining()} </h3>", unsafe_allow_html=True)
    time.sleep(1)