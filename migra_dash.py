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
            # Puedes agregar más estados y colores si es necesario
            # ej: "EN PROCESO": "lightcoral"
        }

        st.subheader("Gráfico de Barras Horizontal por ESTADO GX16 General")
        if 'ESTADO GX16' in df.columns:
            estado_counts = df['ESTADO GX16'].value_counts().sort_values() # Ya ordenado de menor a mayor cantidad
            total_estado = estado_counts.sum()
            porcentajes_mostrados = {}
            
            # Para invertir el orden y mostrar de mayor a menor (opcional, pero común en estos gráficos)
            # estado_counts = df['ESTADO GX16'].value_counts().sort_values(ascending=False)

            fig_estado = px.bar(estado_counts, x=estado_counts.values, y=estado_counts.index, orientation='h',
                                labels={'x': 'Cantidad', 'y': 'Estado GX16'},
                                title='Distribución por Estado GX16',
                                color=estado_counts.index,
                                color_discrete_map=colores_estados_gx16)
            
            fig_estado.update_layout(xaxis_title='Cantidad', yaxis_title='Estado GX16') # Asegura títulos de ejes

            for i, v in enumerate(estado_counts.values):
                estado = estado_counts.index[i]
                percent_individual = (v / total_estado) * 100 if total_estado > 0 else 0
                porcentaje_formateado = f'{percent_individual:.1f}'
                porcentajes_mostrados[estado] = float(porcentaje_formateado)
                fig_estado.add_annotation(x=v, y=estado, text=f'{porcentaje_formateado}% ({v})', # Añadido cantidad absoluta
                                          xref="x", yref="y", showarrow=False, xanchor='left', 
                                          font=dict(color="black")) # Mejor visibilidad del texto
            
            st.plotly_chart(fig_estado, use_container_width=True)

            avance_total_observacion = porcentajes_mostrados.get('YA NO SE UTILIZA', 0) + porcentajes_mostrados.get('COMPILADO', 0)
            st.markdown(f"<div style='text-align: center;'><span style='color:goldenrod;'>Avance Total (YA NO SE UTILIZA + COMPILADO):</span> {avance_total_observacion:.1f}%</div>", unsafe_allow_html=True)
        else:
            st.warning("La columna 'ESTADO GX16' no se encuentra en el DataFrame.")

        
        st.subheader("Ranking por MÓDULO y ESTADO GX16 (Ordenado por Cantidad Total)")
        if 'MODULO' in df.columns and 'ESTADO GX16' in df.columns:
            modulo_estado_counts = df.groupby(['MODULO', 'ESTADO GX16']).size().unstack(fill_value=0).stack().reset_index(name='Cantidad')
            
            # 1. Calcular la cantidad total por MÓDULO para determinar el orden
            total_cantidad_por_modulo = modulo_estado_counts.groupby('MODULO')['Cantidad'].sum().sort_values(ascending=False)
            
            # 2. Obtener la lista ordenada de MÓDULOS
            modulos_ordenados = total_cantidad_por_modulo.index.tolist()
            
            fig_modulo_estado = px.bar(modulo_estado_counts, x='MODULO', y='Cantidad', color='ESTADO GX16',
                                       labels={'Cantidad': 'Cantidad', 'MODULO': 'Módulo', 'ESTADO GX16': 'Estado GX16'},
                                       title='Ranking por Módulo y Estado GX16 (Ordenado por Cantidad Total)',
                                       color_discrete_map=colores_estados_gx16,
                                       category_orders={'MODULO': modulos_ordenados}) # Aplicar orden
            st.plotly_chart(fig_modulo_estado, use_container_width=True, height=600)
        else:
            st.warning("Las columnas 'MODULO' o 'ESTADO GX16' no se encontraron para crear el ranking por módulo.")

        st.subheader("Ranking por Responsable y ESTADO GX16 (Ordenado por Cantidad Total)")
        if 'Responsable' in df.columns and 'ESTADO GX16' in df.columns:
            responsable_estado_counts = df.groupby(['Responsable', 'ESTADO GX16']).size().unstack(fill_value=0).stack().reset_index(name='Cantidad')
            
            # 1. Calcular la cantidad total por Responsable para determinar el orden
            total_cantidad_por_responsable = responsable_estado_counts.groupby('Responsable')['Cantidad'].sum().sort_values(ascending=False)
            
            # 2. Obtener la lista ordenada de Responsables
            responsables_ordenados = total_cantidad_por_responsable.index.tolist()
            
            fig_responsable_estado = px.bar(responsable_estado_counts, x='Responsable', y='Cantidad', color='ESTADO GX16',
                                            labels={'Cantidad': 'Cantidad', 'Responsable': 'Responsable', 'ESTADO GX16': 'Estado GX16'},
                                            title='Ranking por Responsable y Estado GX16 (Ordenado por Cantidad Total)',
                                            color_discrete_map=colores_estados_gx16,
                                            category_orders={'Responsable': responsables_ordenados}) # Aplicar orden
            st.plotly_chart(fig_responsable_estado, use_container_width=True, height=600)
        else:
            st.warning("Las columnas 'Responsable' o 'ESTADO GX16' no se encontraron para crear el ranking por responsable.")

        st.subheader("Cantidad de Estados GX16 por ESTADO (Ordenado por Cantidad Total)") # Título modificado para claridad
        if 'ESTADO' in df.columns and 'ESTADO GX16' in df.columns:
            # Data preparation
            estado_gx16_counts_df = df.groupby(['ESTADO', 'ESTADO GX16']).size().unstack(fill_value=0)
            
            # Calcular totales por 'ESTADO' para ordenar
            estado_gx16_counts_df['Total'] = estado_gx16_counts_df.sum(axis=1)
            estado_gx16_counts_df_sorted = estado_gx16_counts_df.sort_values(by='Total', ascending=False)
            
            # Crear figura
            fig_estado_gx16 = go.Figure()
            
            # Iterar sobre las columnas de ESTADO GX16 (excepto la columna 'Total' que acabamos de añadir)
            # Asegurándonos de que los estados tengan colores definidos
            estados_gx16_presentes = [col for col in estado_gx16_counts_df_sorted.columns if col != 'Total']

            for estado_gx16_col in estados_gx16_presentes:
                fig_estado_gx16.add_trace(go.Bar(
                    name=estado_gx16_col, 
                    x=estado_gx16_counts_df_sorted.index, 
                    y=estado_gx16_counts_df_sorted[estado_gx16_col],
                    text=estado_gx16_counts_df_sorted[estado_gx16_col].apply(lambda x: x if x > 0 else ''), # Mostrar valor solo si es > 0
                    textposition='inside',
                    marker_color=colores_estados_gx16.get(estado_gx16_col, 'lightgrey') # Usar gris claro para no definidos
                ))
            
            fig_estado_gx16.update_layout(
                barmode='stack', 
                title='Cantidad de Estados GX16 por ESTADO (Ordenado por Cantidad Total de Estados GX16)',
                xaxis_title='ESTADO (Entidad principal)', 
                yaxis_title='Cantidad Acumulada de Estados GX16',
                legend_title_text='Estado GX16'
            )
            st.plotly_chart(fig_estado_gx16, use_container_width=True)
        else:
            st.warning("Las columnas 'ESTADO' o 'ESTADO GX16' no se encontraron para crear el gráfico de estados.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo Excel: {e}")
else:
    st.info("Por favor, carga un archivo Excel desde la barra lateral para visualizar los datos.")