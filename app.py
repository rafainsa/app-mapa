import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

# 1. Configuración de la Interfaz
st.title("Generador de Mapas de Coropletas: España")
st.sidebar.header("Configuración del Mapa")

# 2. Carga de Geometrías (Simplificado para el ejemplo)
@st.cache_data
def load_data():
    # Definimos el nombre del archivo que descargaste
    nombre_archivo = "spain-communities.geojson"
    
    # Verificamos si el archivo existe en la carpeta para evitar errores
    if os.path.exists(nombre_archivo):
        # Cargamos el archivo localmente
        gdf = gpd.read_file(spain-communities.geojson)
        return gdf
    else:
        # Si por alguna razón no lo encuentra, mostramos un error en la App
        st.error(f"No se encontró el archivo {spain-communities.geojson} en el repositorio.")
        return None

# Llamamos a la función para cargar el mapa
gdf = load_data()

# 3. Entrada de Datos
st.subheader("1. Introducción de Datos")
st.write("Introduce los valores para las 17 CCAA y 2 Ciudades Autónomas.")

# Crear un DataFrame vacío para que el usuario rellene
comunidades = gdf['name'].unique()
data_input = pd.DataFrame({'Comunidad': comunidades, 'Valor': [0.0]*len(comunidades)})
edited_df = st.data_editor(data_input, num_rows="fixed")

# 4. Procesamiento de Datos (Relativos vs Absolutos)
tipo_dato = st.radio("¿El valor introducido es relativo (ej. %) o absoluto?", ["Relativo", "Absoluto"])

if tipo_dato == "Absoluto":
    poblacion_total = st.number_input("Introduce el valor total de referencia para calcular el valor relativo (ej. Población total)", value=1.0)
    edited_df['Valor_Final'] = (edited_df['Valor'] / poblacion_total) * 100
    unidad = "%"
else:
    edited_df['Valor_Final'] = edited_df['Valor']
    unidad = st.text_input("Unidad de medida (ej. hab/km², %)", "%")

# 5. Diseño del Mapa
st.subheader("2. Elementos del Mapa")
titulo = st.text_input("Título del Mapa", "Distribución de Variable en España")
color_base = st.selectbox("Familia cromática", ["Blues", "Reds", "Greens", "Purples", "Oranges"])

# Botón para generar
if st.button("Generar Mapa"):
    # Join de datos
    merged = gdf.set_index('name').join(edited_df.set_index('Comunidad'))
    
    # Crear figura
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Clasificación en 4 intervalos (Cuantiles o Natural Breaks)
    # Usamos colores secuenciales (gradaciones)
    merged.plot(column='Valor_Final', 
                cmap=color_base, 
                scheme='Quantiles', 
                k=4, 
                ax=ax, 
                edgecolor='0.5', 
                linewidth=0.5,
                legend=True,
                legend_kwds={'loc': 'lower right', 'title': f"Intervalos ({unidad})"})

    # Elementos esenciales
    ax.set_title(titulo, fontsize=16)
    ax.axis('off')
    
    # Indicación del Norte (Simple)
    x, y, arrow_length = 0.05, 0.95, 0.08
    ax.annotate('N', xy=(x, y), xytext=(x, y-arrow_length),
                arrowprops=dict(facecolor='black', width=5, headwidth=15),
                ha='center', va='center', fontsize=20, xycoords='axes fraction')
    
    # Escala (Representación visual simplificada)
    ax.text(0.1, 0.05, "Escala 1:10.000.000 (Aprox)", transform=ax.transAxes, fontsize=10)

    st.pyplot(fig)
