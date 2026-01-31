import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os

# 1. Configuración de la página
st.set_page_config(page_title="App Mapas España - Datos Estadísticos", layout="wide")

# 2. Función para cargar el mapa (Archivo GeoJSON local)
@st.cache_data
def load_data():
    nombre_archivo = "spain-communities.geojson"
    if os.path.exists(nombre_archivo):
        try:
            # Usamos el motor fiona por estabilidad
            gdf = gpd.read_file(nombre_archivo, engine='fiona')
            return gdf
        except:
            return gpd.read_file(nombre_archivo)
    else:
        st.error(f"❌ No se encuentra el archivo '{nombre_archivo}'.")
        return None

gdf = load_data()

if gdf is not None:
    st.title("🗺️ Generador de Mapas Estadísticos de España")
    st.markdown("Crea mapas de coropletas basados en intervalos numéricos.")

    # --- BLOQUE 1: ENTRADA DE DATOS NUMÉRICOS ---
    st.subheader("1. Introducción de Datos")
    
    # Extraer nombres de las CCAA
    comunidades = sorted(gdf['name'].unique())
    df_base = pd.DataFrame({'Comunidad': comunidades, 'Valor': [0.0]*len(comunidades)})
    
    st.write("Introduce los datos numéricos en la tabla:")
    edited_df = st.data_editor(df_base, use_container_width=True, hide_index=True)

    # --- BLOQUE 2: PROCESAMIENTO ESTADÍSTICO ---
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_valor = st.radio("Tipo de dato:", ["Valor Relativo (%)", "Valor Absoluto (Calcular %)"])
    
    if tipo_valor == "Valor Absoluto (Calcular %)":
        with col2:
            total_ref = st.number_input("Total de referencia (ej. Población total):", min_value=0.01, value=100.0)
            edited_df['Valor_Final'] = (edited_df['Valor'] / total_ref) * 100
            unidad_label = "% (Calculado)"
    else:
        edited_df['Valor_Final'] = edited_df['Valor']
        with col2:
            unidad_label = st.text_input("Unidad de medida:", "%")

    # --- BLOQUE 3: DISEÑO DEL MAPA ---
    st.subheader("2. Estética y Elementos del Mapa")
    col_a, col_b = st.columns(2)
    
    with col_a:
        titulo_mapa = st.text_input("Título del Mapa:", "Mapa de Distribución")
        color_familia = st.selectbox("Gama de colores:", ["Blues", "Reds", "Greens", "Purples", "Oranges", "YlOrBr"])
    
    with col_b:
        st.info("El mapa dividirá los datos en 4 intervalos automáticos para un análisis claro.")

    # --- BLOQUE 4: RENDERIZADO DEL MAPA ---
    if st.button("🚀 Generar Mapa"):
        # Unir datos con el mapa
        merged = gdf.merge(edited_df, left_on="name", right_on="Comunidad")
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 9))
        
        # Clasificación obligatoria en 4 intervalos numéricos
        merged.plot(column='Valor_Final', 
                    cmap=color_familia, 
                    scheme='NaturalBreaks', 
                    k=4, 
                    ax=ax, 
                    edgecolor='black', 
                    linewidth=0.5,
                    legend=True,
                    legend_kwds={'loc': 'lower right', 'title': f"Intervalos ({unidad_label})"})

        # Título y limpieza de ejes
        ax.set_title(titulo_mapa, fontsize=20, pad=15)
        ax.axis('off')
        
        # Flecha del Norte
        ax.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.88),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    ha='center', va='center', fontsize=15, xycoords='axes fraction')
        
        # Escala Gráfica
        ax.text(0.05, 0.05, "0 __________ 250 km\nEscala 1:10.000.000", 
                transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        # Mostrar resultado
        st.pyplot(fig)
