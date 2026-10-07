# Las Machuqui-Aventuras

Un diario de viajes en Streamlit: cuenta atrás para el **12 de noviembre de 2026**, recorrido de encuentros, atlas interactivo y álbumes de Praga, París y Monterrey.

## Ejecutar

Con Python 3.11 o 3.12:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

En Streamlit Community Cloud, selecciona este repositorio y `app.py` como archivo principal. Las dependencias y el tema se cargan desde `requirements.txt` y `.streamlit/config.toml`. El mapa utiliza el GeoJSON incluido; no necesita claves, servicios de mapas ni variables secretas.

## Fechas y recuerdos

- `journey.py` contiene la fecha del próximo encuentro, los hitos y los destinos. El contador usa la hora de Budapest y respeta los cambios de horario; la fecha objetivo empieza a las 00:00.
- El contador se actualiza cada segundo con `st.fragment`, sin bloquear los controles. Al llegar la fecha se queda en cero y cambia el mensaje.
- Las fotos originales se conservan en `images/<ciudad>/photoN.jpg`. El álbum detecta y ordena todas las fotos de la ciudad, incluida `photo11.jpg` de Praga.
- `styles.css` adapta las tarjetas y el álbum al ancho de la pantalla; la línea de tiempo se vuelve vertical en móvil. Las fotos pueden ampliarse con el control nativo de Streamlit.

## Comprobar

```sh
python -m unittest discover -s tests -v
```

Las pruebas cubren fechas y horario de verano, posición del avión, cambios de ciudad, fotos y sincronización entre el país destacado y el marcador del mapa.
