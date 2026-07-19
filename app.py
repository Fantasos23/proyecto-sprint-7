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

# 3. Carga y Procesamiento de Datos (Tu lógica para leer 'archivo_limpio_final.csv')
@st.cache_data
def procesar_datos_ecommerce():
    df_sales = pd.read_csv('archivo_limpio_final.csv')
    
    # Filtro estricto: Solo transacciones facturadas con éxito y sin órdenes duplicadas
    df_sales = df_sales[df_sales['Status raw value (temporary)'].str.lower() == 'invoiced'].drop_duplicates(subset=['Order'], keep='first')
    
    # Asegurar formato de fecha correcto
    df_sales['Creation Date'] = pd.to_datetime(df_sales['Creation Date'])
    df_sales['Year'] = df_sales['Creation Date'].dt.year
    df_sales['Month_Num'] = df_sales['Creation Date'].dt.month
    
    # DETERMINAR CLIENTES NUEVOS VS RECURRENTES
    df_sales['First_Purchase_Date'] = df_sales.groupby('Client Document')['Creation Date'].transform('min')
    df_sales['Tipo_Cliente'] = np.where(df_sales['Creation Date'] == df_sales['First_Purchase_Date'], 'Nuevo', 'Recurrente')
    
    # CLASIFICACIÓN DE ORIGEN (UTMs)
    df_sales['UtmMedium'] = df_sales['UtmMedium'].astype(str).str.lower().str.strip()
    palabras_pauta_reales = ['cpc', 'cpa', 'cpa+', 'paid', 'facebook', 'conversion', 'trafico']
    
    df_sales['Origen_Orden'] = np.where(
        df_sales['UtmMedium'].isin(['nan', '', 'none', 'null']), 'Orgánico',
        np.where(df_sales['UtmMedium'].str.contains('|'.join(palabras_pauta_reales)), 'Anuncios (Pauta)', 'Orgánico')
    )
    
    # Filtrar únicamente primer semestre de 2026 (Ene - Jun)
    df_2026 = df_sales[(df_sales['Year'] == 2026) & (df_sales['Month_Num'] <= 6)].copy()
    
    # Mapeo estético de meses
    meses_espanol = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio'}
    df_2026['Mes'] = df_2026['Month_Num'].map(meses_espanol)
    
    return df_2026

# Cargar los datos de forma segura
try:
    df_ecommerce = procesar_datos_ecommerce()
except FileNotFoundError:
    st.error("Por favor, asegúrate de que el archivo 'archivo_limpio_final.csv' esté guardado en la raíz de la carpeta del proyecto.")
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

# Lógica para desplegar el Histograma de Frecuencia
if mostrar_histograma:
    st.write("### 🍊 Histograma de Distribución de Frecuencia")
    df_hist_data = df_ecommerce.groupby(['Mes', 'Creation Date']).agg(
        Pedidos_Diarios=('Order', 'nunique')
    ).reset_index()
    
    fig_histograma = px.histogram(
        df_hist_data, x="Pedidos_Diarios",
        title="Frecuencia de Volumen de Pedidos Diarios en el Ecommerce",
        labels={"Pedidos_Diarios": "Cantidad de Pedidos en un Día", "count": "Frecuencia (Días)"},
        color_discrete_sequence=['#e6550d'], nbins=15
    )
    fig_histograma.update_layout(plot_bgcolor='white', xaxis=dict(showgrid=True, gridcolor='#EAEAEA'), yaxis=dict(showgrid=True, gridcolor='#EAEAEA'))
    st.plotly_chart(fig_histograma, use_container_width=True)