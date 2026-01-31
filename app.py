import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Mapa Coropletas España", layout="wide")

@st.cache_data
def load_data():
    # URL directa al archivo GeoJSON real y comprobado
    url_mapa = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson"
    try:
        # Intentamos cargar desde la URL directamente para evitar fallos de archivos locales
        gdf = gpd.read_file(url_mapa)
        return gdf
    except Exception as e:
        st.error(f"Error al cargar el mapa: {e}")
        return None

gdf = load_data()

if gdf is not None:
    st.title("🗺️ Generador de Mapas de España")
    
    # 1. Tabla de datos
    # En este archivo la columna se llama 'name'
    comunidades = sorted(gdf['name'].unique())
    df_base = pd.DataFrame({'Comunidad': comunidades, 'Valor': [0.0]*len(comunidades)})
    
    st.subheader("1. Introduce los datos numéricos")
    edited_df = st.data_editor(df_base, use_container_width=True, hide_index=True)

    # 2. Configuración visual
    col1, col2 = st.columns(2)
    with col1:
        titulo_mapa = st.text_input("Título del mapa:", "Mapa de España")
    with col2:
        paleta = st.selectbox("Gama de colores:", ["Blues", "Reds", "Greens", "Purples", "Oranges"])

    if st.button("🎨 Generar Mapa"):
        # Unir datos (Geometría + Tabla)
        merged = gdf.merge(edited_df, left_on="name", right_on="Comunidad")
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 9))
        
        # Clasificación en 4 intervalos (Máximo permitido)
        merged.plot(column='Valor', 
                    cmap=paleta, 
                    scheme='NaturalBreaks', 
                    k=4, 
                    ax=ax, 
                    edgecolor='black', 
                    linewidth=0.5,
                    legend=True,
                    legend_kwds={'loc': 'lower right', 'title': "Intervalos"})

        ax.set_title(titulo_mapa, fontsize=20, pad=10)
        
        # Flecha del Norte
        ax.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.88),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    ha='center', va='center', fontsize=15, xycoords='axes fraction')
        
        # Escala Gráfica
        ax.text(0.05, 0.05, "0 __________ 250 km\nEscala 1:10.000.000", 
                transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        ax.axis('off')
        st.pyplot(fig)
