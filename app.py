import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Generador de Mapas Temáticos", layout="wide")

@st.cache_data
def load_and_move_canarias():
    url = "https://raw.githubusercontent.com/codeforgermany/click_that_hood/main/public/data/spain-communities.geojson"
    gdf = gpd.read_file(url)
    canarias = gdf[gdf['name'] == 'Canarias'].copy()
    peninsula = gdf[gdf['name'] != 'Canarias'].copy()
    canarias['geometry'] = canarias['geometry'].translate(xoff=5.5, yoff=7.5)
    return pd.concat([peninsula, canarias])

gdf = load_and_move_canarias()

if gdf is not None:
    st.title("🗺️ Diseñador de Mapas Temáticos de España")
    
    # --- 1. CONFIGURACIÓN DE DATOS ---
    st.subheader("1. Entrada de datos")
    tipo_entrada = st.radio(
        "¿Cómo vas a introducir los datos?",
        ["Tengo el dato relativo (%, densidad, tasa)", "Tengo datos absolutos (requiere cálculo)"],
        horizontal=True
    )

    comunidades = sorted(gdf['name'].unique())
    
    if tipo_entrada == "Tengo el dato relativo (%, densidad, tasa)":
        df_input = pd.DataFrame({'Comunidad': comunidades, 'Valor Relativo': [0.0]*len(comunidades)})
        edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)
        edited_df['Resultado_Final'] = edited_df['Valor Relativo']
        label_unidad = st.text_input("Etiqueta de unidad (ej. %, hab/km²):", "%")

    else:
        # Modo cálculo avanzado
        col_calc_a, col_calc_b = st.columns(2)
        with col_calc_a:
            col_n1 = st.text_input("Nombre Variable A:", "Variable A")
            col_n2 = st.text_input("Nombre Variable B:", "Variable B")
        with col_calc_b:
            operacion = st.selectbox("Operación a realizar:", [
                "Tasa: (A / B) * Multiplicador",
                "Dividir: (A / B)",
                "Multiplicar: (A * B)",
                "Diferencia porcentual: ((A - B) / B) * 100",
                "Suma simple: (A + B)"
            ])
            multiplicador = st.number_input("Multiplicador (K):", value=1000 if "Tasa" in operacion else 1)
        
        df_input = pd.DataFrame({
            'Comunidad': comunidades, 
            col_n1: [0.0]*len(comunidades),
            col_n2: [1.0]*len(comunidades)
        })
        
        edited_df = st.data_editor(df_input, use_container_width=True, hide_index=True)
        
        # --- LÓGICA DE CÁLCULO ---
        if "Tasa" in operacion:
            edited_df['Resultado_Final'] = (edited_df[col_n1] / edited_df[col_n2]) * multiplicador
            f_text = f"({col_n1} / {col_n2}) * {multiplicador}"
        elif "Dividir" in operacion:
            edited_df['Resultado_Final'] = edited_df[col_n1] / edited_df[col_n2]
            f_text = f"{col_n1} / {col_n2}"
        elif "Multiplicar" in operacion:
            edited_df['Resultado_Final'] = edited_df[col_n1] * edited_df[col_n2]
            f_text = f"{col_n1} * {col_n2}"
        elif "Diferencia" in operacion:
            edited_df['Resultado_Final'] = ((edited_df[col_n1] - edited_df[col_n2]) / edited_df[col_n2]) * 100
            f_text = f"(({col_n1} - {col_n2}) / {col_n2}) * 100"
        else:
            edited_df['Resultado_Final'] = edited_df[col_n1] + edited_df[col_n2]
            f_text = f"{col_n1} + {col_n2}"
            
        st.success(f"Fórmula aplicada: {f_text}")
        label_unidad = st.text_input("Unidad para la leyenda:", "Resultado")

    # --- 2. DISEÑO Y MAPA ---
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        titulo = st.text_input("Título del mapa:", "Mapa Temático")
        paleta = st.selectbox("Gama cromática:", ["Blues", "Reds", "YlOrBr", "Purples", "Greens"])
    with c2:
        st.info("Intervalos: 4 (Natural Breaks / Jenks)")

    if st.button("🎨 Generar Mapa"):
        merged = gdf.merge(edited_df, left_on="name", right_on="Comunidad")
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        merged.plot(column='Resultado_Final', 
                    cmap=paleta, 
                    scheme='NaturalBreaks', 
                    k=4, 
                    ax=ax, 
                    edgecolor='black', 
                    linewidth=0.5,
                    legend=True,
                    legend_kwds={'loc': 'lower right', 'title': label_unidad})

        ax.set_title(titulo, fontsize=20, pad=20)
        
        # Elementos cartográficos agrupados arriba a la izquierda
        ax.annotate('N', xy=(0.06, 0.95), xytext=(0.06, 0.88),
                    arrowprops=dict(facecolor='black', width=3, headwidth=10),
                    ha='center', va='center', fontsize=15, xycoords='axes fraction')
        
        ax.text(0.02, 0.82, "0 ________ 250 km\nEscala 1:10.000.000", 
                transform=ax.transAxes, fontsize=9, 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
        
        ax.axis('off')
        st.pyplot(fig)
