import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Agregar la carpeta src al path para importar correctamente los módulos del proyecto
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# Importación real de los módulos lógicos
try:
    from classifiers.sistema_hibrido import SistemaHibridoSoporte
    from classifiers.astar import astar_soporte_ti, START_STATE, GOAL_STATE
    from classifiers.minimax import best_move, board as minimax_board
    from classifiers.evaluacion_modelo import ejecutar_validacion
    MODULOS_CARGADOS = True
except ImportError as e:
    MODULOS_CARGADOS = False

# Configuración de la página
st.set_page_config(
    page_title="Dashboard - Asistente de Soporte TI Híbrido",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (textos negros en la barra lateral)
st.markdown("""
    <style>
    /* Centrar todos los títulos principales */
    h1, h2, h3 {
        text-align: center !important;
    }

    /* Forzar textos en color negro dentro de la barra lateral */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #111111 !important;
    }

    /* Ajustar color del texto de la caja informativa inferior en la barra lateral */
    [data-testid="stSidebar"] [data-testid="stInfo"] {
        color: #111111 !important;
    }
    </style>
""", unsafe_allow_html=True)

AUDIT_LOG_PATH = BASE_DIR / "artifacts" / "audit.log"

# --- Barra Lateral ---
st.sidebar.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=80)
st.sidebar.title("Panel de Control TI")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegación",
    ["📊 Resumen Ejecutivo", "📈 Matriz de Confusión", "🔍 Sistema Híbrido & RAG", "⚙️ Planificador A* & Minimax", "📜 Trazas de Auditoría"]
)

st.sidebar.markdown("---")
st.sidebar.info("**Institución:** ETITC - 10º Semestre\n\n**Autores:** Marco Molina & Daniel Daza")

# --- 1. Resumen Ejecutivo ---
if menu == "📊 Resumen Ejecutivo":
    st.title("🚀 Dashboard General del Asistente de Soporte TI")
    st.markdown("Monitoreo en tiempo real de los componentes lógicos, modelos de machine learning y flujos del sistema híbrido.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Accuracy Modelo Base", value="92.1%", delta="Validación Tickets")
    with col2:
        st.metric(label="Base de Conocimiento", value="30 Casos", delta="Activo (Semana 05)")
    with col3:
        st.metric(label="Algoritmo A*", value="Costo Min: 12", delta="6 Pasos óptimos")
    with col4:
        st.metric(label="Estrategia Minimax", value="Posición 6", delta="Adversarial")

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📌 Distribución por Categorías Técnicas")
        data_cat = {
            "Categoría": ["Hardware", "Red", "Seguridad", "Rendimiento", "Almacenamiento", "Software"],
            "Casos Registrados": [6, 3, 3, 2, 1, 1]
        }
        df_cat = pd.DataFrame(data_cat)
        st.bar_chart(df_cat.set_index("Categoría"))
        
    with col_b:
        st.subheader("🛠️ Estado de Integración de Módulos")
        st.success("✅ Validación y Matriz de Confusión (Semana 03) - Operativo")
        st.success("✅ Planificador A* y Minimax (Semana 04) - Operativo")
        st.success("✅ Sistema Híbrido y RAG (Semana 05) - Operativo")
        st.success("✅ Motor de Auditoría y Trazas - Registrando")

# --- 2. Matriz de Confusión ---
elif menu == "📈 Matriz de Confusión":
    st.title("📉 Validación del Modelo Base y Métricas")
    st.markdown("Resultados de la evaluación de rendimiento del clasificador base sobre el conjunto de pruebas de soporte TI.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Muestras de Entrenamiento", value="112")
        st.metric(label="Muestras de Prueba", value="38")
    with col2:
        st.metric(label="Accuracy Global", value="92.1% (0.921)")
    
    st.markdown("---")
    st.subheader("Matriz de Confusión Numérica")
    
    if MODULOS_CARGADOS:
        try:
            cm = ejecutar_validacion()
            df_matriz = pd.DataFrame(cm)
            st.dataframe(df_matriz, use_container_width=True)
            st.info("La matriz de confusión demuestra una alta tasa de aciertos con mínima dispersión en las clases evaluadas.")
        except Exception as e:
            st.error(f"Error al ejecutar la validación del modelo: {e}")
    else:
        st.warning("Módulos no disponibles para generar la matriz en tiempo real.")

# --- 3. Sistema Híbrido & RAG (Dinámico) ---
elif menu == "🔍 Sistema Híbrido & RAG":
    st.title("🧠 Simulador de Sistema Híbrido (Reglas + TF-IDF)")
    st.markdown("Consulta la base de conocimiento en tiempo real utilizando similitud coseno y reglas lógicas expertas.")

    query = st.text_input("Escribe un reporte de ticket de soporte:", value="Disco lleno", key="query_input")
    
    if st.button("Ejecutar Análisis Híbrido"):
        if MODULOS_CARGADOS:
            sistema = SistemaHibridoSoporte()
            resultado = sistema.procesar(query)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📋 Resultados del Motor")
                st.info(f"**Reglas Activadas:** `{resultado['reglas']}`")
                st.warning(f"**Clase Predicha (ML):** {resultado['clase']}")
                st.metric(label="Similitud Coseno", value=f"{resultado['similitud']:.4f}")
            with col2:
                st.markdown("### 📄 Evidencia Recuperada (RAG)")
                st.success(f"{resultado['evidencia']}")
        else:
            st.error("No se pudieron cargar los módulos de Python desde la carpeta `src/`.")

# --- 4. Planificador A* & Minimax ---
elif menu == "⚙️ Planificador A* & Minimax":
    st.title("🤖 Optimización y Decisiones Adversariales")
    
    tab1, tab2 = st.tabs(["Planificador A*", "Minimax (Recursos)"])
    
    with tab1:
        st.subheader("Secuencia Óptima de Resolución de Soporte (A*)")
        if MODULOS_CARGADOS:
            ruta, costo_total = astar_soporte_ti(START_STATE, GOAL_STATE)
            st.text(f"Estado Inicial: {START_STATE} -> Estado Meta: {GOAL_STATE} | Costo Mínimo: {costo_total}")
            
            pasos_lista = []
            for idx, (orig, dest, desc, c) in enumerate(ruta, 1):
                pasos_lista.append({
                    "Paso": idx,
                    "Acción": desc,
                    "Costo": c,
                    "Transición": f"{orig} -> {dest}"
                })
            st.table(pd.DataFrame(pasos_lista))
        else:
            st.warning("Módulo A* no disponible temporalmente.")
        
    with tab2:
        st.subheader("Minimax - Selección de Posición Estratégica")
        if MODULOS_CARGADOS:
            st.code(f"Tablero actual de recursos: {minimax_board}", language="python")
            mejor_pos = best_move(minimax_board)
            st.success(f"Mejor posición estratégica seleccionada por Minimax: **{mejor_pos}**")
        else:
            st.warning("Módulo Minimax no disponible temporalmente.")

# --- 5. Trazas de Auditoría ---
elif menu == "📜 Trazas de Auditoría":
    st.title("📝 Registro de Auditoría del Sistema (audit.log)")
    st.markdown("Historial persistente de eventos generados por el orquestador `main.py`.")

    if AUDIT_LOG_PATH.exists():
        with open(AUDIT_LOG_PATH, "r", encoding="latin-1", errors="ignore") as f:
            logs = f.readlines()
        
        log_text = "".join(logs)
        st.text_area("Consola de Trazas", log_text, height=400)
    else:
        st.warning("No se encontró el archivo de auditoría en `artifacts/audit.log`. Ejecuta `python src/main.py` para generarlo.")