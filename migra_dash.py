import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página para usar Wide mode
st.set_page_config(layout="wide")

st.title("Dashboard desde archivo Excel")

with st.sidebar:
    st.header("Cargar archivo")
    uploaded_file = st.file_uploader("Seleccionar archivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("Datos cargados:")
        st.dataframe(df, height=400, use_container_width=True)

        # --- Definir diccionario de colores PERSONALIZADO para los estados GX16 ---
        colores_estados_gx16 = {
            "COMPILADO": "goldenrod",
            "PENDIENTE": "mediumaquamarine",
            "YA NO SE UTILIZA": "plum",
        }

        # Suponiendo que tienes un DataFrame llamado 'df' y un diccionario 'colores_estados_gx16' definidos previamente

        st.subheader("Gráfico de Barras Horizontal por ESTADO GX16 General")
        if 'ESTADO GX16' in df.columns:
            estado_counts = df['ESTADO GX16'].value_counts().sort_values()
            total_estado = estado_counts.sum()
            porcentajes_mostrados = {}
            fig_estado = px.bar(estado_counts, x=estado_counts.values, y=estado_counts.index, orientation='h',
                                labels={'x': 'Cantidad', 'y': 'Estado GX16'},
                                title='Distribución por Estado GX16',
                                color=estado_counts.index,
                                color_discrete_map=colores_estados_gx16)
            for i, v in enumerate(estado_counts.values):
                estado = estado_counts.index[i]
                percent_individual = (v / total_estado) * 100
                porcentaje_formateado = f'{percent_individual:.1f}'
                porcentajes_mostrados[estado] = float(porcentaje_formateado)
                fig_estado.add_annotation(x=v, y=estado, text=f'{porcentaje_formateado}%',
                                            xref="x", yref="y", showarrow=False, xanchor='left')
            st.plotly_chart(fig_estado, use_container_width=True)

            # Cálculo del porcentaje total de "YA NO SE UTILIZA" y "COMPILADO" sumando los valores formateados
            avance_total_observacion = porcentajes_mostrados.get('YA NO SE UTILIZA', 0) + porcentajes_mostrados.get('COMPILADO', 0)

            # Mostrar la información al pie del gráfico con el texto resaltado y centrado (alternativa)
            st.markdown(f"<div style='text-align: center;'><span style='color:goldenrod;'>Avance Total (YA NO SE UTILIZA + COMPILADO):</span> {avance_total_observacion:.1f}%</div>", unsafe_allow_html=True)

        else:
            st.warning("La columna 'ESTADO GX16' no se encuentra en el DataFrame.")

            
        st.subheader("Ranking por MÓDULO y ESTADO GX16")
        if 'MODULO' in df.columns and 'ESTADO GX16' in df.columns:
            modulo_estado_counts = df.groupby(['MODULO', 'ESTADO GX16']).size().unstack(fill_value=0).stack().reset_index(name='Cantidad')
            fig_modulo_estado = px.bar(modulo_estado_counts, x='MODULO', y='Cantidad', color='ESTADO GX16',
                                       labels={'Cantidad': 'Cantidad', 'MODULO': 'Módulo', 'ESTADO GX16': 'Estado GX16'},
                                       title='Ranking por Módulo y Estado GX16',
                                       color_discrete_map=colores_estados_gx16)
            st.plotly_chart(fig_modulo_estado, use_container_width=True, height=600)                    
        else:
            st.warning("Las columnas 'MODULO' o 'ESTADO GX16' no se encontraron para crear el ranking por módulo.")

        st.subheader("Ranking por Responsable y ESTADO GX16")
        if 'Responsable' in df.columns and 'ESTADO GX16' in df.columns:
            responsable_estado_counts = df.groupby(['Responsable', 'ESTADO GX16']).size().unstack(fill_value=0).stack().reset_index(name='Cantidad')
            fig_responsable_estado = px.bar(responsable_estado_counts, x='Responsable', y='Cantidad', color='ESTADO GX16',
                                            labels={'Cantidad': 'Cantidad', 'Responsable': 'Responsable', 'ESTADO GX16': 'Estado GX16'},
                                            title='Ranking por Responsable y Estado GX16',
                                            color_discrete_map=colores_estados_gx16)
            st.plotly_chart(fig_responsable_estado, use_container_width=True, height=600)
        else:
            st.warning("Las columnas 'Responsable' o 'ESTADO GX16' no se encontraron para crear el ranking por responsable.")

        # --- Nuevo gráfico de barras apiladas: Cantidad de Estados GX16 por ESTADO ---
        st.subheader("Cantidad de Estados GX16 por ESTADO")
        if 'ESTADO' in df.columns and 'ESTADO GX16' in df.columns:
            estado_gx16_counts = df.groupby(['ESTADO', 'ESTADO GX16']).size().unstack(fill_value=0)
            fig_estado_gx16 = go.Figure(data=[
                go.Bar(name=estado, x=estado_gx16_counts.index, y=estado_gx16_counts[estado], text=estado_gx16_counts[estado],
                       textposition='inside', marker_color=colores_estados_gx16.get(estado, 'gray'))
                for estado in estado_gx16_counts.columns
            ])
            fig_estado_gx16.update_layout(barmode='stack', title='Cantidad de Estados GX16 por Estado',
                                           xaxis_title='Estado', yaxis_title='Cantidad')
            st.plotly_chart(fig_estado_gx16, use_container_width=True)
        else:
            st.warning("Las columnas 'ESTADO' o 'ESTADO GX16' no se encontraron para crear el gráfico de estados.")

    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo Excel: {e}")
else:
    st.info("Por favor, carga un archivo Excel desde la barra lateral para visualizar los datos.")