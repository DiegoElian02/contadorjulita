import streamlit as st
import datetime
import os
import time
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="Cuenta Regresiva", page_icon="✈️", layout="wide")

# Fechas importantes
start_date = datetime.datetime(2025, 1, 4)  # Primer beso
event_date = datetime.datetime(2025, 5, 10)  # Día de la visita

def get_time_remaining():
    now = datetime.datetime.now()
    time_left = event_date - now
    days = time_left.days
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days} días, {hours:02d} horas, {minutes:02d} minutos, {seconds:02d} segundos"

# Título principal centrado
st.markdown("""
    <h1 style='text-align: center;'>Cuenta Regresiva para el 10 de Mayo</h1>
""", unsafe_allow_html=True)

# Diseño de la página
image_folder = "images"
image_files = [f for f in os.listdir(image_folder) if f.endswith((".jpg", ".png"))]

if len(image_files) >= 10:
    col1, col2, col3 = st.columns([0.8, 2.4, 0.8])

    # Izquierda: 3 imágenes en columna
    with col1:
        for i in range(3):
            st.image(os.path.join(image_folder, f"photo{i+1}.jpg"), use_container_width=True)

    # Centro: Contador en vivo y línea de progreso con avión
    with col2:
        st.markdown("""
            <h2 style='text-align: center;'> Tiempo para volver a besarte!!:</h2>
        """, unsafe_allow_html=True)
        countdown_placeholder = st.empty()
        
        progress = (datetime.datetime.now() - start_date).total_seconds() / (event_date - start_date).total_seconds()
        
        # Crear barra de progreso personalizada con Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0.5, 0.5], mode='lines', line=dict(color='gray', width=8, dash='solid'), showlegend=False
        ))
        
        # Etiquetas de fechas ajustadas
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0.5, 0.5],
            text=["4 Ene", "10 May"],
            mode="text",
            textposition="top center",
            showlegend=False,
            textfont=dict(size=10, color="black")
        ))
        
        # Ajustar la posición del avión correctamente
        airplane_img = Image.open(os.path.join(image_folder, "airplane.png"))
        fig.add_layout_image(
            dict(
                source=airplane_img,
                x=progress, y=0.56, xref="x", yref="y",
                sizex=1, sizey=1, xanchor="center", yanchor="middle"
            )
        )
        
        fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, fixedrange=True)
        fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, fixedrange=True)
        fig.update_layout(
            width=600, height=120, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Agregar 3 imágenes en medio, justo debajo de la línea de progreso
        mid_col1, mid_col2, mid_col3 = st.columns(3)
        with mid_col1:
            st.image(os.path.join(image_folder, "photo7.jpg"), use_container_width=True)
            st.image(os.path.join(image_folder, "photo10.jpg"), use_container_width=True)
        with mid_col2:
            st.image(os.path.join(image_folder, "photo8.jpg"), use_container_width=True)
            st.image(os.path.join(image_folder, "photo11.jpg"), use_container_width=True)
        with mid_col3:
            st.image(os.path.join(image_folder, "photo9.jpg"), use_container_width=True)
            st.image(os.path.join(image_folder, "photo12.jpg"), use_container_width=True)

    # Derecha: 3 imágenes en columna
    with col3:
        for i in range(3, 6):
            st.image(os.path.join(image_folder, f"photo{i+1}.jpg"), use_container_width=True)

    # Actualización en tiempo real del contador
    while True:
        countdown_placeholder.markdown(f"""
            <h3 style='text-align: center;'> {get_time_remaining()} </h3>
        """, unsafe_allow_html=True)
        time.sleep(1)
else:
    st.error("Se necesitan al menos 10 imágenes en la carpeta 'images' para mostrar correctamente la galería y el avioncito.")