import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# 1. Configuración de la página web
st.set_page_config(page_title="Estado de Ecommerce 2026", page_icon="🛍️", layout="wide")

# 2. Encabezado principal
st.header('🛍️ Estado de Ecommerce 2026')
st.markdown("""
Bienvenido al cuadro de mando interactivo. Esta aplicación procesa el histórico unificado de ventas 
para analizar la composición de clientes y la atribución de canales en tiempo real.
""")

# # 3. Carga y Procesamiento de Datos Optimizado para Evitar Límites de RAM en Render
@st.cache_data
def procesar_datos_ecommerce():
    # Cargamos directamente el archivo optimizado desde la carpeta notebooks
    df_2026 = pd.read_csv('notebooks/datos_web_dashboard.csv')
    return df_2026

# Cargar los datos de forma segura
try:
    df_ecommerce = procesar_datos_ecommerce()
except FileNotFoundError:
    st.error("Por favor, asegúrate de que el archivo 'datos_web_dashboard.csv' esté dentro de la carpeta 'notebooks'.")
    st.stop()

# --- 4. SECCIÓN DE COMPONENTES INTERACTIVOS CON CASILLAS DE VERIFICACIÓN (DESAFÍO OPCIONAL) ---
st.write('---')
st.subheader("📊 Panel de Visualización Interactivo")
st.markdown("""
Selecciona las casillas de verificación para activar, combinar o desactivar los gráficos en tiempo real.
""")

# Crear las casillas de verificación
mostrar_barras = st.checkbox('Ver Gráfico de Barras: Composición Mensual de Clientes (Nuevos vs. Recurrentes)')
mostrar_scatter = st.checkbox('Ver Gráfico de Dispersión: Relación entre Clientes Únicos y Órdenes Totales')
mostrar_histograma = st.checkbox('Ver Histograma de Frecuencia: Distribución de Pedidos Diarios')

st.write('---')

# Lógica para desplegar el Gráfico de Barras Apiladas
if mostrar_barras:
    st.write("### 🟦 Composición Mensual de Clientes - 2026")
    df_clientes_mes = df_ecommerce.groupby(['Mes', 'Tipo_Cliente'])['Client Document'].nunique().reset_index()
    orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio']
    df_clientes_mes['Mes'] = pd.Categorical(df_clientes_mes['Mes'], categories=orden_meses, ordered=True)
    df_clientes_mes = df_clientes_mes.sort_values('Mes')
    
    fig_barras = px.bar(
        df_clientes_mes, x="Mes", y="Client Document", color="Tipo_Cliente",
        title="Evolución de Clientes Nuevos vs. Recurrentes (2026)",
        labels={"Client Document": "Clientes Únicos", "Tipo_Cliente": "Tipo de Cliente"},
        color_discrete_map={'Nuevo': '#1f77b4', 'Recurrente': '#2ca02c'},
        text_auto=True
    )
    fig_barras.update_layout(barmode='stack', plot_bgcolor='white', xaxis_title="Mes", yaxis_title="Clientes Únicos")
    st.plotly_chart(fig_barras, use_container_width=True)

# Lógica para desplegar el Gráfico de Dispersión
if mostrar_scatter:
    st.write("### 🟢 Relación de Compra por Segmento")
    df_scatter_data = df_ecommerce.groupby(['Mes', 'Tipo_Cliente']).agg(
        Clientes_Unicos=('Client Document', 'nunique'),
        Ordenes_Totales=('Order', 'nunique')
    ).reset_index()
    
    orden_meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio']
    df_scatter_data['Mes'] = pd.Categorical(df_scatter_data['Mes'], categories=orden_meses, ordered=True)
    df_scatter_data = df_scatter_data.sort_values('Mes')
    
    fig_scatter = px.scatter(
        df_scatter_data, x="Clientes_Unicos", y="Ordenes_Totales", color="Tipo_Cliente",
        hover_data=["Mes"], title="Frecuencia de Compra: Clientes Únicos vs. Órdenes Totales (2026)",
        labels={"Clientes_Unicos": "Clientes Únicos", "Ordenes_Totales": "Órdenes Totales", "Tipo_Cliente": "Segmento"},
        color_discrete_map={'Nuevo': '#1f77b4', 'Recurrente': '#2ca02c'},
        size="Ordenes_Totales", size_max=25
    )
    fig_scatter.update_layout(plot_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='#EAEAEA'), yaxis=dict(showgrid=True, gridcolor='#EAEAEA'))
    st.plotly_chart(fig_scatter, use_container_width=True)

# 3. Lógica para el Histograma de Frecuencia (Recompra de Clientes)
if mostrar_histograma:
    st.write("### 🍊 Histograma de Frecuencia de Recompra por Cliente")
    st.markdown("""
    Este gráfico analiza el comportamiento de fidelización: muestra cuántos pedidos acumuló cada cliente único 
    durante el período filtrado, permitiendo identificar el volumen de usuarios que generaron recompra.
    """)
    
    # Agrupar por cliente para contar cuántas órdenes únicas realizó cada uno
    df_recompra_cliente = df_ecommerce.groupby('Client Document').agg(
        Total_Pedidos=('Order', 'nunique')
    ).reset_index()
    
    # Crear el Histograma interactivo con Plotly Express
    fig_histograma = px.histogram(
        df_recompra_cliente, 
        x="Total_Pedidos",
        title="Distribución de Pedidos por Cliente Único",
        labels={"Total_Pedidos": "Número de Pedidos Realizados", "count": "Cantidad de Clientes"},
        color_discrete_sequence=['#e6550d'],
        nbins=10
    )
    
    # Ajustes estéticos para que se vea impecable
    fig_histograma.update_layout(
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#EAEAEA', dtick=1), # dtick=1 fuerza a mostrar números enteros (1, 2, 3...)
        yaxis=dict(showgrid=True, gridcolor='#EAEAEA')
    )
    
    st.plotly_chart(fig_histograma, use_container_width=True)