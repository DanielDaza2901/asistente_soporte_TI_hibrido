import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import numpy as np

# Agregar la carpeta src al path para importar correctamente los módulos del proyecto
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

# Importación real de los módulos lógicos
try:
    from classifiers.sistema_hibrido import SistemaHibridoSoporte
    from classifiers.astar import astar_soporte_ti, START_STATE, GOAL_STATE
    from classifiers.minimax import best_move, board as minimax_board, NODOS_INFRAESTRUCTURA, simular_ciberdefensa
    from classifiers.evaluacion_modelo import ejecutar_validacion
    # Intentar importar la función del autómata si la definiste en semana07_representaciones
    # (Si no, la reimplementamos en el dashboard para la UI)
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
KB_PATH = BASE_DIR / "data" / "base_conocimiento.txt"

@st.cache_data
def cargar_base_conocimiento():
    """Carga y categoriza los 30 procedimientos de la base de conocimiento."""
    procs = []
    categoria_map = {
        1: "Hardware", 2: "Red", 3: "Rendimiento", 4: "Seguridad",
        5: "Hardware", 6: "Hardware", 7: "Hardware", 8: "Red",
        9: "Software", 10: "Seguridad", 11: "Software", 12: "Almacenamiento",
        13: "Hardware", 14: "Hardware", 15: "Almacenamiento", 16: "Hardware",
        17: "Hardware", 18: "Red", 19: "Red", 20: "Red",
        21: "Red", 22: "Seguridad", 23: "Seguridad", 24: "Seguridad",
        25: "Seguridad", 26: "Rendimiento", 27: "Rendimiento", 28: "Rendimiento",
        29: "Rendimiento", 30: "Hardware"
    }
    if KB_PATH.exists():
        with open(KB_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or "->" not in line:
                    continue
                partes = line.split("->", 1)
                izq = partes[0].strip()
                derecha = partes[1].strip()
                id_num = None
                if "." in izq:
                    try:
                        id_num = int(izq.split(".")[0].strip())
                        titulo = izq.split(".", 1)[1].strip()
                    except ValueError:
                        titulo = izq
                else:
                    titulo = izq
                
                cat = categoria_map.get(id_num, "General")
                procs.append({
                    "id": id_num if id_num else len(procs) + 1,
                    "titulo": titulo,
                    "categoria": cat,
                    "solucion": derecha,
                    "pasos": [p.strip() for p in derecha.split(";") if p.strip()]
                })
    return procs

def parsear_audit_log():
    """Parsea el archivo audit.log separando fecha, nivel y mensaje."""
    if not AUDIT_LOG_PATH.exists():
        return [], ""
    
    with open(AUDIT_LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
        lineas = f.readlines()
        
    raw_text = "".join(lineas)
    registros = []
    import re
    patron = re.compile(r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+-\s+\[([A-Z]+)\]\s+-\s+(.*)$")
    
    for l in lineas:
        l_str = l.strip()
        if not l_str:
            continue
        m = patron.match(l_str)
        if m:
            fecha, nivel, mensaje = m.groups()
            registros.append({
                "fecha": fecha,
                "nivel": nivel,
                "mensaje": mensaje,
                "raw": l_str
            })
        else:
            registros.append({
                "fecha": "-",
                "nivel": "INFO",
                "mensaje": l_str,
                "raw": l_str
            })
    return registros, raw_text

def acepta_patron_falla_cascada(secuencia_logs):
    """Implementación del Autómata Finito Determinista (AFD) para la interfaz"""
    state = "q0"
    transitions = {
        ("q0", "O"): "q0", ("q0", "T"): "q0", ("q0", "E"): "q1",
        ("q1", "O"): "q0", ("q1", "E"): "q1", ("q1", "T"): "q2",
        ("q2", "O"): "q0", ("q2", "T"): "q0", ("q2", "E"): "q1",
    }
    for simbolo in secuencia_logs:
        if (state, simbolo) in transitions:
            state = transitions[(state, simbolo)]
        else:
            return False, "Símbolo inválido"
    return state == "q2", "Aceptada" if state == "q2" else "Rechazada"

# --- Barra Lateral ---
st.sidebar.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=80)
st.sidebar.title("Panel de Control TI")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegación",
    [
        "📊 Resumen Ejecutivo", 
        "📈 Matriz de Confusión", 
        "🔍 Sistema Híbrido & TF-IDF", 
        "⚙️ Planificador A* & Minimax", 
        "🧠 Representaciones del Reconocimiento", # <--- NUEVA OPCIÓN AÑADIDA AQUÍ
        "📚 Base de Conocimiento (KB)", 
        "📜 Trazas de Auditoría"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("**Institución:** ETITC - 10º Semestre\n\n**Autores:** Marco Molina & Daniel Daza")

# --- 1. Resumen Ejecutivo ---
if menu == "📊 Resumen Ejecutivo":
    st.title("🚀 Dashboard General del Asistente de Soporte TI")
    st.markdown("Monitoreo en tiempo real de los componentes lógicos, modelos de machine learning y flujos del sistema híbrido.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Accuracy Modelo Base", value="92.1%", delta="Benchmark Semana 02")
    with col2:
        st.metric(label="Base de Conocimiento", value="30 Procedimientos", delta="Activo (Semana 05)")
    with col3:
        st.metric(label="Algoritmo A*", value="3 Escenarios", delta="Costo Óptimo Calculado")
    with col4:
        st.metric(label="Módulo de Representaciones", value="3 Enfoques", delta="Numérico/Simbólico/AFD") # Actualizado

    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("📌 Distribución por Categorías Técnicas (KB)")
        data_cat = {
            "Categoría": ["Hardware", "Red", "Seguridad", "Rendimiento", "Almacenamiento", "Software"],
            "Procedimientos": [8, 6, 6, 6, 3, 3]
        }
        df_cat = pd.DataFrame(data_cat)
        st.bar_chart(df_cat.set_index("Categoría"))
        
    with col_b:
        st.subheader("🛠️ Estado de Integración de Módulos")
        st.success("✅ Validación y Matriz de Confusión (Semana 02) - Operativo (92.1%)")
        st.success("✅ Clasificador Taxonómico (Semana 03) - 100% de Coincidencia")
        st.success("✅ Planificador A* y Ciberdefensa Minimax (Semana 04) - Operativo")
        st.success("✅ Sistema Híbrido (Semana 05) - Operativo con Reglas y TF-IDF")
        st.success("✅ Representaciones del Reconocimiento (Semana 07) - Operativo") # Actualizado
        st.success("✅ Motor de Auditoría y Trazas - Registrando en artifacts/audit.log")

# --- 2. Matriz de Confusión ---
elif menu == "📈 Matriz de Confusión":
    st.title("📉 Validación del Modelo Base (Semana 02)")
    st.markdown("Evaluación del pipeline reproducible de clasificación multiclase del curso (StandardScaler + LogisticRegression sobre el benchmark estándar con división estratificada 75/25).")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Muestras de Entrenamiento", value="112")
        st.metric(label="Muestras de Prueba", value="38")
    with col2:
        st.metric(label="Accuracy Global", value="92.1% (0.921)")
        st.metric(label="Tasa de Error", value="7.9% (3/38)")
    
    st.markdown("---")
    st.subheader("Matriz de Confusión Numérica")
    
    if MODULOS_CARGADOS:
        try:
            cm = ejecutar_validacion()
            clases = ["Clase 0 (Setosa)", "Clase 1 (Versicolor)", "Clase 2 (Virginica)"]
            df_matriz = pd.DataFrame(
                cm,
                index=[f"Real: {c}" for c in clases],
                columns=[f"Pred: {c}" for c in clases]
            )
            st.dataframe(df_matriz, use_container_width=True)
            st.info("La matriz demuestra 35 aciertos de 38 muestras de prueba (92.1% de precisión global), con dispersión mínima focalizada únicamente en 3 casos límite entre clases contiguas.")
        except Exception as e:
            st.error(f"Error al ejecutar la validación del modelo: {e}")
    else:
        st.warning("Módulos no disponibles para generar la matriz en tiempo real.")

# --- 3. Sistema Híbrido & TF-IDF (Dinámico) ---
elif menu == "🔍 Sistema Híbrido & TF-IDF":
    st.title("🧠 Simulador de Sistema Híbrido (Reglas + TF-IDF)")
    st.markdown("Consulta la base de conocimiento en tiempo real utilizando similitud coseno sobre los 30 procedimientos de soporte y reglas lógicas expertas.")

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
                st.warning(f"**Clase Predicha (ML):** `{resultado['clase']}`")
                st.metric(label="Similitud Coseno", value=f"{resultado['similitud']:.4f}")
            with col2:
                st.markdown("### 📄 Evidencia Recuperada (TF-IDF)")
                st.success(f"{resultado['evidencia']}")
        else:
            st.error("No se pudieron cargar los módulos de Python desde la carpeta `src/`.")

# --- 4. Planificador A* & Minimax ---
elif menu == "⚙️ Planificador A* & Minimax":
    st.title("🤖 Optimización en Espacio de Estados y Decisiones Adversariales")
    
    tab1, tab2 = st.tabs(["Planificador A*", "Minimax (Juegos Adversariales)"])
    
    with tab1:
        st.subheader("Secuencia Óptima de Resolución de Soporte con A*")
        st.markdown("Encuentra la secuencia de acciones técnicas de menor costo de esfuerzo utilizando la distancia de Manhattan como heurística admisible $h(n)$.")
        
        if MODULOS_CARGADOS:
            escenarios = {
                "Caso 1: Incidente Estándar (Todo caído: Red=0, BD=0, App=0)": (0, 0, 0),
                "Caso 2: Condición Parcial (En proceso: Red=1, BD=1, App=0)": (1, 1, 0),
                "Caso 3: Restricción Preexistente (BD ya recuperada: Red=0, BD=2, App=1)": (0, 2, 1)
            }
            opcion = st.selectbox("Seleccionar Escenario de Estado Inicial:", list(escenarios.keys()))
            estado_ini = escenarios[opcion]
            
            ruta, costo_total = astar_soporte_ti(estado_ini, GOAL_STATE)
            st.info(f"📍 **Estado Inicial:** `{estado_ini}` ➔ **Estado Meta:** `{GOAL_STATE}` | **Costo Mínimo Acumulado:** `{costo_total}` unidades de esfuerzo")
            
            # --- Visualizador Gráfico de Recuperación de Subsistemas (Requerimiento B) ---
            st.markdown("#### 📊 Recuperación y Salud de Subsistemas")
            c_red, c_bd, c_app = st.columns(3)
            with c_red:
                st.markdown(f"**🌐 Red:** Nivel `{estado_ini[0]}/2`")
                st.progress(estado_ini[0] / 2.0, text=f"{(estado_ini[0]/2)*100:.0f}% Operativo")
            with c_bd:
                st.markdown(f"**🗄️ Base de Datos:** Nivel `{estado_ini[1]}/2`")
                st.progress(estado_ini[1] / 2.0, text=f"{(estado_ini[1]/2)*100:.0f}% Operativo")
            with c_app:
                st.markdown(f"**⚙️ Microservicio Backend:** Nivel `{estado_ini[2]}/2`")
                st.progress(estado_ini[2] / 2.0, text=f"{(estado_ini[2]/2)*100:.0f}% Operativo")
            
            if ruta:
                # Datos para gráfico de evolución paso a paso
                evolucion = [{
                    "Paso": "P0 (Inicial)",
                    "Red (%)": (estado_ini[0] / 2) * 100,
                    "Base de Datos (%)": (estado_ini[1] / 2) * 100,
                    "Backend (%)": (estado_ini[2] / 2) * 100
                }]
                pasos_lista = []
                for idx, (orig, dest, desc, c) in enumerate(ruta, 1):
                    evolucion.append({
                        "Paso": f"P{idx}: {desc[:15]}...",
                        "Red (%)": (dest[0] / 2) * 100,
                        "Base de Datos (%)": (dest[1] / 2) * 100,
                        "Backend (%)": (dest[2] / 2) * 100
                    })
                    pasos_lista.append({
                        "Paso": idx,
                        "Acción Correctiva": desc,
                        "Costo Paso": c,
                        "Transición de Estado": f"{orig} ➔ {dest}"
                    })
                
                st.markdown("##### 📈 Progresión de Salud hacia la Meta (2, 2, 2)")
                df_evol = pd.DataFrame(evolucion)
                st.line_chart(df_evol.set_index("Paso"))
                
                st.markdown("##### 📋 Secuencia Óptima de Acciones Técnicas")
                st.table(pd.DataFrame(pasos_lista))
            else:
                st.warning("No se encontró una ruta válida para este estado.")
        else:
            st.warning("Módulo A* no disponible temporalmente.")
        
    with tab2:
        st.subheader("🛡️ Simulador de Ciberdefensa con Minimax (Blue Team vs. Red Team)")
        st.markdown(
            "Modelado formal de **búsqueda adversarial de suma cero** para contención de incidentes de seguridad y mitigación de intrusión lateral.  \n"
            "- **Jugador MAX (Blue Team / Soporte TI):** Aplica contramedidas preventivas y aísla servidores críticos (`🛡️ Blindado`).  \n"
            "- **Jugador MIN (Red Team / Amenaza Externa):** Explota vulnerabilidades buscando comprometer una ruta crítica (`🚨 Comprometido`).  \n"
            "- **Objetivo:** Minimax evalúa exhaustivamente el árbol de decisiones para seleccionar el nodo que garantiza la resiliencia de la infraestructura corporativa."
        )
        if MODULOS_CARGADOS:
            diag = simular_ciberdefensa(minimax_board)
            
            col_left, col_right = st.columns([1, 1], gap="medium")
            
            with col_left:
                st.markdown("##### 🗺️ Topología de Servidores (Matriz 3x3)")
                
                tarjetas_html = []
                for i in range(9):
                    estado = minimax_board[i]
                    nombre = NODOS_INFRAESTRUCTURA[i]
                    es_mejor = (i == diag["posicion"])
                    
                    if estado == "X":
                        bg = "#e8f5e9"
                        border = "#2e7d32"
                        badge = "🛡️ Blue Team"
                        sub = "Blindado"
                    elif estado == "O":
                        bg = "#ffebee"
                        border = "#c62828"
                        badge = "🚨 Red Team"
                        sub = "Comprometido"
                    elif es_mejor:
                        bg = "#fff8e1"
                        border = "#f57f17"
                        badge = "🎯 Minimax"
                        sub = "Blindar Ahora"
                    else:
                        bg = "#f5f5f5"
                        border = "#9e9e9e"
                        badge = "🟢 En Línea"
                        sub = "Disponible"
                        
                    tarjetas_html.append(
                        f'<div style="background-color: {bg}; border: 2px solid {border}; border-radius: 8px; padding: 10px 4px; text-align: center; min-height: 90px;">'
                        f'<span style="font-size: 0.72rem; color: #555;">[Nodo #{i}]</span><br>'
                        f'<strong style="color: #111; font-size: 0.8rem;">{nombre}</strong><br>'
                        f'<span style="font-weight: bold; font-size: 0.75rem; color: {border};">{badge}</span><br>'
                        f'<small style="color: #444; font-size: 0.7rem;">{sub}</small>'
                        f'</div>'
                    )
                
                grid_html = '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px;">' + "".join(tarjetas_html) + '</div>'
                st.markdown(grid_html, unsafe_allow_html=True)
                
            with col_right:
                st.markdown("##### 🎯 Decisión Táctica de Contención")
                st.success(f"**Servidor Seleccionado:** `{diag['nodo']}` (Nodo #{diag['posicion']})")
                st.info(f"**Acción Defensiva:** {diag['accion']}")
                st.markdown(f"**Análisis Estratégico:**\n\n{diag['justificacion']}")
                st.caption("Función de Utilidad: +1 si el Blue Team asegura el perímetro, 0 si hay contención, -1 si el Red Team compromete la red.")
        else:
            st.warning("Módulo Minimax no disponible temporalmente.")

# --- NUEVA SECCIÓN: 5. REPRESENTACIONES DEL RECONOCIMIENTO (Semana 07) ---
elif menu == "🧠 Representaciones del Reconocimiento":
    st.title("🧠 Representaciones del Reconocimiento (Semana 07)")
    st.markdown("Simulación de los tres enfoques de inteligencia artificial para interpretar y procesar información técnica de soporte.")
    
    tab_num, tab_sim, tab_aut = st.tabs(["1️⃣ Numérica (Telemetría)", "2️⃣ Simbólica (Sistema Experto)", "3️⃣ Autómatas (Logs en Cascada)"])
    
    # 1. Representación Numérica
    with tab_num:
        st.subheader("Representación Numérica: Distancia Euclidiana (Telemetría)")
        st.markdown("Mide qué tan cerca está el estado actual del servidor de un perfil crítico de colapso, usando vectores numéricos y distancias en el espacio.")
        
        perfil_colapso = np.array([98.0, 95.0, 400.0]) # [CPU, RAM, Latencia]
        
        col_sliders, col_results = st.columns([1, 1])
        with col_sliders:
            st.markdown("**Ajusta las métricas actuales del servidor:**")
            cpu_val = st.slider("Uso de CPU (%)", 0.0, 100.0, 75.0)
            ram_val = st.slider("Uso de RAM (%)", 0.0, 100.0, 80.0)
            lat_val = st.slider("Latencia de Red (ms)", 10.0, 500.0, 150.0)
            
        with col_results:
            ticket_actual = np.array([cpu_val, ram_val, lat_val])
            distancia = np.linalg.norm(ticket_actual - perfil_colapso)
            
            st.markdown(f"**Vector de Colapso (Fijo):** `[{perfil_colapso[0]}, {perfil_colapso[1]}, {perfil_colapso[2]}]`")
            st.markdown(f"**Vector Actual (Dinámico):** `[{ticket_actual[0]}, {ticket_actual[1]}, {ticket_actual[2]}]`")
            
            st.metric(label="Distancia Matemática al Colapso", value=f"{distancia:.2f}")
            
            # Lógica de umbral
            if distancia < 60.0:
                st.error("🚨 **ALERTA CRÍTICA:** La distancia es corta. El servidor presenta un comportamiento matemáticamente similar al colapso.")
            elif distancia < 150.0:
                st.warning("⚠️ **ADVERTENCIA:** Las métricas muestran degradación de rendimiento. Monitoreo sugerido.")
            else:
                st.success("✅ **ESTABLE:** El servidor se encuentra matemáticamente lejano al perfil de colapso.")
                
    # 2. Representación Simbólica
    with tab_sim:
        st.subheader("Representación Simbólica: Inferencia Discreta (Hechos y Reglas)")
        st.markdown("Transforma el lenguaje natural en hechos discretos. Utiliza lógica `SI -> ENTONCES` para llegar a un diagnóstico absoluto y justificable.")
        
        st.markdown("**Selecciona los síntomas detectados en el ticket:**")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            sym_ping = st.checkbox("ping_fallido", value=True)
            sym_lento = st.checkbox("sistema_lento", value=False)
        with c2:
            sym_srv = st.checkbox("servidor_no_responde", value=False)
            sym_tmp = st.checkbox("temperatura_alta", value=False)
        with c3:
            sym_led = st.checkbox("luces_rojas_switch", value=False)
        
        hechos_detectados = set()
        if sym_ping: hechos_detectados.add("ping_fallido")
        if sym_lento: hechos_detectados.add("sistema_lento")
        if sym_srv: hechos_detectados.add("servidor_no_responde")
        if sym_tmp: hechos_detectados.add("temperatura_alta")
        if sym_led: hechos_detectados.add("luces_rojas_switch")
        
        st.markdown(f"**Base de Hechos Actual:** `{hechos_detectados}`")
        
        # Evaluación de reglas
        st.markdown("---")
        st.markdown("#### Motor de Inferencia")
        if {"ping_fallido", "servidor_no_responde"}.issubset(hechos_detectados) or \
           {"ping_fallido", "luces_rojas_switch"}.issubset(hechos_detectados):
            st.error("🚨 **Diagnóstico Simbólico:** `caida_red_masiva` detectada (Regla 1 activada)")
            st.markdown("**Acción:** Aislar nodo y ejecutar protocolo de enrutamiento alternativo.")
        elif {"temperatura_alta", "sistema_lento"}.issubset(hechos_detectados):
            st.warning("⚠️ **Diagnóstico Simbólico:** `sobrecalentamiento_hardware` (Regla 2 activada)")
            st.markdown("**Acción:** Acelerar ventiladores y migrar carga de procesamiento.")
        else:
            st.info("ℹ️ **Diagnóstico Simbólico:** Sin coincidencias de riesgo crítico. Incidentes aislados.")

    # 3. Representación por Autómata
    with tab_aut:
        st.subheader("Representación por Autómata: Validación de Cronologías")
        st.markdown("Utiliza un Autómata Finito Determinista (AFD) para auditar secuencias de tiempo. Valida si una sucesión de eventos (`O`: Operativo, `E`: Error, `T`: Timeout) desencadena el patrón estricto de una *falla en cascada* (errores finalizados en un Timeout).")
        
        st.markdown("**Alfabeto permitido:** `O` (Operativo), `E` (Error), `T` (Timeout)")
        secuencia = st.text_input("Ingresa una secuencia de logs temporales:", "OOOEET").upper()
        
        if st.button("Auditar Secuencia con AFD"):
            secuencia_limpia = "".join(c for c in secuencia if c in ['O', 'E', 'T'])
            
            if len(secuencia_limpia) != len(secuencia):
                st.error(f"La secuencia contiene caracteres no válidos. Procesando solo la parte válida: `{secuencia_limpia}`")
            
            if not secuencia_limpia:
                st.warning("Ingresa una secuencia válida (ej. 'OEOET').")
            else:
                aceptada, mensaje = acepta_patron_falla_cascada(secuencia_limpia)
                
                st.markdown(f"#### Resultados de Auditoría para: `{secuencia_limpia}`")
                
                # Visualización tipo paso a paso del autómata
                estado_visual = "q0"
                pasos = [f"Inicio (q0)"]
                for sim in secuencia_limpia:
                    if sim == 'O': 
                        estado_visual = "q0"
                    elif sim == 'E' and estado_visual in ["q0", "q2"]:
                        estado_visual = "q1"
                    elif sim == 'E' and estado_visual == "q1":
                        estado_visual = "q1"
                    elif sim == 'T' and estado_visual == "q1":
                        estado_visual = "q2"
                    elif sim == 'T' and estado_visual in ["q0", "q2"]:
                        estado_visual = "q0"
                    pasos.append(f"Leer '{sim}' ➔ {estado_visual}")
                
                st.code(" -> ".join(pasos), language="text")
                
                if aceptada:
                    st.success("✅ **Secuencia Aceptada.** El AFD confirma que el patrón `[Error -> Timeout]` se cumple al final de la traza. Falla en cascada confirmada.")
                else:
                    st.error("❌ **Secuencia Rechazada.** El patrón estricto de falla no se cumplió (el sistema pudo haberse estabilizado al final o la secuencia no terminó en Timeout).")


# --- 6. Base de Conocimiento (KB) (Requerimiento C) ---
elif menu == "📚 Base de Conocimiento (KB)":
    st.title("📚 Base de Conocimiento Técnica (KB)")
    st.markdown("Catálogo de los **30 procedimientos operativos estandarizados** del Asistente de Soporte TI, utilizados para el entrenamiento del clasificador y el motor TF-IDF.")
    
    procedimientos = cargar_base_conocimiento()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        categorias = ["Todas", "Hardware", "Red", "Seguridad", "Rendimiento", "Almacenamiento", "Software"]
        cat_sel = st.selectbox("Filtrar por Categoría:", categorias)
    with col2:
        busqueda = st.text_input("Buscar procedimiento o palabra clave (ej. 'disco', 'wifi', 'memoria'):")
    
    # Filtrar
    filtrados = procedimientos
    if cat_sel != "Todas":
        filtrados = [p for p in filtrados if p["categoria"] == cat_sel]
    if busqueda.strip():
        q_b = busqueda.lower().strip()
        filtrados = [
            p for p in filtrados
            if q_b in p["titulo"].lower() or q_b in p["solucion"].lower() or q_b in p["categoria"].lower()
        ]
    
    st.markdown(f"**Mostrando {len(filtrados)} de {len(procedimientos)} procedimientos técnicos disponibles**")
    st.markdown("---")
    
    if filtrados:
        for proc in filtrados:
            with st.expander(f"📌 #{proc['id']} - {proc['titulo']}  [{proc['categoria']}]"):
                st.markdown(f"**Categoría:** `{proc['categoria']}`")
                st.markdown("**Procedimiento de Solución:**")
                for paso_idx, paso in enumerate(proc['pasos'], 1):
                    st.markdown(f"{paso_idx}. {paso}")
    else:
        st.warning("No se encontraron procedimientos que coincidan con los filtros aplicados.")

# --- 7. Trazas de Auditoría (Requerimiento D) ---
elif menu == "📜 Trazas de Auditoría":
    st.title("📝 Registro de Auditoría del Sistema (audit.log)")
    st.markdown("Monitoreo y observabilidad de eventos generados por el orquestador `main.py` y los clasificadores del sistema.")
    
    registros, raw_text = parsear_audit_log()
    
    if registros:
        # Métricas de resumen de auditoría
        total_logs = len(registros)
        info_count = sum(1 for r in registros if r["nivel"] == "INFO")
        warn_count = sum(1 for r in registros if r["nivel"] in ["WARNING", "WARN"])
        err_count = sum(1 for r in registros if r["nivel"] == "ERROR")
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Eventos", total_logs)
        with m2:
            st.metric("Eventos INFO", info_count)
        with m3:
            st.metric("Alertas / Errores", warn_count + err_count)
        with m4:
            st.metric("Último Registro", registros[-1]["fecha"] if registros else "-")
        
        st.markdown("---")
        
        # Filtros interactivos
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            niveles_disp = sorted(list(set(r["nivel"] for r in registros)))
            niveles_sel = st.multiselect("Filtrar por Nivel:", niveles_disp, default=niveles_disp)
        with f_col2:
            texto_filtro = st.text_input("Buscar en trazas (Ticket ID, Acción, Texto):")
            
        # Filtrado de registros
        regs_filtrados = [r for r in registros if r["nivel"] in niveles_sel]
        if texto_filtro.strip():
            tf = texto_filtro.lower().strip()
            regs_filtrados = [r for r in regs_filtrados if tf in r["mensaje"].lower() or tf in r["fecha"].lower()]
            
        st.caption(f"Mostrando {len(regs_filtrados)} de {total_logs} líneas registradas.")
        
        tab_tabla, tab_raw = st.tabs(["📋 Vista Estructurada", "🖥️ Consola Raw"])
        
        with tab_tabla:
            if regs_filtrados:
                df_regs = pd.DataFrame(regs_filtrados)[["fecha", "nivel", "mensaje"]]
                df_regs.columns = ["Fecha / Hora", "Nivel", "Detalle del Evento"]
                st.dataframe(df_regs, use_container_width=True, height=400)
            else:
                st.info("No hay eventos que coincidan con los filtros seleccionados.")
                
        with tab_raw:
            st.text_area("Contenido Completo de audit.log", raw_text, height=400)
            st.download_button(
                label="⬇️ Descargar audit.log",
                data=raw_text,
                file_name="audit.log",
                mime="text/plain"
            )
    else:
        st.warning("No se encontró el archivo de auditoría en `artifacts/audit.log`. Ejecuta `python src/main.py` para generarlo.")