import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os

# Configuración de la página
st.set_page_config(page_title="Mapa Coropletas España", layout="wide")

@st.cache_data
def load_data():
    nombre_archivo = "spain-communities.geojson"
    if os.path.exists(nombre_archivo):
        # Leemos sin forzar motores para evitar conflictos de versiones
        return gpd.read_file(nombre_archivo)
    else:
        st.error(f"❌ No se encuentra el archivo '{nombre_archivo}'")
        return None

gdf = load_data()

if gdf is not None:
    st.title("🗺️ Generador de Mapas de España")
    
    # 1. Tabla de datos
    comunidades = sorted(gdf['name'].unique())
    df_base = pd.DataFrame({'Comunidad': comunidades, 'Valor': [0.0]*len(comunidades)})
    st.subheader("1. Introduce los datos")
    edited_df = st.data_editor(df_base, use_container_width=True, hide_index=True)

    # 2. Configuración
    col1, col2 = st.columns(2)
    with col1:
        titulo_mapa = st.text_input("Título:", "Distribución Territorial")
    with col2:
        paleta = st.selectbox("Color:", ["Blues", "Reds", "Greens", "Oranges"])

    if st.button("🎨 Generar Mapa"):
        # Unir datos
        merged = gdf.merge(edited_df, left_on="name", right_on="Comunidad")
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 9))
        
        # Mapa con 4 intervalos
        merged.plot(column='Valor', 
                    cmap=paleta, 
                    scheme='NaturalBreaks', 
                    k=4, 
                    ax=ax, 
                    edgecolor='black', 
                    linewidth=0.5,
                    legend=True,
                    legend_kwds={'loc': 'lower right'})

        ax.set_title(titulo_mapa, fontsize=18)
        
        # Elementos fijos
        ax.annotate('N', xy=(0.05, 0.9), xytext=(0.05, 0.8),
                    arrowprops=dict(facecolor='black', width=2, headwidth=8),
                    ha='center', va='center', fontsize=12, xycoords='axes fraction')
        
        ax.text(0.05, 0.05, "Escala 1:10.000.000", transform=ax.transAxes, 
                fontsize=8, bbox=dict(facecolor='white', alpha=0.5))
        
        ax.axis('off')
        st.pyplot(fig)
