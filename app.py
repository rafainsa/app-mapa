import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os

# 1. Configuración de la interfaz
st.set_page_config(page_title="Mapa Coropletas España", layout="wide")

# 2. Función de carga de datos optimizada (Motor Fiona)
@st.cache_data
def load_data():
    nombre_archivo = "spain-communities.geojson"
    if os.path.exists(nombre_archivo):
        try:
            # Usamos engine='fiona' para evitar errores de pyogrio en la nube
            gdf = gpd.read_file(nombre_archivo, engine='fiona')
            return gdf
        except Exception as e:
            # Intento de rescate si fiona no está disponible
            return gpd.read_file(nombre_archivo)
    else:
        st.error(f"❌ Error: El archivo '{nombre_archivo}' no existe en el repositorio.")
        return None

# Llamada a la carga
gdf = load_data()

if gdf is not None:
    st.title("🗺️ Generador de Mapas Estadísticos de España")
    st.info("Introduce tus datos en la tabla inferior para generar el mapa de coropletas.")

    # --- SECCIÓN 1: TABLA DE DATOS ---
    st.subheader("1. Datos por Comunidad Autónoma")
    
    # Extraer nombres únicos del archivo geojson
    comunidades = sorted(gdf['name'].unique())
    df_base = pd.DataFrame({'Comunidad': comunidades, 'Valor': [0.0]*len(comunidades)})
    
    # Editor de datos
    edited_df = st.data_editor(df_base, use_container_width=True, hide_index=True)

    # --- SECCIÓN 2: PROCESAMIENTO ---
    col1, col2 = st.columns(2)
    with col1:
        metodo = st.radio("Tratamiento de datos:", ["Dato directo (%)", "Calcular porcentaje (Absoluto / Total)"])
    
    if metodo == "Calcular porcentaje (Absoluto / Total)":
        with col2:
            total = st.number_input("Valor total de referencia:", min_value=0.01, value=100.0)
            edited_df['Valor_Final'] = (edited_df['Valor'] / total) * 100
            unidad = "% (Calc.)"
    else:
        edited_df['Valor_Final'] = edited_df['Valor']
        with col2:
            unidad = st.text_input("Etiqueta de unidad:", "%")

    # --- SECCIÓN 3: PERSONALIZACIÓN Y MAPA ---
    st.subheader("2. Visualización")
    c1, c2 = st.columns(2)
    with c1:
        titulo = st.text_input("Título del mapa:", "Distribución de Variable")
    with c2:
        paleta = st.selectbox("Color principal:", ["Blues", "Reds", "Greens", "Purples", "Oranges", "YlOrBr"])

    if st.button("🚀 Generar Mapa"):
        # Unión de datos (Geometría + Tabla)
        merged = gdf.merge(edited_df, left_on="name", right_on="Comunidad")
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 9))
        
        # Mapa con clasificación en 4 intervalos (Natural Breaks)
        merged.plot(column='Valor_Final', 
                    cmap=paleta, 
                    scheme='NaturalBreaks', 
                    k=4, 
                    ax=ax, 
                    edgecolor='black', 
                    linewidth=0.5,
                    legend=True,
                    legend_kwds={'loc': 'lower right', 'title': f"Leyenda ({unidad})"})

        # Título y limpieza
        ax.set_title(titulo, fontsize=22, pad=15)
        ax.axis('off')
        
        # Flecha del Norte
        ax.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.88),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    ha='center', va='center', fontsize=15, xycoords='axes fraction')
        
        # Escala Gráfica aproximada
        ax.text(0.05, 0.05, "0 __________ 250 km\nEscala 1:10.000.000", 
                transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        st.pyplot(fig)
