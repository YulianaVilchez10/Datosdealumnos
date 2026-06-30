import streamlit as st
from supabase import create_client
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE CONEXIÓN CON SUPABASE
# ==========================================
URL_SUPABASE = "https://usauhbsgmstihwllktur.supabase.co"  
KEY_SUPABASE = "sb_secret_i1Gwo0wSOfxXPy2pwzXXhg_zgzY-fMp"  
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# Configuración de la página web
st.set_page_config(page_title="Dashboard Industrial - IIoT", layout="wide")

st.title("🏭 Panel de Control de Cajas en Tiempo Real (IIoT)")
st.subheader("Monitoreo de fajas transportadoras en la nube")

# Botón para actualizar los datos manualmente
if st.button("🔄 Actualizar Datos del PLC"):
    st.rerun()

# 1. Descargar datos desde Supabase
try:
    respuesta = supabase.table("cajas").select("*").order("fecha_llegada", descending=True).execute()
    datos = respuesta.data
    
    if datos:
        # Convertir los datos de la nube a un DataFrame de Pandas
        df = pd.DataFrame(datos)
        
        # --- SECCIÓN 1: TARJETAS DE MÉTRICAS (KPIs) ---
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Total Cajas Procesadas", value=len(df))
        with col2:
            peso_total = round(df["peso_kg"].sum(), 1)
            st.metric(label="Peso Total Despachado", value=f"{peso_total} kg")
        with col3:
            # Calcular porcentaje de aprobados
            aprobados = len(df[df["estado_calidad"] == "Aprobado"])
            porcentaje_ok = round((aprobados / len(df)) * 100, 1) if len(df) > 0 else 0
            st.metric(label="Eficiencia de Calidad (OK)", value=f"{porcentaje_ok} %")
        with col4:
            tiempo_promedio = round(df["duracion_proceso_seg"].mean(), 2)
            st.metric(label="Tiempo Promedio en Faja", value=f"{tiempo_promedio} seg")
            
        st.markdown("---")
        
        # --- SECCIÓN 2: GRÁFICAS INDUSTRIALES ---
        st.subheader("📊 Análisis de Producción")
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("**Cantidad de Cajas por Tamaño**")
            conteo_tamanos = df["tamano"].value_counts()
            st.bar_chart(conteo_tamanos)
            
        with col_graf2:
            st.markdown("**Cajas Procesadas por Línea de Faja**")
            conteo_lineas = df["id_linea"].value_counts()
            st.bar_chart(conteo_lineas)
            
        st.markdown("---")
        
        # --- SECCIÓN 3: CUADRO DE DATOS GENERAL ---
        st.subheader("📋 Registro Histórico de Cajas (Últimos movimientos)")
        # Reordenamos las columnas para que se vea más estético en la web
        df_mostrar = df[["id", "codigo_barras", "tamano", "peso_kg", "estado_calidad", "id_linea", "duracion_proceso_seg", "fecha_llegada"]]
        st.dataframe(df_mostrar, use_container_width=True)
        
    else:
        st.info("La tabla está vacía. Enciende tu programa de Python para registrar las primeras cajas.")

except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
