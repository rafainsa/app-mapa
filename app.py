import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import os  # Necesario para verificar archivos

# 1. Configuración de la Interfaz
st.set_page_config(page_title="Generador de Mapas España", layout="wide")
st.title("🗺️ Generador de Mapas de Coropletas: España")
st.sidebar.header("Configuración del Mapa")

# 2. Carga de Geometrías (Archivo Local corregido)
@st.cache_data
def load_data():
    nombre_archivo = "spain-communities.geojson"
    
    if os.path.exists(nombre_archivo):
        # CORRECCIÓN: Usar la variable nombre_archivo entre comillas
        gdf = gpd.read_file(nombre_archivo)
        return gdf
    else:
        st.error(f"No se encontró el archivo '{nombre_archivo}' en el repositorio.")
        return None

gdf = load_data()

# Solo continuamos si el mapa se cargó correctamente
if gdf is not None:
    # 3. Entrada de Datos
    st.subheader("1. Introducción de Datos")
    st.write("Introduce los valores para las 17 CCAA y 2 Ciudades Autónomas.")

    # Aseguramos nombres consistentes
    comunidades = sorted(gdf['name'].unique())
    data_input = pd.DataFrame({'Comunidad': comunidades, 'Valor': [0.0]*len(comunidades)})
    edited_df = st.data_editor(data_input, num_rows="fixed", use_container_width=True)

    # 4. Procesamiento de Datos (Relativos vs Absolutos)
    tipo_dato = st.radio("¿Cómo son los datos introducidos?", ["Ya son Relativos", "Son Absolutos (Calcular)"])

    if tipo_dato == "Son Absolutos (Calcular)":
        poblacion_total = st.number_input("Valor total de referencia (ej. Población total)", min_value=0.1, value=100.0)
        edited_df['Valor_Final'] = (edited_df['Valor'] / poblacion_total) * 100
        unidad = "%"
    else:
        # Aquí permitimos que sean números o texto (como códigos Koeppen)
        edited_df['Valor_Final'] = edited_df['Valor']
        unidad = st.text_input("Unidad de medida (ej. hab/km², %)", "%")

    # 5. Diseño del Mapa
    st.subheader("2. Elementos del Mapa")
    col_a, col_b = st.columns(2)
    with col_a:
        titulo = st.text_input("Título del Mapa", "Distribución de Variable en España")
    with col_b:
        color_base = st.selectbox("Familia cromática (Oscuro = Mayor valor)", ["Blues", "Reds", "Greens", "Purples", "Oranges", "YlOrBr"])

    # Botón para generar
    if st.button("🎨 Generar Mapa"):
        # Unión de datos
        merged = gdf.set_index('name').join(edited_df.set_index('Comunidad'))
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # Intentamos clasificación numérica (máximo 4 intervalos)
        try:
            merged.plot(column='Valor_Final', 
                        cmap=color_base, 
                        scheme='NaturalBreaks', 
                        k=4, 
                        ax=ax, 
                        edgecolor='0.3', 
                        linewidth=0.5,
                        legend=True,
                        legend_kwds={'loc': 'lower right', 'title': f"Intervalos ({unidad})"})
        except:
            # Si los datos son texto (ej: Csa, Csb), se dibujan como categorías
            merged.plot(column='Valor_Final', 
                        cmap=color_base, 
                        ax=ax, 
                        edgecolor='0.3', 
                        linewidth=0.5,
                        legend=True,
                        legend_kwds={'loc': 'lower right', 'title': "Categorías"})

        # Elementos esenciales
        ax.set_title(titulo, fontsize=18, pad=20)
        ax.axis('off')
        
        # Indicación del Norte
        x, y, arrow_length = 0.05, 0.95, 0.08
        ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    ha='center', va='center', fontsize=15, xycoords='axes fraction')
        
        # Escala
        ax.text(0.1, 0.05, "Escala 1:10.000.000 (Aprox)\nSistema de Referencia: ETRS89", 
                transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

        st.pyplot(fig)
