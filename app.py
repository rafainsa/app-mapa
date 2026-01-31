import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os

# LÍNEA MAESTRA: Desactiva pyogrio para evitar errores de carga en la nube
import geopandas; geopandas.options.use_pyogrio = False

st.set_page_config(page_title="Mapa Coropletas España", layout="wide")

@st.cache_data
def load_data():
    # El nombre del archivo debe ser exacto al de GitHub
    nombre_archivo = "spain-communities.geojson"
    if os.path.exists(nombre_archivo):
        # Al haber desactivado pyogrio arriba, usará fiona por defecto
        return gpd.read_file(nombre_archivo)
    else:
        st.error(f"❌ No se encuentra el archivo '{nombre_archivo}' en el repositorio.")
        return None

gdf = load_data()

if gdf is not None:
    st.title("🗺️ Generador de Mapas Estadísticos de España")
    
    # 1. Entrada de datos
    st.subheader("1. Tabla de datos por Comunidad")
    comunidades = sorted(gdf['name'].unique())
    df_base = pd.DataFrame({'Comunidad': comunidades, 'Valor': [0.0]*len(comunidades)})
    edited_df = st.data_editor(df_base, use_container_width=True, hide_index=True)

    # 2. Lógica de cálculo
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.radio("Formato de datos:", ["Dato directo", "Calcular % sobre total"])
    
    if tipo == "Calcular % sobre total":
        with col2:
            total_ref = st.number_input("Total de referencia:", min_value=0.01, value=100.0)
            edited_df['Valor_Final'] = (edited_df['Valor'] / total_ref) * 100
            unidad = "%"
    else:
        edited_df['Valor_Final'] = edited_df['Valor']
        with col2:
            unidad = st.text_input("Unidad:", "uds")

    # 3. Diseño del mapa
    st.subheader("2. Configuración visual")
    c1, c2 = st.columns(2)
    with c1:
        titulo_mapa = st.text_input("Título del mapa:", "Mapa Temático")
        paleta = st.selectbox("Color:", ["Blues", "Reds", "Greens", "Purples", "Oranges"])
    with c2:
        st.info("El mapa se dividirá automáticamente en 4 intervalos (Natural Breaks).")

    if st.button("🎨 Generar Mapa"):
        merged = gdf.merge(edited_df, left_on="name", right_on="Comunidad")
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 9))
        
        # CLASIFICACIÓN EN 4 INTERVALOS
        merged.plot(column='Valor_Final', 
                    cmap=paleta, 
                    scheme='NaturalBreaks', 
                    k=4, 
                    ax=ax, 
                    edgecolor='black', 
                    linewidth=0.5,
                    legend=True,
                    legend_kwds={'loc': 'lower right', 'title': f"Leyenda ({unidad})"})

        ax.set_title(titulo_mapa, fontsize=20, pad=10)
        
        # Elementos cartográficos: Flecha Norte y Escala
        ax.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.88),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    ha='center', va='center', fontsize=15, xycoords='axes fraction')
        
        ax.text(0.05, 0.05, "0 __________ 250 km\nEscala 1:10.000.000", 
                transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        ax.axis('off')
        st.pyplot(fig)
