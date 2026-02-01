import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Generador de Mapas Coropléticos", layout="wide")

@st.cache_data
def load_and_move_canarias():
    # URL del GeoJSON de comunidades autónomas
    url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson"
    gdf = gpd.read_file(url)
    
    # --- Lógica para desplazar Canarias ---
    canarias = gdf[gdf['name'] == 'Canarias'].copy()
    peninsula = gdf[gdf['name'] != 'Canarias'].copy()
    
    # Desplazamiento geométrico para que aparezcan cerca de la península
    # xoff: mueve horizontalmente, yoff: mueve verticalmente
    canarias['geometry'] = canarias['geometry'].translate(xoff=5.5, yoff=7.5)
    
    return pd.concat([peninsula, canarias])

gdf = load_and_move_canarias()

if gdf is not None:
    st.title("🗺️ Diseñador de Mapas Temáticos de España")
    st.markdown("Herramienta avanzada para la representación de datos espaciales.")
    
    # --- 1. ENTRADA DE DATOS ---
    st.subheader("1. Tabla de Datos")
    comunidades = sorted(gdf['name'].unique())
    df_base = pd.DataFrame({'Comunidad': comunidades, 'Dato_Origen': [0.0]*len(comunidades)})
    
    st.info("Introduce los datos en la columna 'Dato_Origen'.")
    edited_df = st.data_editor(df_base, use_container_width=True, hide_index=True)

    # --- 2. TRATAMIENTO ESTADÍSTICO (RELATIVOS VS ABSOLUTOS) ---
    st.divider()
    st.subheader("2. Tratamiento de los Datos")
    
    tipo_dato = st.radio("Naturaleza del dato introducido:", 
                         ["Dato Relativo (ya es una tasa o %)", "Dato Absoluto (necesita conversión)"])
    
    if tipo_dato == "Dato Absoluto (necesita conversión)":
        col_calc1, col_calc2 = st.columns(2)
        with col_calc1:
            divisor = st.number_input("Valor de referencia (Divisor):", 
                                      min_value=0.0001, value=1.0, 
                                      help="Suele ser la población total o superficie total.")
        with col_calc2:
            multiplicador = st.number_input("Multiplicador ajustable (K):", 
                                            value=100, 
                                            help="Usa 100 para %, 1.000 para tasas por mil, etc.")
        
        # Fórmula: (Valor / Referencia) * K
        edited_df['Valor_Final'] = (edited_df['Dato_Origen'] / divisor) * multiplicador
        st.caption(f"Fórmula aplicada: (Dato / {divisor}) * {multiplicador}")
        label_unidad = f"Tasa (K={multiplicador})"
    else:
        edited_df['Valor_Final'] = edited_df['Dato_Origen']
        label_unidad = st.text_input("Unidad de medida (ej. %, hab/km²):", "%")

    # --- 3. DISEÑO Y REPRESENTACIÓN ---
    st.divider()
    st.subheader("3. Configuración Visual")
    col1, col2 = st.columns(2)
    with col1:
        titulo = st.text_input("Título del mapa:", "Distribución Geográfica")
        paleta = st.selectbox("Gama de colores:", ["Blues", "Reds", "YlOrBr", "Purples", "Greens"])
    with col2:
        st.write("**Clasificación:**")
        st.write("- Método: Natural Breaks (Jenks)")
        st.write("- Intervalos: 4 (Máximo recomendado)")

    # --- 4. GENERACIÓN DEL MAPA ---
    if st.button("🎨 Generar y Visualizar Mapa"):
        # Unir datos con geometría
        merged = gdf.merge(edited_df, left_on="name", right_on="Comunidad")
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # Mapa coroplético
        merged.plot(column='Valor_Final', 
                    cmap=paleta, 
                    scheme='NaturalBreaks', 
                    k=4, 
                    ax=ax, 
                    edgecolor='black', 
                    linewidth=0.5,
                    legend=True,
                    legend_kwds={'loc': 'lower right', 'title': f"Unidades: {label_unidad}"})

        # Estética final
        ax.set_title(titulo, fontsize=22, pad=20)
        
        # Indicador de Canarias
        ax.text(0.1, 0.28, "Canarias\n(desplazadas)", transform=ax.transAxes, 
                fontsize=9, color='gray', style='italic', ha='center',
                bbox=dict(facecolor='white', alpha=0.5, edgecolor='gray', boxstyle='round,pad=0.5'))
        
        # Flecha Norte
        ax.annotate('N', xy=(0.05, 0.95), xytext=(0.05, 0.88),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    ha='center', va='center', fontsize=15, xycoords='axes fraction')
        
        # Escala Gráfica
        ax.text(0.05, 0.05, "0 __________ 250 km\nEscala 1:10.000.000", 
                transform=ax.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        ax.axis('off')
        
        # Mostrar en Streamlit
        st.pyplot(fig)
