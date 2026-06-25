import streamlit as st
from supabase import create_client
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE CONEXIÓN CON SUPABASE
# ==========================================
# ⚠️ ASEGÚRATE DE COPIARLOS BIEN, SIN ESPACIOS EN BLANCO AL INICIO O AL FINAL
URL_SUPABASE = "https://usauhbsgmstihwllktur.supabase.co"  
KEY_SUPABASE = "sb_secret_i1Gwo0wSOfxXPy2pwzXXhg_zgzY-fMp"  

@st.cache_resource
def init_connection():
    return create_client(URL_SUPABASE, KEY_SUPABASE)

supabase = init_connection()

# ==========================================
# INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================
st.set_page_config(page_title="CRUD Alumnos - Supabase", layout="wide")
st.title("📚 Sistema CRUD de Gestión de Alumnos")

opcion = st.sidebar.selectbox(
    "Selecciona una Operación:",
    ["Consultar Alumnos (Read)", "Insertar Alumno (Create)", "Actualizar Alumno (Update)", "Eliminar Alumno (Delete)"]
)

# ==========================================
# 1. OPERACIÓN: CONSULTAR (READ)
# ==========================================
if opcion == "Consultar Alumnos (Read)":
    st.subheader("📋 Lista de Alumnos Registrados")
    try:
        response = supabase.table("ALUMNOS").select("*").execute()
        datos = response.data
        if datos:
            df = pd.DataFrame(datos)
            columnas_ordenadas = ["id", "DNI", "NOMBRE", "APELLIDO_PAT", "APELLIDO_MAT", "SEXO", "EDAD", "created_at"]
            df = df[columnas_ordenadas]
            
            # Mostrar la tabla de datos arriba
            st.dataframe(df, use_container_width=True)
            st.metric(label="Total de Alumnos", value=len(datos))
            
            st.markdown("---")
            st.subheader("📊 Visualización Gráfica de los Datos")
            
            # Importamos matplotlib para los gráficos avanzados
            import matplotlib.pyplot as plt
            
            # Crear dos columnas en la página web para poner los gráficos lado a lado
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.write("**Distribución de Alumnos por Sexo (Círculo)**")
                conteo_sexo = df["SEXO"].value_counts()
                
                # Configurar el gráfico circular (Pie Chart)
                fig1, ax1 = plt.subplots(figsize=(5, 5))
                # Colores bonitos: Azul para M, Rosado/Lila para F
                colores_sexo = ['#3498db', '#e74c3c'] if conteo_sexo.index[0] == 'M' else ['#e74c3c', '#3498db']
                
                ax1.pie(conteo_sexo, labels=conteo_sexo.index, autopct='%1.1f%%', startangle=90, colors=colores_sexo)
                ax1.axis('equal')  # Asegura que el gráfico sea un círculo perfecto
                st.pyplot(fig1)
                
            with col_graf2:
                st.write("**Cantidad de Alumnos por Edades (Barras)**")
                # Agrupamos cuántos alumnos hay por cada edad exacta
                conteo_edad = df["EDAD"].value_counts().sort_index()
                
                # Configurar el gráfico de barras (Bar Chart)
                fig2, ax2 = plt.subplots(figsize=(5, 5))
                ax2.bar(conteo_edad.index.astype(str), conteo_edad.values, color='#2ecc71')
                ax2.set_xlabel("Edad")
                ax2.set_ylabel("Cantidad de Alumnos")
                
                # Forzar que el eje Y muestre solo números enteros
                ax2.yaxis.get_major_locator().set_params(integer=True)
                
                st.pyplot(fig2)

        else:
            st.info("La tabla está vacía. Registra un alumno en la pestaña 'Insertar Alumno'.")
    except Exception as e:
        st.error(f"Error al consultar o graficar: {e}")

# ==========================================
# 2. OPERACIÓN: INSERTAR (CREATE)
# ==========================================
elif opcion == "Insertar Alumno (Create)":
    st.subheader("➕ Registrar un Nuevo Alumno")
    
    with st.form("form_insertar", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            dni = st.text_input("DNI (Obligatorio):", max_chars=8)
            nombre = st.text_input("Nombre(s):")
            sexo = st.selectbox("Sexo:", ["M", "F"])
        with col2:
            apellido_pat = st.text_input("Apellido Paterno:")
            apellido_mat = st.text_input("Apellido Materno:")
            edad = st.number_input("Edad:", min_value=0, max_value=120, value=20, step=1)
            
        boton_guardar = st.form_submit_button("Guardar Registro")
        
        if boton_guardar:
            if not dni or not nombre or not apellido_pat:
                st.warning("⚠️ Por favor completa los campos obligatorios (DNI, Nombre y Apellido Paterno).")
            else:
                nuevo_alumno = {
                    "DNI": str(dni).strip(),
                    "NOMBRE": str(nombre).strip(),
                    "APELLIDO_PAT": str(apellido_pat).strip(),
                    "APELLIDO_MAT": str(apellido_mat).strip() if apellido_mat else None,
                    "SEXO": str(sexo),
                    "EDAD": int(edad)
                }
                
                try:
                    supabase.table("ALUMNOS").insert(nuevo_alumno).execute()
                    st.success(f"🎉 ¡Alumno {nombre} {apellido_pat} registrado con éxito!")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# ==========================================
# 3. OPERACIÓN: ACTUALIZAR (UPDATE)
# ==========================================
elif opcion == "Actualizar Alumno (Update)":
    st.subheader("🔄 Modificar Datos de un Alumno")
    dni_buscar = st.text_input("Ingresa el DNI del alumno que deseas modificar:", max_chars=8)
    if dni_buscar:
        response = supabase.table("ALUMNOS").select("*").eq("DNI", dni_buscar.strip()).execute()
        alumno = response.data
        if alumno:
            datos_alumno = alumno[0]
            with st.form("form_actualizar"):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_nombre = st.text_input("Nombre(s):", value=datos_alumno["NOMBRE"])
                    nuevo_sexo = st.selectbox("Sexo:", ["M", "F"], index=0 if datos_alumno["SEXO"] == "M" else 1)
                with col2:
                    nuevo_pat = st.text_input("Apellido Paterno:", value=datos_alumno["APELLIDO_PAT"])
                    nuevo_mat = st.text_input("Apellido Materno:", value=datos_alumno["APELLIDO_MAT"] if datos_alumno["APELLIDO_MAT"] else "")
                    nueva_edad = st.number_input("Edad:", min_value=0, max_value=120, value=int(datos_alumno["EDAD"]) if datos_alumno["EDAD"] else 20)
                
                boton_actualizar = st.form_submit_button("Actualizar Cambios")
                if boton_actualizar:
                    datos_nuevos = {
                        "NOMBRE": nuevo_nombre.strip(),
                        "APELLIDO_PAT": nuevo_pat.strip(),
                        "APELLIDO_MAT": nuevo_mat.strip(),
                        "SEXO": nuevo_sexo,
                        "EDAD": int(nueva_edad)
                    }
                    supabase.table("ALUMNOS").update(datos_nuevos).eq("DNI", dni_buscar.strip()).execute()
                    st.success("✨ ¡Datos del alumno actualizados correctamente!")
        else:
            st.error("No se encontró ningún alumno.")

# ==========================================
# 4. OPERACIÓN: ELIMINAR (DELETE)
# ==========================================
elif opcion == "Eliminar Alumno (Delete)":
    st.subheader("❌ Dar de Baja a un Alumno")
    dni_eliminar = st.text_input("Ingresa el DNI del alumno que deseas ELIMINAR:", max_chars=8)
    if dni_eliminar:
        response = supabase.table("ALUMNOS").select("*").eq("DNI", dni_eliminar.strip()).execute()
        alumno = response.data
        if alumno:
            datos_alumno = alumno[0]
            st.warning(f"¿Estás seguro de eliminar a: **{datos_alumno['NOMBRE']} {datos_alumno['APELLIDO_PAT']}**?")
            if st.button("Confirmar Eliminación", type="primary"):
                supabase.table("ALUMNOS").delete().eq("DNI", dni_eliminar.strip()).execute()
                st.success("🗑️ El alumno ha sido eliminado correctamente.")
        else:
            st.error("No se encontró ningún alumno.")
