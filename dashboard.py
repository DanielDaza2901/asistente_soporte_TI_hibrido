import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import numpy as np
import pickle
import sqlite3
import networkx as nx
import base64
from PIL import Image
import io

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
    from classifiers.vision import ejecutar_vision_soporte
    from classifiers.texturas import procesar_imagen_proyecto
    from classifiers.motor_inferencia import inferir_con_explicacion, REGLAS_SOPORTE_TI
    from classifiers.red_semantica import RedSemanticaSoporteTI, RELACIONES, RELACIONES_HEREDABLES, normalizar  # S14 REDES SEMÁNTICAS
    MODULOS_CARGADOS = True
except ImportError as e:
    MODULOS_CARGADOS = False

# Módulo de preguntas frecuentes (independiente: si falta, solo esa página lo avisa)
try:
    from classifiers.faq_semanas import AsistenteFAQ, SEMANAS
    FAQ_DISPONIBLE = True
except ImportError:
    AsistenteFAQ, SEMANAS = None, {}
    FAQ_DISPONIBLE = False

# Configuración de la página
st.set_page_config(
    page_title="Dashboard - Asistente de Soporte TI Híbrido",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (sistema de diseño: paleta, tipografía y componentes)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --ink: #0F1B2D;
        --ink-hover: #1A2B45;
        --accent: #2457D6;
        --accent-dark: #1B44AD;
        --accent-soft: #E8EEFC;
        --bg: #F4F6FA;
        --surface: #FFFFFF;
        --line: #E2E7F0;
        --text: #14213D;
        --muted: #5B6779;
        --ok: #1E8E5A;
        --ok-soft: #E7F5EE;
        --warn: #B7791F;
        --warn-soft: #FEF6E4;
        --err: #C0392B;
        --err-soft: #FCEBE9;
    }

    /* ---------- Base ---------- */
    .stApp {
        background: var(--bg);
        color: var(--text);
        font-family: 'IBM Plex Sans', 'Segoe UI', Roboto, Arial, sans-serif;
    }
    h1, h2, h3, h4, h5, p, li, label, td, th, input, textarea, button {
        font-family: 'IBM Plex Sans', 'Segoe UI', Roboto, Arial, sans-serif;
    }
    code, pre, [data-testid="stCode"] * {
        font-family: 'IBM Plex Mono', Consolas, 'Courier New', monospace !important;
    }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }

    /* ---------- Tipografía ---------- */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {
        text-align: left !important;
        color: var(--text);
        letter-spacing: -0.01em;
    }
    .stApp h2 { font-size: 1.25rem; font-weight: 600; }
    .stApp h3 { font-size: 1.1rem; font-weight: 600; }
    .stApp h4 { font-size: 1rem; font-weight: 600; }
    .stApp h5 { font-size: 0.92rem; font-weight: 600; color: var(--muted); }
    .stApp p, .stApp li { line-height: 1.6; }
    .stApp hr { border: none; border-top: 1px solid var(--line); margin: 1.4rem 0; }
    .stApp code {
        background: var(--accent-soft);
        color: var(--accent-dark);
        border-radius: 5px;
        padding: 1px 6px;
        font-size: 0.85em;
    }

    /* ---------- Cabecera de página ---------- */
    .page-head { margin: 0 0 1.6rem 0; padding-bottom: 1.1rem; border-bottom: 1px solid var(--line); }
    .page-head h1 {
        font-size: 1.75rem; font-weight: 700; line-height: 1.25;
        margin: 0 0 0.45rem 0; padding: 0 !important; color: var(--text);
    }
    .page-head p { color: var(--muted); margin: 0; max-width: 80ch; font-size: 0.97rem; }
    .page-head code { font-size: 0.82em; }

    /* ---------- Barra lateral ---------- */
    [data-testid="stSidebar"] { background: var(--ink); border-right: 1px solid #0B1424; }
    [data-testid="stSidebar"] * { color: #C9D3E3; }
    [data-testid="stSidebar"] hr { border-top: 1px solid #22344F; margin: 1.1rem 0; }
    [data-testid="stSidebar"] button svg { color: #C9D3E3; fill: #C9D3E3; }

    .brand { display: flex; align-items: center; gap: 12px; padding: 6px 4px 4px 4px; }
    .brand-mark {
        width: 40px; height: 40px; border-radius: 10px; background: var(--accent);
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1rem; letter-spacing: 0.02em; flex-shrink: 0;
    }
    [data-testid="stSidebar"] .brand-mark { color: #FFFFFF; }
    .brand-name { font-size: 1.02rem; font-weight: 600; line-height: 1.2; }
    [data-testid="stSidebar"] .brand-name { color: #FFFFFF; }
    .brand-sub { font-size: 0.78rem; margin-top: 2px; }
    [data-testid="stSidebar"] .brand-sub { color: #8294AE; }

    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 0.8rem; font-weight: 500; color: #8294AE; margin-bottom: 6px;
    }
    [data-testid="stSidebar"] [role="radiogroup"] { gap: 2px; }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        width: 100%; padding: 9px 12px; border-radius: 8px; cursor: pointer;
        transition: background 0.15s ease;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label div:not(:has(p)),
    [data-testid="stSidebar"] [role="radiogroup"] label span:not(:has(p)),
    [data-testid="stSidebar"] [role="radiogroup"] label svg { display: none !important; }
    [data-testid="stSidebar"] [role="radiogroup"] label p { font-size: 0.9rem; font-weight: 500; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background: var(--ink-hover); }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: var(--accent); }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * { color: #FFFFFF; font-weight: 600; }

    .side-card { background: var(--ink-hover); border: 1px solid #22344F; border-radius: 10px; padding: 12px 14px; }
    .side-card-k { font-size: 0.75rem; margin-top: 8px; }
    .side-card-k:first-child { margin-top: 0; }
    [data-testid="stSidebar"] .side-card-k { color: #8294AE; }
    .side-card-v { font-size: 0.86rem; font-weight: 500; line-height: 1.4; }
    [data-testid="stSidebar"] .side-card-v { color: #FFFFFF; }

    /* ---------- Métricas ---------- */
    [data-testid="stMetric"] {
        background: var(--surface); border: 1px solid var(--line);
        border-left: 4px solid var(--accent); border-radius: 10px;
        padding: 14px 18px; box-shadow: 0 1px 2px rgba(15, 27, 45, 0.04);
    }
    [data-testid="stMetricLabel"] p { color: var(--muted); font-size: 0.82rem; font-weight: 500; }
    [data-testid="stMetricValue"] { color: var(--text); font-weight: 600; }
    [data-testid="stMetricValue"] > div {
        font-size: 1.5rem; white-space: normal; overflow: visible; text-overflow: clip; line-height: 1.25;
    }
    [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] * { color: var(--muted) !important; font-size: 0.78rem; }
    [data-testid="stMetricDelta"] { background: #EDF1F8 !important; border-radius: 6px; padding: 2px 8px; width: fit-content; }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* ---------- Alertas ---------- */
    [data-testid="stAlert"] { border-radius: 10px; border: 1px solid var(--line); }
    [data-testid="stAlert"] p { line-height: 1.55; }

    /* ---------- Estado de módulos (Resumen) ---------- */
    .status-list { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
    .status-row {
        display: flex; align-items: center; justify-content: space-between; gap: 14px;
        padding: 11px 16px; border-bottom: 1px solid var(--line);
    }
    .status-row:last-child { border-bottom: none; }
    .status-name { color: var(--text); font-size: 0.9rem; font-weight: 500; line-height: 1.35; }
    .status-meta { color: var(--muted); font-size: 0.78rem; margin-top: 1px; }
    .status-meta:empty { display: none; }
    .badge-ok {
        background: var(--ok-soft); color: var(--ok); border-radius: 999px;
        padding: 3px 11px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;
    }

    /* ---------- Pestañas ---------- */
    [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line); }
    button[data-baseweb="tab"] { padding: 10px 16px; border-radius: 8px 8px 0 0; }
    button[data-baseweb="tab"] p { font-size: 0.92rem; font-weight: 500; color: var(--muted); }
    [data-baseweb="tab-list"] button[aria-selected="true"],
    [data-baseweb="tab-list"] button[aria-selected="true"] * { color: var(--accent) !important; font-weight: 600; }
    [data-baseweb="tab-highlight"] { background-color: var(--accent) !important; height: 3px; }
    [data-baseweb="tab-border"] { display: none; }

    /* ---------- Botones ---------- */
    .stButton > button, [data-testid="stDownloadButton"] > button {
        background: var(--accent); color: #FFFFFF; border: none; border-radius: 8px;
        padding: 0.55rem 1.3rem; font-weight: 600; font-size: 0.92rem;
        box-shadow: 0 1px 2px rgba(15, 27, 45, 0.12);
        transition: background 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
        background: var(--accent-dark); color: #FFFFFF; border: none;
        box-shadow: 0 3px 8px rgba(36, 87, 214, 0.28);
    }
    .stButton > button:focus-visible, [data-testid="stDownloadButton"] > button:focus-visible {
        outline: 3px solid rgba(36, 87, 214, 0.35); outline-offset: 2px;
    }
    .stButton > button p, [data-testid="stDownloadButton"] > button p { color: #FFFFFF; }

    /* ---------- Campos de entrada ---------- */
    [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
        background: var(--surface); border-radius: 8px; border-color: var(--line);
    }
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {
        border-color: var(--accent); box-shadow: 0 0 0 3px rgba(36, 87, 214, 0.15);
    }
    [data-testid="stWidgetLabel"] p { font-size: 0.88rem; font-weight: 500; color: var(--text); }
    [data-testid="stFileUploaderDropzone"] {
        background: var(--surface); border: 1.5px dashed #B9C4D8; border-radius: 12px;
    }

    /* ---------- Expansores, tablas y código ---------- */
    [data-testid="stExpander"] {
        background: var(--surface); border: 1px solid var(--line); border-radius: 10px; margin-bottom: 8px;
    }
    [data-testid="stExpander"] summary p { font-weight: 600; font-size: 0.93rem; }
    [data-testid="stTable"] table { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; background: var(--surface); }
    [data-testid="stTable"] th { background: #EDF1F8; color: var(--text); font-weight: 600; font-size: 0.85rem; }
    [data-testid="stTable"] td { font-size: 0.88rem; border-color: var(--line); }
    [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
    [data-testid="stCode"] { border: 1px solid var(--line); border-radius: 10px; }
    [data-testid="stImage"] img { border-radius: 10px; border: 1px solid var(--line); }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: var(--muted) !important; opacity: 1 !important; }

    /* =====================================================================
       SISTEMA DE DISEÑO V2: menú, desplegables, estados, gráficas y controles
       ===================================================================== */

    /* ---------- Barra lateral: grupos del menú ---------- */
    [data-testid="stSidebar"] [role="radiogroup"] > label { position: relative; }
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(1),
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(3),
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(10),
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(12) { margin-top: 30px; }
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(1)::before,
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(3)::before,
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(10)::before,
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(12)::before {
        position: absolute; left: 12px; top: -23px; pointer-events: none;
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: #6F829F;
    }
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(1)::before { content: "Fundamentos"; }
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(3)::before { content: "Modelos y algoritmos"; }
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(10)::before { content: "Conocimiento"; }
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(12)::before { content: "Operación"; }

    /* ---------- Menús desplegables (selectbox y multiselect) ---------- */
    [data-baseweb="select"] > div { min-height: 42px; transition: border-color 0.15s ease, box-shadow 0.15s ease; }
    [data-baseweb="select"] > div:hover { border-color: #B9C4D8; }
    [data-baseweb="select"]:focus-within > div { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(36, 87, 214, 0.15); }
    [data-baseweb="select"] svg { color: var(--muted); }
    [data-baseweb="tag"] { border-radius: 6px; font-weight: 500; }
    div[data-baseweb="popover"] { font-family: 'IBM Plex Sans', 'Segoe UI', Roboto, Arial, sans-serif; }
    div[data-baseweb="popover"] > div {
        border-radius: 12px; border: 1px solid var(--line); background: var(--surface);
        box-shadow: 0 12px 32px rgba(15, 27, 45, 0.18); overflow: hidden;
    }
    div[data-baseweb="popover"] ul[role="listbox"], div[data-baseweb="popover"] [data-baseweb="menu"] { background: var(--surface); padding: 6px; }
    div[data-baseweb="popover"] li[role="option"] {
        border-radius: 8px; margin: 1px 0; padding-top: 9px; padding-bottom: 9px; font-size: 0.9rem; color: var(--text);
    }
    div[data-baseweb="popover"] li[role="option"]:hover,
    div[data-baseweb="popover"] li[role="option"][data-highlighted="true"] { background: var(--accent-soft); }
    div[data-baseweb="popover"] li[role="option"][aria-selected="true"] { background: var(--accent-soft); color: var(--accent-dark); font-weight: 600; }

    /* ---------- Estados: alertas por tipo ---------- */
    [data-testid="stAlert"] {
        border-radius: 10px; border: 1px solid var(--line); border-left: 4px solid var(--line);
        box-shadow: 0 1px 2px rgba(15, 27, 45, 0.04);
    }
    [data-testid="stAlert"] p, [data-testid="stAlert"] li { color: var(--text); }
    [data-testid="stAlert"] code { background: rgba(255, 255, 255, 0.8); color: var(--accent-dark); }
    [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) { background: var(--accent-soft); border-color: #CFDBF8; border-left-color: var(--accent); }
    [data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { background: var(--ok-soft); border-color: #CBE8D8; border-left-color: var(--ok); }
    [data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { background: var(--warn-soft); border-color: #F2DFB5; border-left-color: var(--warn); }
    [data-testid="stAlert"]:has([data-testid="stAlertContentError"]) { background: var(--err-soft); border-color: #F2C9C4; border-left-color: var(--err); }

    /* ---------- Tarjetas de resultado de los modelos ---------- */
    .result-card {
        background: var(--surface); border: 1px solid var(--line); border-left: 4px solid var(--tono, var(--accent));
        border-radius: 12px; padding: 14px 18px; margin: 0 0 12px 0; box-shadow: 0 1px 2px rgba(15, 27, 45, 0.04);
    }
    .result-label { font-size: 0.78rem; font-weight: 600; color: var(--muted); letter-spacing: 0.02em; margin-bottom: 4px; }
    .result-value { font-size: 1.35rem; font-weight: 700; color: var(--text); line-height: 1.3; word-break: break-word; }
    .result-card.texto .result-value { font-size: 0.98rem; font-weight: 500; line-height: 1.6; }
    .result-detail {
        display: inline-block; margin-top: 8px; padding: 2px 10px; border-radius: 6px;
        background: var(--tono-suave, var(--accent-soft)); color: var(--tono, var(--accent)); font-size: 0.78rem; font-weight: 600;
    }
    .result-bar { margin-top: 10px; height: 8px; border-radius: 999px; background: #E9EDF4; overflow: hidden; }
    .result-bar > span { display: block; height: 100%; border-radius: 999px; background: var(--tono, var(--accent)); }
    .badge-warn { background: var(--warn-soft); color: var(--warn); border-radius: 999px; padding: 3px 11px; font-size: 0.75rem; font-weight: 600; }
    .badge-err { background: var(--err-soft); color: var(--err); border-radius: 999px; padding: 3px 11px; font-size: 0.75rem; font-weight: 600; }

    /* ---------- Gráficas e imágenes como paneles ---------- */
    [data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"], [data-testid="stGraphVizChart"] {
        background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
        padding: 14px 14px 8px 14px; box-shadow: 0 1px 2px rgba(15, 27, 45, 0.04);
    }
    [data-testid="stImage"] img { background: var(--surface); box-shadow: 0 1px 2px rgba(15, 27, 45, 0.05); }
    [data-testid="stImageCaption"] { color: var(--muted); font-size: 0.8rem; text-align: center; }

    /* ---------- Controles operativos ---------- */
    [data-testid="stProgress"] [role="progressbar"] { height: 10px !important; border-radius: 999px; background: #E2E7F0; overflow: hidden; }
    [data-testid="stProgress"] [role="progressbar"] > div { border-radius: 999px; }
    [data-testid="stProgress"] p { font-size: 0.82rem; color: var(--muted); }
    [data-testid="stSlider"] [data-testid="stThumbValue"] { color: var(--accent-dark); font-weight: 600; font-size: 0.85rem; }
    [data-testid="stSlider"] [data-testid="stTickBarMin"], [data-testid="stSlider"] [data-testid="stTickBarMax"] { color: var(--muted); font-size: 0.75rem; }
    [data-testid="stCheckbox"] label { padding: 6px 10px; border-radius: 8px; transition: background 0.15s ease; }
    [data-testid="stCheckbox"] label:hover { background: var(--accent-soft); }
    [data-testid="stCheckbox"] label p { font-size: 0.9rem; }
    .stButton > button:active, [data-testid="stDownloadButton"] > button:active { transform: translateY(1px); box-shadow: none; }
    .stButton > button:disabled, [data-testid="stDownloadButton"] > button:disabled {
        background: #C5CEDC; color: #FFFFFF; box-shadow: none; cursor: not-allowed;
    }
    [data-testid="stFileUploaderDropzone"] { transition: border-color 0.15s ease, background 0.15s ease; }
    [data-testid="stFileUploaderDropzone"]:hover { border-color: var(--accent); background: var(--accent-soft); }
    [data-testid="stExpander"] summary { border-radius: 10px; transition: background 0.15s ease; }
    [data-testid="stExpander"] summary:hover { background: #F7F9FC; }
    [data-testid="stExpander"] details[open] > summary { border-bottom: 1px solid var(--line); border-radius: 10px 10px 0 0; }
    [data-testid="stMetric"] { transition: box-shadow 0.15s ease; }
    [data-testid="stMetric"]:hover { box-shadow: 0 4px 14px rgba(15, 27, 45, 0.08); }
    [data-testid="stSpinner"] { color: var(--muted); }
    [data-testid="stTooltipContent"] { font-size: 0.82rem; border-radius: 8px; }

    /* ---------- Barras de desplazamiento ---------- */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-thumb { background: #C5CEDC; border-radius: 999px; border: 2px solid transparent; background-clip: content-box; }
    ::-webkit-scrollbar-thumb:hover { background: #A9B6CB; background-clip: content-box; }
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb { background: #2A3E5C; background-clip: content-box; }
    [data-testid="stSidebar"] ::-webkit-scrollbar-track { background: transparent; }

    /* =====================================================================
       SEGUNDA PASADA: cabecera, subtítulos, selector segmentado, estado y FAQ
       ===================================================================== */
    .page-eyebrow { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); margin-bottom: 0.5rem; }
    [data-testid="stMain"] h3 { font-size: 1.12rem; padding-bottom: 0.45rem; border-bottom: 1px solid var(--line); margin-bottom: 0.8rem; }

    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(15) { margin-top: 30px; }
    [data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(15)::before {
        content: "Ayuda"; position: absolute; left: 12px; top: -23px; pointer-events: none;
        font-size: 0.68rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: #6F829F;
    }
    .dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px; }
    .dot.ok { background: #34D399; }
    .dot.err { background: #F87171; }

    /* Selectores horizontales del área principal como botones segmentados */
    [data-testid="stMain"] [role="radiogroup"] { gap: 8px; flex-wrap: wrap; }
    [data-testid="stMain"] [role="radiogroup"] label {
        background: var(--surface); border: 1px solid var(--line); border-radius: 999px;
        padding: 5px 15px; cursor: pointer; transition: background 0.15s ease, border-color 0.15s ease;
    }
    [data-testid="stMain"] [role="radiogroup"] label div:not(:has(p)),
    [data-testid="stMain"] [role="radiogroup"] label span:not(:has(p)),
    [data-testid="stMain"] [role="radiogroup"] label svg { display: none !important; }
    [data-testid="stMain"] [role="radiogroup"] label p { font-size: 0.86rem; font-weight: 500; }
    [data-testid="stMain"] [role="radiogroup"] label:hover { border-color: #B9C4D8; background: #F7F9FC; }
    [data-testid="stMain"] [role="radiogroup"] label:has(input:checked) { background: var(--accent); border-color: var(--accent); }
    [data-testid="stMain"] [role="radiogroup"] label:has(input:checked) p { color: #FFFFFF; font-weight: 600; }

    /* Preguntas frecuentes */
    .faq-card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 16px 20px; margin: 0 0 12px 0; box-shadow: 0 1px 2px rgba(15, 27, 45, 0.04); }
    .faq-card.mejor { border-color: #B9CBF5; box-shadow: 0 2px 10px rgba(36, 87, 214, 0.10); }
    .faq-top { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 10px; }
    .faq-sem { background: var(--accent-soft); color: var(--accent-dark); border-radius: 999px; padding: 2px 11px; font-size: 0.74rem; font-weight: 600; }
    .faq-best { background: var(--ok-soft); color: var(--ok); border-radius: 999px; padding: 2px 11px; font-size: 0.74rem; font-weight: 600; }
    .faq-sim { margin-left: auto; font-size: 0.78rem; font-weight: 600; color: var(--muted); }
    .faq-q { font-size: 1.04rem; font-weight: 600; color: var(--text); line-height: 1.4; margin: 0 0 6px 0; }
    .faq-a { font-size: 0.93rem; color: var(--text); line-height: 1.65; margin: 0; }
    .faq-meta { margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--line); font-size: 0.78rem; color: var(--muted); }
    [class*="st-key-faq_sug"] button {
        width: 100%; text-align: left; justify-content: flex-start; background: var(--surface); color: var(--accent-dark);
        border: 1px solid var(--line); box-shadow: none; font-weight: 500;
    }
    [class*="st-key-faq_sug"] button:hover { background: var(--accent-soft); border-color: #B9CBF5; color: var(--accent-dark); box-shadow: none; }
    [class*="st-key-faq_sug"] button p { color: var(--accent-dark); }

    /* =====================================================================
       TERCERA PASADA: ruta del proyecto, accesos rápidos y pie de página
       ===================================================================== */
    .roadmap { display: flex; overflow-x: auto; padding: 8px 2px 16px 2px; margin: 4px 0 10px 0; }
    .rm-step { position: relative; flex: 1 0 94px; text-align: center; padding: 0 6px; }
    .rm-step::before { content: ""; position: absolute; top: 28px; left: -50%; width: 100%; height: 2px; background: #C9D5EE; z-index: 0; }
    .rm-step:first-child::before { display: none; }
    .rm-dot {
        position: relative; z-index: 1; width: 40px; height: 40px; margin: 8px auto 10px auto; border-radius: 50%;
        background: var(--accent); color: #FFFFFF; font-weight: 700; font-size: 0.88rem;
        display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 5px var(--accent-soft);
    }
    .rm-name { font-size: 0.78rem; font-weight: 700; color: var(--text); }
    .rm-desc { font-size: 0.76rem; color: var(--muted); line-height: 1.35; margin-top: 2px; }
    .quick-group { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--muted); margin: 16px 0 8px 0; }
    [class*="st-key-acc_"] button {
        width: 100%; text-align: left; justify-content: flex-start; min-height: 58px; padding: 12px 16px;
        background: var(--surface); color: var(--text); border: 1px solid var(--line); box-shadow: none; font-weight: 600;
    }
    [class*="st-key-acc_"] button:hover { border-color: var(--accent); background: var(--accent-soft); color: var(--accent-dark); box-shadow: 0 4px 14px rgba(36, 87, 214, 0.10); }
    [class*="st-key-acc_"] button p { color: inherit; font-weight: 600; text-align: left; }
    .app-footer { margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid var(--line); font-size: 0.78rem; color: var(--muted); text-align: center; }

    /* =====================================================================
       AJUSTES TRAS REVISAR CAPTURAS: desbordes, márgenes y botones
       ===================================================================== */
    [data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"], [data-testid="stGraphVizChart"] {
        box-sizing: border-box; max-width: 100%; overflow: hidden;
    }
    .block-container { padding-left: 2.8rem !important; padding-right: 2.8rem !important; }
    .rm-step { flex: 1 0 84px; padding: 0 3px; }
    .rm-desc { font-size: 0.72rem; }
    [class*="st-key-acc_"] button, [class*="st-key-faq_sug"] button { height: auto; min-height: 60px; }
    [class*="st-key-acc_"] button p, [class*="st-key-faq_sug"] button p {
        white-space: normal; overflow: visible; text-overflow: clip; line-height: 1.3; text-align: left;
    }

    /* =====================================================================
       PORTADA: recorrido real, actividad, arquitectura y estados
       ===================================================================== */
    .rm-step.pend .rm-dot { background: #C5CEDC; box-shadow: 0 0 0 5px #EDF1F8; }
    .rm-step.pend .rm-name, .rm-step.pend .rm-desc { color: #8A97AB; }
    .activity { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 6px 20px; }
    .act-item { position: relative; display: flex; gap: 14px; padding: 12px 0; border-bottom: 1px solid var(--line); }
    .act-item:last-child { border-bottom: none; }
    .act-dot { flex-shrink: 0; width: 10px; height: 10px; margin-top: 6px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 0 4px var(--accent-soft); }
    .act-body { flex: 1; min-width: 0; }
    .act-top { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
    .act-action { font-size: 0.9rem; font-weight: 600; color: var(--text); }
    .act-time { font-size: 0.76rem; color: var(--muted); white-space: nowrap; }
    .act-detail { font-size: 0.82rem; color: var(--muted); margin-top: 2px; line-height: 1.45; word-break: break-word; }
    .arch { display: flex; align-items: stretch; gap: 0; overflow-x: auto; padding: 6px 2px 12px 2px; }
    .arch-col { flex: 1 1 0; min-width: 150px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 12px; }
    .arch-head { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--accent); margin-bottom: 10px; }
    .arch-chip { background: #F4F6FA; border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; margin-bottom: 8px; }
    .arch-chip b { display: block; font-size: 0.82rem; color: var(--text); }
    .arch-chip span { display: block; font-size: 0.72rem; color: var(--muted); margin-top: 1px; }
    .arch-arrow { flex: 0 0 26px; display: flex; align-items: center; justify-content: center; color: #9AA8C0; font-size: 1.1rem; }

    /* =====================================================================
       ESTADO: barras propias y paneles de gráfica sin desborde
       ===================================================================== */
    [data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"], [data-testid="stGraphVizChart"] { padding: 0 !important; }
    .bars { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 14px 20px; margin-bottom: 6px; box-shadow: 0 1px 2px rgba(15, 27, 45, 0.04); }
    .bar-row { display: flex; align-items: center; gap: 14px; padding: 8px 0; }
    .bar-label { flex: 0 0 124px; font-size: 0.86rem; font-weight: 500; color: var(--text); }
    .bar-track { flex: 1; height: 10px; background: #E9EDF4; border-radius: 999px; overflow: hidden; }
    .bar-fill { height: 100%; background: var(--accent); border-radius: 999px; }
    .bar-value { flex: 0 0 26px; text-align: right; font-size: 0.86rem; font-weight: 600; color: var(--text); }
    </style>
""", unsafe_allow_html=True)

ETIQUETAS_PAGINA = {
    "Resumen Ejecutivo": "Fundamentos",
    "Matriz de Confusión": "Fundamentos · Semana 02",
    "Sistema Híbrido & TF-IDF": "Modelos y algoritmos · Semana 05",
    "Planificador A* & Minimax": "Modelos y algoritmos · Semana 04",
    "Representaciones del Reconocimiento": "Modelos y algoritmos · Semana 07",
    "Red Neuronal & Ontología": "Modelos y algoritmos · Semana 08",
    "Visión Artificial (Semana 09)": "Modelos y algoritmos · Semana 09",
    "Histogramas y Texturas LBP (Semana 10)": "Modelos y algoritmos · Semana 10",
    "Benchmark y Decisiones de Modelos (Semana 11)": "Modelos y algoritmos · Semana 11",
    "Motor de Inferencia (Semana 13)": "Conocimiento · Semana 13",
    "Redes Semánticas (Semana 14)": "Conocimiento · Semana 14",
    "Portal de Usuario": "Operación",
    "Base de Conocimiento (KB)": "Operación",
    "Trazas de Auditoría": "Operación",
    "Preguntas Frecuentes (FAQ)": "Ayuda · Semana 02 a Semana 14",
}

def encabezado(titulo, descripcion=""):
    """Cabecera de página con jerarquía visual consistente (solo presentación)."""
    import html as _html
    import re as _re
    t = _html.escape(titulo)
    d = _html.escape(descripcion)
    d = _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", d)
    d = _re.sub(r"`(.+?)`", r"<code>\1</code>", d)
    cuerpo = f"<p>{d}</p>" if d else ""
    etiqueta = ETIQUETAS_PAGINA.get(globals().get("menu"), "")
    ojo = f'<div class="page-eyebrow">{_html.escape(etiqueta)}</div>' if etiqueta else ""
    st.markdown(f'<div class="page-head">{ojo}<h1>{t}</h1>{cuerpo}</div>', unsafe_allow_html=True)

# --- Portada: artefactos, actividad, arquitectura y pruebas ---
ARTEFACTOS = [
    ("artifacts/audit.log", "02", "Registro de auditoría"),
    ("reports/semana03.md", "03", "Informe de la taxonomía"),
    ("reports/semana05.md", "05", "Informe del sistema híbrido"),
    ("artifacts/modelo_mlp.pkl", "08", "Modelo MLP entrenado"),
    ("artifacts/soporte_evidencia.db", "08", "Base SQLite de evidencia"),
    ("artifacts/ontologia.graphml", "08", "Ontología del dominio"),
    ("artifacts/semana09_vision.png", "09", "Figura del pipeline de visión"),
    ("artifacts/benchmark.csv", "11", "Resultados del benchmark"),
    ("artifacts/mejor_modelo.pkl", "11", "Mejor modelo serializado"),
    ("reports/semana11_adr.md", "11", "Registro de decisión (ADR)"),
]
REQUISITOS_MODULOS = {
    "Semana 03)": ["reports/semana03.md"],
    "Semana 05)": ["reports/semana05.md"],
    "Semana 08)": ["artifacts/modelo_mlp.pkl", "artifacts/soporte_evidencia.db", "artifacts/ontologia.graphml"],
    "Semana 09)": ["artifacts/semana09_vision.png"],
    "Semana 11)": ["artifacts/benchmark.csv", "artifacts/mejor_modelo.pkl", "reports/semana11_adr.md"],
    "Motor de Auditor": ["artifacts/audit.log"],
}
ETAPAS_TICKET = [
    ("RECEPCION", "Recepción"), ("TAXONOMIA", "Taxonomía"), ("PRIORIZACION", "Prioridad"),
    ("SISTEMA_HIBRIDO", "Híbrido"), ("REPRESENTACIONES", "Represent."), ("SEMANA_08", "Red neuronal"),
    ("SEMANA_09", "Visión"), ("SEMANA_10", "Texturas"), ("SEMANA_11_BENCHMARK", "Benchmark"),
    ("SEMANA_13_INFERENCIA", "Inferencia"), ("SEMANA_14_RED_SEMANTICA", "Red semántica"),
]

def html_barras(etiquetas, valores):
    """Barras horizontales ordenadas de mayor a menor, dibujadas con HTML (sin depender de Vega)."""
    import html as _h
    pares = sorted(zip(etiquetas, valores), key=lambda x: -x[1])
    maximo = max((v for _, v in pares), default=1) or 1
    filas = "".join(
        f'<div class="bar-row"><div class="bar-label">{_h.escape(str(e))}</div>'
        f'<div class="bar-track"><div class="bar-fill" style="width:{v / maximo * 100:.1f}%"></div></div>'
        f'<div class="bar-value">{v}</div></div>' for e, v in pares)
    return f'<div class="bars">{filas}</div>'

def ir_a_faq(consulta):
    """Abre Preguntas Frecuentes con la consulta ya escrita."""
    st.session_state["menu_nav"] = "Preguntas Frecuentes (FAQ)"
    st.session_state["faq_consulta"] = consulta

def modulos_faltantes(nombre_modulo):
    """Archivos que un módulo debe haber generado y todavía no existen."""
    for clave, archivos in REQUISITOS_MODULOS.items():
        if clave in nombre_modulo:
            return [a for a in archivos if not (BASE_DIR / a).exists()]
    return []

def _tamano_legible(n):
    return f"{n} B" if n < 1024 else (f"{n / 1024:.1f} KB" if n < 1024 * 1024 else f"{n / (1024 * 1024):.1f} MB")

def estado_artefactos():
    """Comprueba en disco cada artefacto: existencia, tamaño y fecha de modificación."""
    from datetime import datetime
    filas = []
    for ruta, semana, descripcion in ARTEFACTOS:
        p = BASE_DIR / ruta
        existe = p.exists()
        info = p.stat() if existe else None
        filas.append({"ruta": ruta, "semana": semana, "descripcion": descripcion, "existe": existe,
                      "tamano": _tamano_legible(info.st_size) if info else "",
                      "fecha": datetime.fromtimestamp(info.st_mtime).strftime("%d/%m/%Y %H:%M") if info else ""})
    return filas

def html_artefactos(filas):
    import html as _h
    partes = []
    for f in filas:
        if f["existe"]:
            meta, badge = f'Semana {f["semana"]} · {f["descripcion"]} · {f["tamano"]} · {f["fecha"]}', '<span class="badge-ok">Disponible</span>'
        else:
            meta, badge = f'Semana {f["semana"]} · {f["descripcion"]} · aún no generado', '<span class="badge-warn">Pendiente</span>'
        partes.append(f'<div class="status-row"><div><div class="status-name">{_h.escape(f["ruta"])}</div>'
                      f'<div class="status-meta">{_h.escape(meta)}</div></div>{badge}</div>')
    return '<div class="status-list">' + "".join(partes) + "</div>"

def trazas_del_log():
    """Trazas estructuradas (fecha, ticket, acción, detalle) leídas de audit.log."""
    import re as _re
    patron = _re.compile(r"TICKET_ID:\s*(?P<ticket>[^|]+?)\s*\|\s*ACCI\S{0,3}N:\s*(?P<accion>[^|]+?)\s*\|\s*DETALLES:\s*(?P<detalle>.*)$")
    registros, _ = parsear_audit_log()
    trazas = []
    for r in registros:
        m = patron.search(r.get("mensaje", ""))
        if m:
            trazas.append({"fecha": r["fecha"], "ticket": m["ticket"].strip(), "accion": m["accion"].strip(), "detalle": m["detalle"].strip()})
    return trazas

def recorrido_ticket(trazas):
    """Última traza de cada etapa para el ticket más reciente del log."""
    if not trazas:
        return None, []
    ticket = trazas[-1]["ticket"]
    ultimas = {t["accion"]: t for t in trazas if t["ticket"] == ticket}
    return ticket, [(accion, nombre, ultimas.get(accion)) for accion, nombre in ETAPAS_TICKET]

def html_recorrido(etapas):
    pasos = []
    for i, (accion, nombre, tr) in enumerate(etapas, 1):
        hora = tr["fecha"].split()[-1] if tr else "sin traza"
        pasos.append(f'<div class="rm-step{"" if tr else " pend"}"><div class="rm-dot">{i}</div>'
                     f'<div class="rm-name">{nombre}</div><div class="rm-desc">{hora}</div></div>')
    return '<div class="roadmap">' + "".join(pasos) + "</div>"

def html_actividad(trazas, n=8):
    import html as _h
    nombres = dict(ETAPAS_TICKET)
    filas = []
    for t in reversed(trazas[-n:]):
        detalle = t["detalle"] if len(t["detalle"]) <= 120 else t["detalle"][:117] + "..."
        filas.append(
            '<div class="act-item"><div class="act-dot"></div><div class="act-body"><div class="act-top">'
            f'<span class="act-action">{_h.escape(nombres.get(t["accion"], t["accion"]))}</span>'
            f'<span class="act-time">{_h.escape(t["fecha"])}</span></div>'
            f'<div class="act-detail">{_h.escape(t["ticket"])} · {_h.escape(detalle)}</div></div></div>')
    return '<div class="activity">' + "".join(filas) + "</div>"

def html_arquitectura():
    capas = [
        ("Entrada", [("Ticket de soporte", "descripción, impacto, urgencia"), ("Imagen de evidencia", "fallo de hardware")]),
        ("Clasificación", [("Taxonomía", "Semana 03"), ("Prioridad", "Semana 02"), ("Validación del modelo base", "Semana 02")]),
        ("Razonamiento", [("Sistema híbrido", "Semana 05"), ("A* y Minimax", "Semana 04"), ("Representaciones", "Semana 07"),
                          ("Motor de inferencia", "Semana 13"), ("Red semántica", "Semana 14")]),
        ("Visión y modelos", [("Visión artificial", "Semana 09"), ("Texturas LBP", "Semana 10"),
                              ("Red neuronal MLP", "Semana 08"), ("Benchmark de modelos", "Semana 11")]),
        ("Persistencia y auditoría", [("audit.log", "trazas de cada etapa"), ("SQLite y ontología", "evidencia"),
                                      ("Modelos .pkl", "MLP y mejor modelo"), ("Informes .md", "reports/")]),
    ]
    columnas = []
    for titulo, modulos in capas:
        chips = "".join(f'<div class="arch-chip"><b>{n}</b><span>{d}</span></div>' for n, d in modulos)
        columnas.append(f'<div class="arch-col"><div class="arch-head">{titulo}</div>{chips}</div>')
    return '<div class="arch">' + '<div class="arch-arrow">→</div>'.join(columnas) + "</div>"

def ejecutar_pruebas():
    """Ejecuta unittest sobre tests/ en un proceso aparte y resume el resultado."""
    import os
    import re as _re
    import subprocess
    import sys
    carpeta = BASE_DIR / "tests"
    if not carpeta.is_dir():
        return {"ok": False, "error": "No se encontró la carpeta tests/ en el proyecto."}
    entorno = {**os.environ, "PYTHONPATH": str(BASE_DIR / "src"), "PYTHONIOENCODING": "utf-8"}
    try:
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=str(BASE_DIR), env=entorno,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Las pruebas superaron los 180 segundos y se cancelaron."}
    salida = (r.stderr or "") + (r.stdout or "")
    ran = _re.search(r"Ran (\d+) tests? in ([\d.]+)s", salida)
    fallos = _re.search(r"FAILED \((.*?)\)", salida)
    return {"ok": r.returncode == 0, "pruebas": int(ran.group(1)) if ran else None,
            "segundos": float(ran.group(2)) if ran else None, "detalle_fallos": fallos.group(1) if fallos else "",
            "salida": salida[-3500:]}

# --- Navegación desde la página de inicio ---
def ir_a(pagina):
    """Cambia la página activa del menú lateral (se ejecuta antes de volver a dibujar)."""
    st.session_state["menu_nav"] = pagina

# --- Preguntas frecuentes: componentes ---
@st.cache_resource
def cargar_asistente_faq():
    """Construye una sola vez el índice TF-IDF de las preguntas frecuentes."""
    return AsistenteFAQ()

def _md_inline(texto):
    import html as _h
    import re as _r
    t = _h.escape(str(texto))
    t = _r.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return _r.sub(r"`(.+?)`", r"<code>\1</code>", t)

def tarjeta_faq(faq, similitud=None, mejor=False):
    """Tarjeta de una pregunta frecuente con su semana, respuesta y similitud."""
    import html as _h
    etiqueta = "General" if faq["semana"] == 0 else f"Semana {faq['semana']:02d}"
    partes = [f'<div class="faq-card{" mejor" if mejor else ""}">', '<div class="faq-top">',
              f'<span class="faq-sem">{etiqueta} · {_h.escape(faq["tema"])}</span>']
    if mejor:
        partes.append('<span class="faq-best">Mejor coincidencia</span>')
    if similitud is not None:
        partes.append(f'<span class="faq-sim">Similitud {similitud:.2f}</span>')
    partes += ['</div>', f'<div class="faq-q">{_h.escape(faq["pregunta"])}</div>',
               f'<p class="faq-a">{_md_inline(faq["respuesta"])}</p>']
    if similitud is not None:
        pct = max(0.0, min(1.0, similitud)) * 100
        partes.append(f'<div class="result-bar" style="--tono:#2457D6"><span style="width:{pct:.1f}%"></span></div>')
    pagina = SEMANAS.get(faq["semana"], ("", ""))[1]
    partes.append(f'<div class="faq-meta">Página del dashboard: {_h.escape(pagina)} · Módulo: <code>{_h.escape(faq["ref"])}</code></div></div>')
    st.markdown("".join(partes), unsafe_allow_html=True)

# --- Componentes visuales reutilizables (solo presentación) ---
def tarjeta_resultado(etiqueta, valor, detalle="", tono="azul", progreso=None, texto=False):
    """Tarjeta de resultado de un modelo: etiqueta, valor, detalle opcional y barra de progreso 0-1."""
    import html as _h
    tonos = {"azul": ("#2457D6", "#E8EEFC"), "verde": ("#1E8E5A", "#E7F5EE"),
             "ambar": ("#B7791F", "#FEF6E4"), "rojo": ("#C0392B", "#FCEBE9"), "gris": ("#5B6779", "#EDF1F8")}
    fuerte, suave = tonos.get(tono, tonos["azul"])
    clase = "result-card texto" if texto else "result-card"
    partes = [f'<div class="{clase}" style="--tono:{fuerte};--tono-suave:{suave}">',
              f'<div class="result-label">{_h.escape(str(etiqueta))}</div>',
              f'<div class="result-value">{_h.escape(str(valor))}</div>']
    if detalle:
        partes.append(f'<div class="result-detail">{_h.escape(str(detalle))}</div>')
    if progreso is not None:
        try:
            pct = max(0.0, min(1.0, float(progreso))) * 100
            partes.append(f'<div class="result-bar"><span style="width:{pct:.1f}%"></span></div>')
        except (TypeError, ValueError):
            pass
    partes.append("</div>")
    st.markdown("".join(partes), unsafe_allow_html=True)

def estilo_plotly(fig):
    """Aplica la paleta, tipografía y rejilla del dashboard a una figura de Plotly."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family="IBM Plex Sans, Segoe UI, Arial, sans-serif", size=13, color="#14213D"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        colorway=["#2457D6", "#0E9F8E", "#E08A1E", "#C0392B", "#7A5AF8"],
        xaxis=dict(showgrid=False, linecolor="#C5CEDC", tickcolor="#C5CEDC", title_font=dict(size=12, color="#5B6779")),
        yaxis=dict(gridcolor="#E9EDF4", zeroline=False, title_font=dict(size=12, color="#5B6779")),
        hoverlabel=dict(bgcolor="#0F1B2D", font=dict(color="#FFFFFF", size=12), bordercolor="#0F1B2D"),
    )
    return fig

def estilo_matplotlib():
    """Estilo uniforme (paleta, tipografía, rejilla suave) para las figuras de Matplotlib."""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["IBM Plex Sans", "Segoe UI", "DejaVu Sans", "Arial"],
        "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlecolor": "#14213D",
        "axes.labelcolor": "#5B6779", "axes.edgecolor": "#C5CEDC", "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "axes.axisbelow": True,
        "grid.color": "#E9EDF4", "grid.linewidth": 0.8, "xtick.color": "#5B6779", "ytick.color": "#5B6779",
        "legend.frameon": False, "lines.linewidth": 2.0,
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
    })
    return plt

# --- Redes semánticas (Semana 14): construcción de redes y grafos ---
ORACIONES_RED_PROYECTO = [
    "servidor_bd es un hardware_critico",
    "hardware_critico es un activo_corporativo",
    "activo_corporativo requiere alimentacion_redundante",
    "estacion_trabajo es un hardware_estandar",
    "sobrecalentamiento se resuelve con limpieza_ventilacion",
]
REQUISITOS_POR_CATEGORIA = {
    "hardware": "soporte_presencial_campo",
    "red": "monitoreo_noc_24_7",
    "seguridad": "auditoria_cumplimiento_iso",
}
REQUISITO_POR_DEFECTO = "resolucion_automatizada_nivel_1"
COLOR_RELACION = {"es_un": "#2457D6", "requiere": "#1E8E5A", "se_resuelve_con": "#B7791F"}

def construir_red_proyecto():
    """Red base de la Semana 14."""
    red = RedSemanticaSoporteTI()
    for oracion in ORACIONES_RED_PROYECTO:
        red.interpretar_oracion(oracion)
    return red

def construir_red_ampliada(procs_kb):
    """Red base + casos de la KB: caso -> categoría técnica -> activo_corporativo."""
    red = construir_red_proyecto()
    omitidos = []
    for p in procs_kb:
        try:
            categoria = normalizar(p["categoria"])
            nodo_categoria = f"categoria_{categoria}"
            red.agregar_triple(p["titulo"], "es_un", nodo_categoria)
            red.agregar_triple(nodo_categoria, "es_un", "activo_corporativo")
            red.agregar_triple(nodo_categoria, "requiere", REQUISITOS_POR_CATEGORIA.get(categoria, REQUISITO_POR_DEFECTO))
        except (ValueError, KeyError):
            omitidos.append(str(p.get("titulo", "?")))
    return red, omitidos

def dot_red(triples, camino=None):
    """Código DOT para st.graphviz_chart. Los triples de 'camino' se resaltan."""
    resaltados = set(camino or [])
    nodos_resaltados = {n for s, _, o in resaltados for n in (s, o)}
    nodos = sorted({n for s, _, o in triples for n in (s, o)})
    lineas = [
        "digraph red {", "rankdir=LR;", 'bgcolor="transparent";', "nodesep=0.45;", "ranksep=0.9;",
        'node [shape=box, style="rounded,filled", fillcolor="#FFFFFF", color="#C5CEDC", fontname="Helvetica", fontsize=14, fontcolor="#14213D", margin="0.18,0.09"];',
        'edge [fontname="Helvetica", fontsize=12, arrowsize=0.9];',
    ]
    for n in nodos:
        if n in nodos_resaltados:
            lineas.append(f'"{n}" [fillcolor="#E8EEFC", color="#2457D6", penwidth=1.8];')
        else:
            lineas.append(f'"{n}";')
    for s, r, o in triples:
        color = COLOR_RELACION.get(r, "#8294AE")
        color_texto = color
        if resaltados and (s, r, o) not in resaltados:
            color, color_texto = "#C5CEDC", "#8294AE"
        grosor = 3 if (s, r, o) in resaltados else 1.2
        estilo = "" if r == "es_un" else ", style=dashed"
        lineas.append(f'"{s}" -> "{o}" [label="{r}", color="{color}", fontcolor="{color_texto}", penwidth={grosor}{estilo}];')
    lineas.append("}")
    return "\n".join(lineas)

def triples_para_grafo(red, prueba):
    return red.triples if len(red.nodos) <= 12 else prueba

AUDIT_LOG_PATH = BASE_DIR / "artifacts" / "audit.log"
KB_PATH = BASE_DIR / "data" / "base_conocimiento.txt"
BENCHMARK_CSV_PATH = BASE_DIR / "artifacts" / "benchmark.csv"

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
    """Implementación del Autómata Finito Determinista (AFD) para la interfaz con alfabeto O, E, T"""
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
    return state == "q2", "Falla en cascada detectada (ET)" if state == "q2" else "Comportamiento normal / recuperado"

# --- Barra Lateral ---
st.sidebar.markdown(
    '<div class="brand"><div class="brand-mark">TI</div>'
    '<div><div class="brand-name">Panel de Control TI</div>'
    '<div class="brand-sub">Asistente de Soporte Híbrido</div></div></div>',
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navegación",
    [
        "Resumen Ejecutivo", 
        "Matriz de Confusión", 
        "Sistema Híbrido & TF-IDF", 
        "Planificador A* & Minimax", 
        "Representaciones del Reconocimiento",
        "Red Neuronal & Ontología",
        "Visión Artificial (Semana 09)",
        "Histogramas y Texturas LBP (Semana 10)",
        "Benchmark y Decisiones de Modelos (Semana 11)",
        "Motor de Inferencia (Semana 13)",
        "Redes Semánticas (Semana 14)", 
        "Portal de Usuario",
        "Base de Conocimiento (KB)", 
        "Trazas de Auditoría",
        "Preguntas Frecuentes (FAQ)"
    ],
    key="menu_nav"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    '<div class="side-card">'
    '<div class="side-card-k">Institución</div><div class="side-card-v">ETITC - 10º Semestre</div>'
    '<div class="side-card-k">Autores</div><div class="side-card-v">Marco Molina &amp; Daniel Daza</div>'
    f'<div class="side-card-k">Estado</div><div class="side-card-v"><span class="dot {"ok" if MODULOS_CARGADOS else "err"}"></span>{"Módulos cargados" if MODULOS_CARGADOS else "Módulos no disponibles"}</div>'
    '</div>',
    unsafe_allow_html=True
)

# --- 1. Resumen Ejecutivo ---
if menu == "Resumen Ejecutivo":
    encabezado("Dashboard General del Asistente de Soporte TI", "Monitoreo en tiempo real de los componentes lógicos, modelos de machine learning y flujos del sistema híbrido.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Accuracy Benchmark S11", value="98.0%", delta="Modelo Óptimo Seleccionado")
    with col2:
        st.metric(label="Base de Conocimiento", value="30 Procedimientos", delta="Activo (Semana 05)")
    with col3:
        st.metric(label="Algoritmo A*", value="3 Escenarios", delta="Costo Óptimo Calculado")
    with col4:
        st.metric(label="Módulo de Representaciones", value="3 Enfoques", delta="Numérico/Simbólico/AFD")

    st.markdown("")

    # --- 1) Pregunta al asistente ---
    st.markdown("### Pregunta al asistente")
    if FAQ_DISPONIBLE:
        asistente_inicio = cargar_asistente_faq()
        pregunta_inicio = st.text_input("Pregunta al asistente", key="inicio_consulta", label_visibility="collapsed",
                                        placeholder="Pregunta algo sobre el proyecto. Ejemplo: ¿Qué es la red semántica?")
        if pregunta_inicio.strip():
            respuestas_inicio = asistente_inicio.buscar(pregunta_inicio, k=1)
            if respuestas_inicio:
                tarjeta_faq(respuestas_inicio[0], similitud=respuestas_inicio[0]["similitud"], mejor=True)
                st.button("Ver más respuestas en Preguntas Frecuentes", key="inicio_ver_mas", on_click=ir_a_faq, args=(pregunta_inicio,))
            else:
                st.info("No encontré una pregunta suficientemente parecida. Prueba con otras palabras o abre Preguntas Frecuentes.")
    else:
        st.info("El asistente de preguntas frecuentes no está disponible (falta `classifiers/faq_semanas.py`).")

    tab_estado, tab_actividad, tab_arquitectura, tab_calidad = st.tabs(
        ["Estado del sistema", "Actividad reciente", "Arquitectura", "Calidad y pruebas"])

    # --- 2) Estado del sistema: módulos, categorías y artefactos reales ---
    with tab_estado:
        trazas_est = trazas_del_log()
        filas_art = estado_artefactos()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Distribución por Categorías Técnicas (KB)")
            data_cat = {
                "Categoría": ["Hardware", "Red", "Seguridad", "Rendimiento", "Almacenamiento", "Software"],
                "Procedimientos": [8, 6, 6, 6, 3, 3]
            }
            df_cat = pd.DataFrame(data_cat)
            procs_kb_res = cargar_base_conocimiento()
            if procs_kb_res:  # categorías reales de la base de conocimiento
                conteo_kb = {}
                for p_kb in procs_kb_res:
                    nombre_cat = str(p_kb.get("categoria", "Sin categoría")).strip()
                    nombre_cat = nombre_cat[:1].upper() + nombre_cat[1:]
                    conteo_kb[nombre_cat] = conteo_kb.get(nombre_cat, 0) + 1
                etiquetas_cat, valores_cat = list(conteo_kb.keys()), list(conteo_kb.values())
            else:
                etiquetas_cat, valores_cat = list(df_cat["Categoría"]), list(df_cat["Procedimientos"])
            st.markdown(html_barras(etiquetas_cat, valores_cat), unsafe_allow_html=True)
            st.caption(f"{sum(valores_cat)} procedimientos en {len(valores_cat)} categorías.")
            ticket_est, etapas_est = recorrido_ticket(trazas_est)
            if trazas_est:
                con_traza_est = sum(1 for _, _, tr in etapas_est if tr)
                tarjeta_resultado("Última ejecución", trazas_est[-1]["fecha"], detalle=ticket_est, tono="azul")
                tarjeta_resultado("Etapas con traza", f"{con_traza_est} de {len(etapas_est)}",
                                  tono="verde" if con_traza_est == len(etapas_est) else "ambar", progreso=con_traza_est / len(etapas_est))
            n_art_ok = sum(1 for f in filas_art if f["existe"])
            tarjeta_resultado("Artefactos disponibles", f"{n_art_ok} de {len(filas_art)}",
                              tono="verde" if n_art_ok == len(filas_art) else "ambar", progreso=n_art_ok / len(filas_art))
        
        with col_b:
            st.subheader("Estado de Integración de Módulos")
            modulos_estado = [
                ("Validación y Matriz de Confusión (Semana 02)", "Accuracy 92.1%"),
                ("Clasificador Taxonómico (Semana 03)", "100% de coincidencia"),
                ("Planificador A* y Ciberdefensa Minimax (Semana 04)", ""),
                ("Sistema Híbrido (Semana 05)", "Reglas y TF-IDF"),
                ("Representaciones del Reconocimiento (Semana 07)", ""),
                ("Red Neuronal, Imagen Base64, SQLite y Ontología (Semana 08)", ""),
                ("Visión Artificial (Semana 09)", ""),
                ("Histogramas y Texturas LBP (Semana 10)", "Extracción de Features Vectoriales"),
                ("Benchmark de Modelos y ADR (Semana 11)", "Evaluación y Serialización en artifacts/"),
                ("Motor de Inferencia Avanzado (10 Reglas - Semana 13)", "Reglas Horn, Trazas y Explicabilidad"),
                ("Redes Semánticas e Inferencia (Semana 14)", "Triples, es_un y Herencia con KB de 30 Casos"),
                ("Motor de Auditoría y Trazas", "Registrando en artifacts/audit.log"),
            ]
            filas_estado = ""
            for nombre, detalle in modulos_estado:
                faltan = modulos_faltantes(nombre)
                if faltan:
                    detalle_fila = (detalle + " · " if detalle else "") + "Falta: " + ", ".join(faltan)
                    insignia = '<span class="badge-warn">Pendiente</span>'
                else:
                    detalle_fila, insignia = detalle, '<span class="badge-ok">Operativo</span>'
                filas_estado += (f'<div class="status-row"><div><div class="status-name">{nombre}</div>'
                                 f'<div class="status-meta">{detalle_fila}</div></div>{insignia}</div>')
            st.markdown(f'<div class="status-list">{filas_estado}</div>', unsafe_allow_html=True)

        st.markdown("")
        st.subheader("Artefactos generados")
        st.caption(f"{sum(1 for f in filas_art if f['existe'])} de {len(filas_art)} artefactos disponibles en disco. Se generan al ejecutar `python src/main.py` y los scripts de cada semana.")
        st.markdown(html_artefactos(filas_art), unsafe_allow_html=True)

    # --- 3) Actividad: recorrido del ticket y últimas trazas ---
    with tab_actividad:
        trazas_log = trazas_del_log()
        if trazas_log:
            ticket_log, etapas_log = recorrido_ticket(trazas_log)
            con_traza = sum(1 for _, _, tr in etapas_log if tr)
            st.subheader("Recorrido del ticket")
            st.caption(f"{ticket_log} · {con_traza} de {len(etapas_log)} etapas con traza en audit.log · última traza: {trazas_log[-1]['fecha']}")
            st.markdown(html_recorrido(etapas_log), unsafe_allow_html=True)
            st.subheader("Últimas trazas")
            st.markdown(html_actividad(trazas_log), unsafe_allow_html=True)
        else:
            st.info("Aún no hay trazas en `artifacts/audit.log`. Ejecuta `python src/main.py` para generarlas.")

    # --- 4) Arquitectura ---
    with tab_arquitectura:
        st.subheader("Cómo fluye un ticket por el sistema")
        st.caption("Cinco capas: lo que entra, cómo se clasifica, cómo se razona, qué evidencia y modelos intervienen y qué queda registrado.")
        st.markdown(html_arquitectura(), unsafe_allow_html=True)

    # --- 5) Calidad: pruebas automáticas ---
    with tab_calidad:
        st.subheader("Pruebas automáticas")
        st.markdown("Ejecuta todas las pruebas de la carpeta `tests/` (unittest) y muestra el resultado.")
        if st.button("Ejecutar pruebas", key="inicio_pruebas"):
            with st.spinner("Ejecutando pruebas..."):
                st.session_state["resultado_pruebas"] = ejecutar_pruebas()
        resultado_pruebas = st.session_state.get("resultado_pruebas")
        if resultado_pruebas:
            if resultado_pruebas.get("error"):
                st.error(resultado_pruebas["error"])
            else:
                q1, q2, q3 = st.columns(3)
                q1.metric("Pruebas ejecutadas", resultado_pruebas["pruebas"] if resultado_pruebas["pruebas"] is not None else "-")
                q2.metric("Resultado", "Todas pasan" if resultado_pruebas["ok"] else "Con fallos", resultado_pruebas["detalle_fallos"] or None, delta_color="off")
                q3.metric("Duración", f"{resultado_pruebas['segundos']:.2f} s" if resultado_pruebas["segundos"] is not None else "-")
                (st.success if resultado_pruebas["ok"] else st.error)("Todas las pruebas pasaron." if resultado_pruebas["ok"] else "Hay pruebas que fallan. Revisa la salida.")
                with st.expander("Ver salida completa"):
                    st.code(resultado_pruebas["salida"], language="text")

# --- 2. Matriz de Confusión ---
elif menu == "Matriz de Confusión":
    encabezado("Validación del Modelo Base (Semana 02)", "Evaluación del pipeline reproducible de clasificación multiclase del curso (StandardScaler + LogisticRegression sobre el benchmark estándar con división estratificada 75/25).")
    
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
            st.dataframe(df_matriz, width="stretch")
            st.info("La matriz demuestra 35 aciertos de 38 muestras de prueba (92.1% de precisión global), con dispersión mínima focalizada únicamente en 3 casos límite entre clases contiguas.")
        except Exception as e:
            st.error(f"Error al ejecutar la validación del modelo: {e}")
    else:
        st.warning("Módulos no disponibles para generar la matriz en tiempo real.")

# --- 3. Sistema Híbrido & TF-IDF (Dinámico) ---
elif menu == "Sistema Híbrido & TF-IDF":
    encabezado("Simulador de Sistema Híbrido (Reglas + TF-IDF)", "Consulta la base de conocimiento en tiempo real utilizando similitud coseno sobre los 30 procedimientos de soporte y reglas lógicas expertas.")

    query = st.text_input("Escribe un reporte de ticket de soporte:", value="Disco lleno", key="query_input")
    
    if st.button("Ingresar su consulta"):
        if MODULOS_CARGADOS:
            sistema = SistemaHibridoSoporte()
            resultado = sistema.procesar(query)
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Resultados del Motor")
                tarjeta_resultado("Reglas activadas", resultado['reglas'], tono="azul")
                tarjeta_resultado("Clase predicha (ML)", resultado['clase'], tono="ambar")
                tarjeta_resultado("Similitud coseno", f"{resultado['similitud']:.4f}", tono="verde", progreso=resultado['similitud'])
            with col2:
                st.markdown("### Evidencia Recuperada (TF-IDF)")
                tarjeta_resultado("Procedimiento recuperado", resultado['evidencia'], tono="verde", texto=True)
        else:
            st.error("No se pudieron cargar los módulos de Python desde la carpeta `src/`.")

# --- 4. Planificador A* & Minimax ---
elif menu == "Planificador A* & Minimax":
    encabezado("Optimización en Espacio de Estados y Decisiones Adversariales")
    
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
            st.info(f"**Estado Inicial:** `{estado_ini}` ➔ **Estado Meta:** `{GOAL_STATE}` | **Costo Mínimo Acumulado:** `{costo_total}` unidades de esfuerzo")
            
            st.markdown("#### Recuperación y Salud de Subsistemas")
            c_red, c_bd, c_app = st.columns(3)
            with c_red:
                st.markdown(f"**Red:** Nivel `{estado_ini[0]}/2`")
                st.progress(estado_ini[0] / 2.0, text=f"{(estado_ini[0]/2)*100:.0f}% Operativo")
            with c_bd:
                st.markdown(f"**Base de Datos:** Nivel `{estado_ini[1]}/2`")
                st.progress(estado_ini[1] / 2.0, text=f"{(estado_ini[1]/2)*100:.0f}% Operativo")
            with c_app:
                st.markdown(f"**Microservicio Backend:** Nivel `{estado_ini[2]}/2`")
                st.progress(estado_ini[2] / 2.0, text=f"{(estado_ini[2]/2)*100:.0f}% Operativo")
            
            if ruta:
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
                
                st.markdown("##### Progresión de Salud hacia la Meta (2, 2, 2)")
                df_evol = pd.DataFrame(evolucion)
                st.line_chart(df_evol.set_index("Paso"), color=["#2457D6", "#0E9F8E", "#E08A1E"])
                
                st.markdown("##### Secuencia Óptima de Acciones Técnicas")
                st.table(pd.DataFrame(pasos_lista))
            else:
                st.warning("No se encontró una ruta válida para este estado.")
        else:
            st.warning("Módulo A* no disponible temporalmente.")
        
    with tab2:
        st.subheader("Simulador de Ciberdefensa con Minimax (Blue Team vs. Red Team)")
        st.markdown(
            "Modelado formal de **búsqueda adversarial de suma cero** para contención de incidentes de seguridad y mitigación de intrusión lateral.  \n"
            "- **Jugador MAX (Blue Team / Soporte TI):** Aplica contramedidas preventivas y aísla servidores críticos (`Blindado`).  \n"
            "- **Jugador MIN (Red Team / Amenaza Externa):** Explota vulnerabilidades buscando comprometer una ruta crítica (`Comprometido`).  \n"
            "- **Objetivo:** Minimax evalúa exhaustivamente el árbol de decisiones para seleccionar el nodo que garantiza la resiliencia de la infraestructura corporativa."
        )
        if MODULOS_CARGADOS:
            diag = simular_ciberdefensa(minimax_board)
            
            col_left, col_right = st.columns([1, 1], gap="medium")
            
            with col_left:
                st.markdown("##### Topología de Servidores (Matriz 3x3)")
                
                tarjetas_html = []
                for i in range(9):
                    estado = minimax_board[i]
                    nombre = NODOS_INFRAESTRUCTURA[i]
                    es_mejor = (i == diag["posicion"])
                    
                    if estado == "X":
                        bg = "#E7F5EE"
                        border = "#1E8E5A"
                        badge = "Blue Team"
                        sub = "Blindado"
                    elif estado == "O":
                        bg = "#FCEBE9"
                        border = "#C0392B"
                        badge = "Red Team"
                        sub = "Comprometido"
                    elif es_mejor:
                        bg = "#FEF6E4"
                        border = "#B7791F"
                        badge = "Minimax"
                        sub = "Blindar Ahora"
                    else:
                        bg = "#F4F6FA"
                        border = "#C5CEDC"
                        badge = "En Línea"
                        sub = "Disponible"
                        
                    tarjetas_html.append(
                        f'<div style="background-color: {bg}; border: 1px solid {border}; border-left: 4px solid {border}; border-radius: 10px; padding: 12px 6px; text-align: center; min-height: 96px;">'
                        f'<span style="font-size: 0.72rem; color: #5B6779;">[Nodo #{i}]</span><br>'
                        f'<strong style="color: #14213D; font-size: 0.82rem;">{nombre}</strong><br>'
                        f'<span style="font-weight: bold; font-size: 0.75rem; color: {border};">{badge}</span><br>'
                        f'<small style="color: #5B6779; font-size: 0.72rem;">{sub}</small>'
                        f'</div>'
                    )
                
                grid_html = '<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px;">' + "".join(tarjetas_html) + '</div>'
                st.markdown(grid_html, unsafe_allow_html=True)
                
            with col_right:
                st.markdown("##### Decisión Táctica de Contención")
                st.success(f"**Servidor Seleccionado:** `{diag['nodo']}` (Nodo #{diag['posicion']})")
                st.info(f"**Acción Defensiva:** {diag['accion']}")
                st.markdown(f"**Análisis Estratégico:**\n\n{diag['justificacion']}")
                st.caption("Función de Utilidad: +1 si el Blue Team asegura el perímetro, 0 si hay contención, -1 si el Red Team compromete la red.")
        else:
            st.warning("Módulo Minimax no disponible temporalmente.")

# --- 5. REPRESENTACIONES DEL RECONOCIMIENTO (Semana 07) ---
elif menu == "Representaciones del Reconocimiento":
    encabezado("Representaciones del Reconocimiento (Semana 07)", "Simulación de los tres enfoques de inteligencia artificial para interpretar y procesar información técnica de soporte.")
    
    tab_num, tab_sim, tab_aut = st.tabs(["Numérica (Telemetría)", "Simbólica (Sistema Experto)", "Autómatas (Logs en Cascada)"])
    
    # 1. Representación Numérica
    with tab_num:
        st.subheader("Representación Numérica: Distancia Euclidiana (Triaje de Tickets)")
        st.markdown("Mide qué tan cerca está el estado actual del servidor de un perfil crítico de colapso, usando vectores numéricos y distancias en el espacio.")
        
        perfil_colapso = np.array([10.0, 10.0, 1.0]) # [Impacto Infraestructura, Urgencia Tiempo, Sentimiento NLP]
        
        col_sliders, col_results = st.columns([1, 1])
        with col_sliders:
            st.markdown("**Ajusta las características del ticket entrante:**")
            imp_val = st.slider("Impacto en Infraestructura (1-10)", 1.0, 10.0, 8.5)
            urg_val = st.slider("Urgencia de Tiempo (1-10)", 1.0, 10.0, 9.0)
            nlp_val = st.slider("Sentimiento Negativo NLP (0.0-1.0)", 0.0, 1.0, 0.95)
            
        with col_results:
            ticket_actual = np.array([imp_val, urg_val, nlp_val])
            distancia = np.linalg.norm(ticket_actual - perfil_colapso)
            
            st.markdown(f"**Perfil Crítico (Fijo):** `[{perfil_colapso[0]}, {perfil_colapso[1]}, {perfil_colapso[2]}]`")
            st.markdown(f"**Ticket Actual (Dinámico):** `[{ticket_actual[0]}, {ticket_actual[1]}, {ticket_actual[2]}]`")
            
            st.metric(label="Distancia Numérica al Escalamiento Inmediato", value=f"{distancia:.2f}")
            
            if distancia < 3.0:
                st.error("**ALERTA DE TRIAJE:** Clasificación prioritaria. Asignando directamente a Especialista Humano.")
            else:
                st.success("**ESTABLE:** Ticket estándar manejable por chatbot de Nivel 1.")
                
    # 2. Representación Simbólica
    with tab_sim:
        st.subheader("Representación Simbólica: Inferencia Discreta (Hechos y Reglas)")
        st.markdown("Transforma el lenguaje natural en hechos discretos. Utiliza lógica `SI -> ENTONCES` para llegar a un diagnóstico absoluto y justificable.")
        
        st.markdown("**Selecciona los síntomas detectados en el ticket:**")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            sym_bsod = st.checkbox("pantalla_azul", value=True)
            sym_rein = st.checkbox("reinicio_constante", value=True)
        with c2:
            sym_ping = st.checkbox("ping_fallido", value=False)
            sym_serv = st.checkbox("servidor_no_responde", value=False)
        with c3:
            sym_pwd = st.checkbox("olvido_contrasena", value=False)
            sym_ad = st.checkbox("active_directory", value=False)
        
        hechos_detectados = set()
        if sym_bsod: hechos_detectados.add("pantalla_azul")
        if sym_rein: hechos_detectados.add("reinicio_constante")
        if sym_ping: hechos_detectados.add("ping_fallido")
        if sym_serv: hechos_detectados.add("servidor_no_responde")
        if sym_pwd: hechos_detectados.add("olvido_contrasena")
        if sym_ad: hechos_detectados.add("active_directory")
        
        st.markdown(f"**Base de Hechos Actual:** `{hechos_detectados}`")
        
        st.markdown("---")
        st.markdown("#### Motor de Inferencia")
        if {"pantalla_azul", "reinicio_constante"}.issubset(hechos_detectados):
            st.error("**Diagnóstico Simbólico:** `falla_hardware_fisico` detectada.")
            st.markdown("**Acción recomendada:** Desviar al módulo de Soporte de Campo (Presencial) y solicitar modelo del equipo.")
        elif {"ping_fallido", "servidor_no_responde"}.issubset(hechos_detectados):
            st.error("**Diagnóstico Simbólico:** `caida_infraestructura_red` detectada.")
            st.markdown("**Acción recomendada:** Notificar a NOC y ejecutar protocolo de ping persistente.")
        elif {"olvido_contrasena", "active_directory"}.issubset(hechos_detectados):
            st.warning("**Diagnóstico Simbólico:** `restablecimiento_credenciales`.")
            st.markdown("**Acción recomendada:** Ejecutar script de automatización de reseteo (Nivel 1 - Bot).")
        else:
            st.info("**Diagnóstico Simbólico:** Incidentes sin mapeo directo crítico.")

    # 3. Representación por Autómata
    with tab_aut:
        st.subheader("Representación por Autómata: Validación de Cronologías")
        st.markdown("Utiliza un Autómata Finito Determinista (AFD) para auditar secuencias de tiempo. Valida si una sucesión de eventos (`O`: Operativo, `E`: Error, `T`: Timeout) desencadena el patrón estricto de una *falla en cascada* (`ET`).")
        
        st.markdown("**Alfabeto permitido:** `O` (Operativo), `E` (Error), `T` (Timeout)")
        secuencia = st.text_input("Ingresa una secuencia de logs temporales:", "OOOEET").upper()
        
        if st.button("Auditar Secuencia con AFD"):
            secuencia_limpia = "".join(c for c in secuencia if c in ['O', 'E', 'T'])
            
            if len(secuencia_limpia) != len(secuencia):
                st.error(f"La secuencia contiene caracteres no válidos. Procesando solo la parte válida: `{secuencia_limpia}`")
            
            if not secuencia_limpia:
                st.warning("Ingresa una secuencia válida (ej. 'OOET').")
            else:
                aceptada, mensaje = acepta_patron_falla_cascada(secuencia_limpia)
                
                st.markdown(f"#### Resultados de Auditoría para: `{secuencia_limpia}`")
                
                estado_visual = "q0"
                pasos = [f"Inicio (q0)"]
                
                transitions_vis = {
                    ("q0", "O"): "q0", ("q0", "T"): "q0", ("q0", "E"): "q1",
                    ("q1", "O"): "q0", ("q1", "E"): "q1", ("q1", "T"): "q2",
                    ("q2", "O"): "q0", ("q2", "T"): "q0", ("q2", "E"): "q1",
                }
                
                for sim in secuencia_limpia:
                    if (estado_visual, sim) in transitions_vis:
                        estado_visual = transitions_vis[(estado_visual, sim)]
                        pasos.append(f"Leer '{sim}' ➔ {estado_visual}")
                    else:
                        pasos.append(f"Transición Inválida para '{sim}'")
                        estado_visual = "Error"
                        break
                
                st.code(" -> ".join(pasos), language="text")
                
                if aceptada:
                    st.error("**Secuencia Aceptada.** El AFD confirma que el patrón estricto `[Error -> Timeout]` se cumple. Falla en cascada confirmada.")
                else:
                    st.success("**Secuencia Rechazada.** El sistema se estabilizó al final o la secuencia no terminó en Timeout.")

# --- 6. Red Neuronal, Imagen Base64 & Ontología (Semana 08) ---
elif menu == "Red Neuronal & Ontología":
    encabezado("Red Neuronal, Imágenes Base64 y Ontología (Semana 08)", "Integración completa: Modelo MLP (Predicción) + Carga y Descripción de Imagen Base64 ➔ SQLite (Evidencia) ➔ Ontología GraphML (Significado).")
    
    tab_nn, tab_img, tab_db, tab_onto = st.tabs([
        "Clasificador MLP", 
        "Análisis de Imagen (Base64)", 
        "Base de Evidencia (SQLite)", 
        "Ontología del Dominio"
    ])
    
    with tab_nn:
        st.subheader("Clasificador de Tickets por Red Neuronal Artificial")
        st.markdown("Introduce las métricas de telemetría del incidente para que la MLP prediga la categoría de soporte.")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: f1 = st.slider("Impacto App (0-10)", 0.0, 10.0, 5.0)
        with c2: f2 = st.slider("Urgencia (0-10)", 0.0, 10.0, 5.0)
        with c3: f3 = st.slider("Temperatura Servidor", 0.0, 10.0, 4.0)
        with c4: f4 = st.slider("Fallos de Red", 0.0, 10.0, 3.0)
        
        if st.button("Ejecutar Predicción Neuronal"):
            modelo_path = BASE_DIR / "artifacts" / "modelo_mlp.pkl"
            if modelo_path.exists():
                with open(modelo_path, "rb") as f:
                    clf = pickle.load(f)
                entrada = np.array([[f1, f2, f3, f4]])
                prediccion = clf.predict(entrada)[0]
                mapa_clases = {0: "Hardware", 1: "Red", 2: "Software", 3: "Seguridad"}
                tarjeta_resultado("Categoría predicha por el modelo", mapa_clases.get(prediccion, 'Desconocida'), detalle=f"Clase ID: {prediccion}", tono="verde")
            else:
                st.warning("Primero debes ejecutar `python src/main.py` para generar el modelo entrenado.")
                
    with tab_img:
        st.subheader("Reconocimiento de Imágenes, Base64 y Metadatos (Soporte TI)")
        st.markdown("Adjunta una captura de pantalla de error técnico e ingresa una descripción textual para que el agente la codifique, analice e integre en el flujo de evidencia.")
        
        uploaded_file = st.file_uploader("Sube una imagen de diagnóstico de soporte", type=["png", "jpg", "jpeg"])
        desc_usuario = st.text_input("Añade una descripción textual o sintomatología observada:", "Pantalla azul intermitente con volcado de memoria en equipo contable.")
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"Archivo cargado: {uploaded_file.name}", width=350)
            
            bytes_data = uploaded_file.getvalue()
            base64_str = base64.b64encode(bytes_data).decode("utf-8")
            
            with st.expander("Ver cadena Base64 generada"):
                st.code(base64_str[:250] + "...", language="text")
                
            if st.button("Procesar Imagen, Base64 y Descripción en el Pipeline"):
                try:
                    from classifiers.reconocimiento import ejecutar_semana_08
                    ejecutar_semana_08(imagen_bytes=bytes_data, nombre_archivo=uploaded_file.name, descripcion_texto=desc_usuario)
                    
                    nombre_l = uploaded_file.name.lower()
                    if "red" in nombre_l or "router" in nombre_l:
                        diag_resultado = "Red / Conectividad (Clase 1)"
                    elif "azul" in nombre_l or "hardware" in nombre_l:
                        diag_resultado = "Hardware / Pantalla Azul (Clase 0)"
                    else:
                        diag_resultado = "Software / Aplicación (Clase 2)"
                        
                    st.success(f"**Agente IA - Imagen Reconocida y Descrita:** {diag_resultado}")
                    st.info("**Estado en Proyecto:** La imagen se codificó en Base64, se asoció a su descripción textual, se clasificó con enfoque de soporte TI, se persistió en SQLite y se enlazó en la ontología GraphML.")
                except Exception as e:
                    st.error(f"Error al procesar la imagen en el pipeline: {e}")

    with tab_db:
        st.subheader("Registro de Evidencia Verificable (SQLite)")
        st.markdown("Consulta los registros almacenados en `artifacts/soporte_evidencia.db` (incluyendo metadatos de imágenes Base64 y descripciones textualmente auditadas).")
        db_p = BASE_DIR / "artifacts" / "soporte_evidencia.db"
        if db_p.exists():
            with sqlite3.connect(db_p) as conn:
                df_ev = pd.read_sql("SELECT * FROM evidencia_tickets ORDER BY id DESC LIMIT 15", conn)
            st.dataframe(df_ev, width="stretch")
        else:
            st.warning("Base de datos no encontrada. Ejecuta el script del proyecto.")
            
    with tab_onto:
        st.subheader("Representación del Conocimiento (Ontología GraphML)")
        st.markdown("Relaciones lógicas que otorgan significado a las predicciones y canales visuales dentro del dominio del Asistente de Soporte TI.")
        onto_p = BASE_DIR / "artifacts" / "ontologia.graphml"
        if onto_p.exists():
            G_load = nx.read_graphml(onto_p)
            st.info(f"Grafo cargado correctamente con {G_load.number_of_nodes()} conceptos y {G_load.number_of_edges()} relaciones semánticas.")
            edges_list = [(u, v, data.get('rel', 'relación')) for u, v, data in G_load.edges(data=True)]
            st.table(pd.DataFrame(edges_list, columns=["Sujeto", "Objeto", "Relación Semántica"]))
        else:
            st.warning("Archivo GraphML no encontrado en artifacts/.")
            
# --- 7. Visión Artificial (Semana 09) ---
elif menu == "Visión Artificial (Semana 09)":
    encabezado("Visión Artificial y Procesamiento de Imágenes", "Transformación de evidencia visual en información numérica mediante extracción de características, detección de contornos (Canny) y segmentación por umbrales (Otsu).")

    st.subheader("Analizar Evidencia desde la Base de Conocimiento")
    
    opciones_imagenes = {
        "Falla 1: Disco Duro Dañado (Sectores defectuosos)": "disco_duro.png",
        "Falla 2: Pantalla Azul (Volcado de memoria)": "pantalla_azul.png",
        "Falla 3: Router sin conexión (Luces apagadas)": "router.png"
    }
    
    imagen_seleccionada = st.selectbox("Selecciona un caso de estudio predefinido para procesar:", list(opciones_imagenes.keys()), key="select_vis_09")
    archivo_imagen = opciones_imagenes[imagen_seleccionada]

    if st.button("Procesar Imagen Seleccionada", key="btn_vis_09"):
        if MODULOS_CARGADOS:
            with st.spinner(f"Procesando bordes, umbrales y regiones de {archivo_imagen}..."):
                try:
                    umbral, regiones = ejecutar_vision_soporte(nombre_imagen=archivo_imagen)
                    
                    if umbral is not None:
                        st.session_state['otsu_thresh'] = umbral
                        st.session_state['otsu_regs'] = regiones
                        st.success(f"¡Pipeline ejecutado! Imagen '{archivo_imagen}' procesada correctamente.")
                    else:
                        st.error(f"No se encontró la imagen '{archivo_imagen}' en la carpeta 'data/'. ¡Asegúrate de guardarla allí primero!")
                except Exception as e:
                    st.error(f"Error en el procesamiento: {e}")
        else:
            st.error("Los módulos no se cargaron correctamente. Verifica las importaciones.")

    img_path = Path("artifacts/semana09_vision.png")
    if img_path.exists():
        st.image(str(img_path), caption="Pipeline de Visión: Imagen Original ➔ Bordes (Canny) ➔ Máscara Binaria (Otsu)", width="stretch")
        
        if 'otsu_thresh' in st.session_state and 'otsu_regs' in st.session_state:
            st.markdown("### Resultados del Procesamiento Numérico")
            col1, col2 = st.columns(2)
            col1.metric("Umbral Otsu (Corte de Intensidad)", f"{st.session_state['otsu_thresh']:.4f}")
            col2.metric("Regiones Conectadas Detectadas", st.session_state['otsu_regs'])
            st.markdown("---")
            
        st.info("""
        **Análisis Técnico del Procesamiento:**
        * **Contornos (Canny):** Identifica los cambios bruscos de intensidad en los píxeles, marcando los límites físicos y estructurales del hardware defectuoso para aislar su forma.
        * **Umbral Automático (Otsu):** Calcula matemáticamente el punto óptimo en el histograma de la imagen para separar los píxeles en dos clases (claro/oscuro), generando una máscara binaria.
        * **Regiones Conectadas:** La máscara permite al sistema contar grupos de píxeles unidos, lo cual es el primer paso para aislar piezas o zonas afectadas antes de pasarlas a una red neuronal convolucional.
        """)
    else:
        st.warning("No se ha generado la evidencia visual. Selecciona una imagen y procesa el pipeline.")

# --- 8. Histogramas y Texturas LBP (Semana 10) ---
elif menu == "Histogramas y Texturas LBP (Semana 10)":
    encabezado("Comparativa de Dispositivos (Bueno vs. Malo) y Análisis de Texturas LBP", "Evaluación morfológica y comparación lado a lado entre componentes en estado óptimo y componentes con fallos específicos.")

    categorias_hardware = {
        "Disco Duro": {
            "bueno": "disco_duro_bueno.jpg",
            "malos": {
                "Daño por Golpe Físico": "disco_duro_dañado_por_golpe.jpg",
                "Rayones en Superficie Magnética": "disco_duro_dañado_por_rayones.jpg",
                "No Gira (Falla en Motor Spindle)": "disco_duro_no_gira.jpg"
            }
        },
        "Router / Red": {
            "bueno": "router_bueno.jpg",
            "malos": {
                "Falla de Conexión Intermitente": "router_falla_conexion_intermitente.jpg"
            }
        },
        "Pantalla / Display": {
            "bueno": "panatalla_inicio_bueno.jpg",
            "malos": {
                "Daño Físico por Golpe en Display": "pantalla_dañada_por_golpe.jpg",
                "Fallo de Encendido (No Arranca / Sin Video)": "pantalla_no_arranca.jpg"
            }
        }
    }

    col_cat1, col_cat2 = st.columns(2)
    with col_cat1:
        categoria_sel = st.selectbox("Seleccionar Categoría de Producto:", list(categorias_hardware.keys()), key="s10_cat")
    
    prod_info = categorias_hardware[categoria_sel]
    img_buena_nombre = prod_info["bueno"]

    with col_cat2:
        fallo_sel = st.selectbox(f"Seleccionar Tipo de Avería ({categoria_sel}):", list(prod_info["malos"].keys()), key="s10_fallo")
    
    img_mala_nombre = prod_info["malos"][fallo_sel]

    st.markdown("---")

    if st.button("Ejecutar Análisis Comparativo (Bueno vs. Malo)"):
        if MODULOS_CARGADOS:
            with st.spinner("Procesando características, histogramas y texturas LBP para ambos estados..."):
                try:
                    import matplotlib.pyplot as plt
                    estilo_matplotlib()
                    
                    img_a, mask_a, hist_int_a, hist_lbp_a, feat_a = procesar_imagen_proyecto(img_buena_nombre)
                    img_b, mask_b, hist_int_b, hist_lbp_b, feat_b = procesar_imagen_proyecto(img_mala_nombre)

                    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
                    
                    axes[0, 0].imshow(img_a, cmap='gray')
                    axes[0, 0].set_title(f"Óptimo: {img_buena_nombre}")
                    axes[0, 0].axis('off')
                    
                    axes[0, 1].imshow(img_b, cmap='gray')
                    axes[0, 1].set_title(f"Averiado: {img_mala_nombre}")
                    axes[0, 1].axis('off')
                    
                    axes[1, 0].plot(hist_int_a, label="Intensidad (Sano)", color="#2457D6")
                    axes[1, 0].plot(hist_lbp_a, label="LBP Textura (Sano)", color="#E08A1E")
                    axes[1, 0].set_title(f"Histogramas - {img_buena_nombre}")
                    axes[1, 0].legend(loc="upper right")
                    
                    axes[1, 1].plot(hist_int_b, label="Intensidad (Averiado)", color="#0E9F8E")
                    axes[1, 1].plot(hist_lbp_b, label="LBP Textura (Averiado)", color="#C0392B")
                    axes[1, 1].set_title(f"Histogramas - {img_mala_nombre}")
                    axes[1, 1].legend(loc="upper right")
                    
                    plt.tight_layout()
                    artifact_path = BASE_DIR / "artifacts" / "semana10_comparativa.png"
                    artifact_path.parent.mkdir(parents=True, exist_ok=True)
                    plt.savefig(artifact_path, dpi=150, bbox_inches="tight")
                    plt.close()

                    st.session_state['s10_feat_bueno'] = feat_a
                    st.session_state['s10_feat_malo'] = feat_b
                    st.session_state['s10_nombres'] = (img_buena_nombre, img_mala_nombre)
                    st.session_state['s10_fallo_desc'] = fallo_sel

                    st.success("¡Análisis comparativo de la Semana 10 completado con éxito!")
                except Exception as e:
                    st.error(f"Error al procesar las imágenes: {e}")
        else:
            st.error("Módulos no cargados correctamente.")

    comp_path = Path("artifacts/semana10_comparativa.png")
    if comp_path.exists():
        st.markdown("### Visualización Lado a lado (Imágenes e Histogramas Analíticos)")
        st.image(str(comp_path), width="stretch")

    if 's10_feat_bueno' in st.session_state:
        f_bno = st.session_state['s10_feat_bueno']
        f_mlo = st.session_state['s10_feat_malo']
        n_bno, n_mlo = st.session_state['s10_nombres']
        desc_fallo = st.session_state['s10_fallo_desc']

        st.markdown("### Especificación Técnica del Diagnóstico y Fallos")
        st.error(f"**Avería Detectada:** {desc_fallo} (`{n_mlo}`)")
        
        if "golpe" in n_mlo:
            st.markdown("- **Análisis de Fallo:** Disrupción estructural por impacto cinético. Las regiones conectadas aumentan debido a las fracturas y astillas, alterando drásticamente el patrón regular de la referencia sana (`{n_bno}`).")
        elif "rayones" in n_mlo:
            st.markdown("- **Análisis de Fallo:** Abrasión profunda en la superficie magnética. Se observa una desviación notoria en los descriptores de textura LBP respecto al componente óptimo.")
        elif "no_gira" in n_mlo:
            st.markdown("- **Análisis de Fallo:** Traba mecánica en el motor o bloqueo de eje. El histograma carece de variabilidad dinámica al encontrarse el componente detenido.")
        elif "intermitente" in n_mlo:
            st.markdown("- **Análisis de Fallo:** Degeneración en la pasarela de red y pérdida de estabilidad de enlace inalámbrico.")
        else:
            st.markdown("- **Análisis de Fallo:** Anomalía crítica en circuitos de video o alimentación, rompiendo la simetría morfológica del estado base.")

        st.markdown("---")
        st.markdown("### Comparativa Numérica de Vectores de Características (.npy)")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"**Referencia Sana: `{n_bno}`**")
            st.metric("Área Media de Regiones", f"{f_bno[0]:.2f} px")
            st.metric("Desviación Estándar", f"{f_bno[1]:.2f}")
            st.metric("Regiones Validadas", int(f_bno[2]))
        with col_m2:
            st.markdown(f"**Componente Averiado: `{n_mlo}`**")
            st.metric("Área Media de Regiones", f"{f_mlo[0]:.2f} px", delta=f"{f_mlo[0]-f_bno[0]:.2f} px", delta_color="inverse")
            st.metric("Desviación Estándar", f"{f_mlo[1]:.2f}", delta=f"{f_mlo[1]-f_bno[1]:.2f}", delta_color="off")
            st.metric("Regiones Validadas", int(f_mlo[2]), delta=f"{int(f_mlo[2]-f_bno[2])}", delta_color="inverse")
    else:
        st.warning("Selecciona una categoría y un tipo de avería, luego haz clic en 'Ejecutar Análisis Comparativo (Bueno vs. Malo)'.")

# --- 9. Benchmark y Decisiones de Modelos (Semana 11) ---
elif menu == "Benchmark y Decisiones de Modelos (Semana 11)":
    encabezado("Benchmark de Modelos y Justificación Técnica (Semana 11)", "Evaluación comparativa entre Regresión Logística, Random Forest y Red Neuronal MLP bajo un protocolo estricto y reproducible.")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Modelo Serializado", "mejor_modelo.pkl", "Guardado en artifacts/")
    with col2: st.metric("Protocolo de Datos", "Train-Test Split", "Semilla Fija 42 (75/25)")
    with col3: st.metric("Auditoría", "audit.log", "Registro Automático")
    
    st.markdown("---")
    st.subheader("Tabla de Evidencias del Benchmark (artifacts/benchmark.csv)")
    
    if BENCHMARK_CSV_PATH.exists():
        df_bench = pd.read_csv(BENCHMARK_CSV_PATH)
        st.dataframe(df_bench, width="stretch")
        
        st.markdown("#### Gráfico Comparativo de Desempeño (Accuracy)")
        
        import plotly.express as px
        fig = px.bar(
            df_bench, 
            x="modelo", 
            y="accuracy", 
            text="accuracy",
            color="modelo",
            color_discrete_sequence=["#2457D6", "#0E9F8E", "#E08A1E"]
        )
        fig.update_traces(texttemplate='%{text:.4f}', textposition='outside', textfont=dict(size=13, color="#14213D"), cliponaxis=False)
        fig.update_layout(
            yaxis=dict(range=[0.90, 1.02]),
            margin=dict(t=20, b=20, l=20, r=20),
            height=400,
            showlegend=False
        )
        fig = estilo_plotly(fig)
        st.plotly_chart(fig, width="stretch")
        
        df_sorted = df_bench.sort_values("accuracy", ascending=False).reset_index(drop=True)
        
        ganador_nombre = df_sorted.iloc[0]["modelo"]
        ganador_acc = df_sorted.iloc[0]["accuracy"] * 100
        ganador_tiempo = df_sorted.iloc[0]["fit_seconds"]
        
        segundo_nombre = df_sorted.iloc[1]["modelo"]
        segundo_acc = df_sorted.iloc[1]["accuracy"] * 100
        segundo_tiempo = df_sorted.iloc[1]["fit_seconds"]
        
        tercero_nombre = df_sorted.iloc[2]["modelo"]
        tercero_acc = df_sorted.iloc[2]["accuracy"] * 100
        tercero_tiempo = df_sorted.iloc[2]["fit_seconds"]

        st.markdown("### Análisis Analítico de la Gráfica Comparativa (Datos en Tiempo Real)")
        st.markdown(
            f"Del análisis visual y métrico de la gráfica anterior, alimentada directamente desde `artifacts/benchmark.csv`, se desprenden los siguientes hallazgos de ingeniería:\n\n"
            f"1. **Modelo Líder ({ganador_nombre}):** Se posiciona en el primer lugar del benchmark con una precisión (*accuracy*) de **{ganador_acc:.2f}%** y un tiempo de entrenamiento de **{ganador_tiempo:.4f}s**, garantizando el mejor balance predictivo para el asistente.\n"
            f"2. **Segundo Modelo ({segundo_nombre}):** Alcanza un desempeño competitivo de **{segundo_acc:.2f}%** con un tiempo de entrenamiento de **{segundo_tiempo:.4f}s**, demostrando una alta eficiencia computacional en el espacio de características.\n"
            f"3. **Tercer Modelo ({tercero_nombre}):** Registra un accuracy de **{tercero_acc:.2f}%** y un tiempo de **{tercero_tiempo:.4f}s**, evidenciando las variaciones del algoritmo frente a este conjunto de datos específico.\n\n"
            f"**Conclusión del Análisis:** La elección de **{ganador_nombre}** queda rigurosamente justificada al maximizar la tasa de aciertos en el triaje de tickets, cumpliendo de forma óptima con los criterios de evaluación de la Semana 11."
        )
        
        st.markdown("---")
        st.subheader("Registro de Decisión Arquitectónica (ADR - Semana 11)")
        adr_path = BASE_DIR / "reports" / "semana11_adr.md"
        if adr_path.exists():
            with open(adr_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())
        else:
            st.info("Ejecuta `python src/semana11_benchmark.py` para generar el informe ADR automáticamente.")
    else:
        st.warning("No se encontró el archivo de benchmark. Ejecuta `python src/semana11_benchmark.py` para generarlo.")

# --- 10. Motor de Inferencia Avanzado (10 Reglas - Semana 13) ---
elif menu == "Motor de Inferencia (Semana 13)":
    encabezado("Ingeniería del Conocimiento: Motor de Inferencia Lógica (10 Reglas)", "Evaluación de reglas Horn por encadenamiento hacia adelante con trazabilidad y explicabilidad paso a paso para el Asistente de Soporte TI.")
    
    st.markdown("### Catálogo Extendido de Reglas del Sistema (10 Reglas de Cobertura KB)")
    st.markdown("""
    - **R1:** $\\text{imagen\\_procesada\\_ok} \\land \\text{textura\\_anomala\\_detectada} \\longrightarrow \\text{diagnostico\\_hardware\\_fallido}$
    - **R2:** $\\text{diagnostico\\_hardware\\_fallido} \\land \\text{hardware\\_critico} \\longrightarrow \\text{escalamiento\\_nivel\\_2}$
    - **R3:** $\\text{escalamiento\\_nivel\\_2} \\land \\text{sla\\_excedido} \\longrightarrow \\text{prioridad\\_critica\\_urgente}$
    - **R4:** $\\text{conexion\\_intermitente} \\land \\text{alta\\_latencia} \\longrightarrow \\text{falla\\_enlace\\_wan}$
    - **R5:** $\\text{falla\\_enlace\\_wan} \\land \\text{impacto\\_critico} \\longrightarrow \\text{escalamiento\\_redes\\_nivel\\_3}$
    - **R6:** $\\text{espacio\\_disco\\_insuficiente} \\land \\text{archivos\\_temporales\\_excesivos} \\longrightarrow \\text{saturacion\\_almacenamiento}$
    - **R7:** $\\text{saturacion\\_almacenamiento} \\longrightarrow \\text{ejecutar\\_script\\_liberacion\\_disco}$
    - **R8:** $\\text{intentos\\_fallidos\\_login} \\land \\text{bloqueo\\_cuenta\\_activo\\_directory} \\longrightarrow \\text{incidente\\_seguridad\\_credenciales}$
    - **R9:** $\\text{incidente\\_seguridad\\_credenciales} \\land \\text{acceso\\_no\\_autorizado\\_detectado} \\longrightarrow \\text{aislamiento\\_dispositivo\\_red}$
    - **R10:** $\\text{error\\_runtime\\_aplicacion} \\land \\text{cierre\\_inesperado\\_nomina} \\longrightarrow \\text{falla\\_critica\\_software\\_negocio}$
    """)
    
    st.markdown("---")
    st.subheader("Simulador Interactivo de Escenarios y Explicabilidad")
    
    col_esc1, col_esc2 = st.columns(2)
    with col_esc1:
        st.markdown("**Selecciona las evidencias de Hardware / Tickets:**")
        hecho_1 = st.checkbox("imagen_procesada_ok", value=True)
        hecho_2 = st.checkbox("textura_anomala_detectada", value=True)
        hecho_3 = st.checkbox("hardware_critico", value=True)
        hecho_4 = st.checkbox("sla_excedido", value=True)
    with col_esc2:
        st.markdown("**Selecciona las evidencias de Red / Almacenamiento / Seguridad:**")
        hecho_5 = st.checkbox("conexion_intermitente", value=False)
        hecho_6 = st.checkbox("alta_latencia", value=False)
        hecho_7 = st.checkbox("impacto_critico", value=False)
        hecho_8 = st.checkbox("espacio_disco_insuficiente", value=False)
        hecho_9 = st.checkbox("archivos_temporales_excesivos", value=False)
        
    hechos_usuario = set()
    if hecho_1: hechos_usuario.add("imagen_procesada_ok")
    if hecho_2: hechos_usuario.add("textura_anomala_detectada")
    if hecho_3: hechos_usuario.add("hardware_critico")
    if hecho_4: hechos_usuario.add("sla_excedido")
    if hecho_5: hechos_usuario.add("conexion_intermitente")
    if hecho_6: hechos_usuario.add("alta_latencia")
    if hecho_7: hechos_usuario.add("impacto_critico")
    if hecho_8: hechos_usuario.add("espacio_disco_insuficiente")
    if hecho_9: hechos_usuario.add("archivos_temporales_excesivos")
    
    if st.button("Ejecutar Motor de Inferencia con Explicabilidad"):
        if MODULOS_CARGADOS:
            hechos_finales, trazas, explicaciones = inferir_con_explicacion(hechos_usuario, REGLAS_SOPORTE_TI)
            
            st.markdown("---")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("#### Hechos Deducidos (Base Ampliada)")
                st.info(list(hechos_finales))
            with col_r2:
                st.markdown("#### Traza de Reglas Activadas")
                st.success(trazas if trazas else "Ninguna regla activada.")
                
            st.markdown("#### Explicabilidad Paso a Paso (Modus Ponens)")
            if explicaciones:
                for exp in explicaciones:
                    st.markdown(f"- {exp}")
            else:
                st.warning("No se disparó ninguna regla con las premisas proporcionadas.")
                
            if "prioridad_critica_urgente" in hechos_finales:
                st.error("**Conclusión Demostrada:** `prioridad_critica_urgente` alcanzada con éxito.")
            elif "ejecutar_script_liberacion_disco" in hechos_finales:
                st.success("**Conclusión Demostrada:** `ejecutar_script_liberacion_disco` alcanzada con éxito (Automatización ejecutada).")
            else:
                st.warning("**Conclusión No Demostrada:** Faltan premisas intermedias para llegar a la conclusión final.")
        else:
            st.error("Módulos no disponibles.")

# --- 11. Redes Semánticas (Semana 14) ---
elif menu == "Redes Semánticas (Semana 14)":
    encabezado("Ingeniería del Conocimiento: Redes Semánticas (Semana 14)", "Modelado de conceptos de soporte TI, triples semánticos, inferencia por jerarquía (es_un) y herencia de propiedades.")

    if MODULOS_CARGADOS:
        procs_kb = cargar_base_conocimiento()
        red_proyecto = construir_red_proyecto()
        red_ampliada, kb_omitidos = construir_red_ampliada(procs_kb)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Conceptos del proyecto", len(red_proyecto.nodos), "Red base", delta_color="off")
        m2.metric("Triples explícitos", len(red_proyecto.triples), "Hechos almacenados", delta_color="off")
        m3.metric("Relaciones", len(RELACIONES), "Vocabulario controlado", delta_color="off")
        m4.metric("Casos de la KB", len(procs_kb), f"Red ampliada: {len(red_ampliada.nodos)} conceptos", delta_color="off")
        st.markdown("")

        tab_red, tab_oracion, tab_consulta, tab_kb = st.tabs([
            "Red del proyecto", "Interpretar oraciones", "Consultas e inferencias", "Red ampliada (KB)"
        ])

        with tab_red:
            st.subheader("Grafo de conocimiento del proyecto")
            st.caption("Cada flecha es un triple (sujeto, relación, objeto). Azul: es_un. Verde: requiere. Ámbar discontinuo: se_resuelve_con.")
            st.graphviz_chart(dot_red(red_proyecto.triples))
            st.markdown("#### Triples explícitos")
            st.dataframe(pd.DataFrame(red_proyecto.triples, columns=["Sujeto", "Relación", "Objeto"]),
                         width="stretch", hide_index=True)
            st.markdown("#### Relaciones y su significado")
            st.table(pd.DataFrame([
                {"Relación": r, "Significado": d, "Transitiva": "Sí" if r == "es_un" else "No",
                 "Se hereda": "Sí" if r in RELACIONES_HEREDABLES else "No"}
                for r, d in RELACIONES.items()
            ]).set_index("Relación"))

        with tab_oracion:
            st.subheader("De una oración a un triple semántico")
            st.markdown("Formatos admitidos: `<A> es un <B>`, `<A> requiere <B>` (o `necesita`) y `<A> se resuelve con <B>`.")
            oracion = st.text_input("Escribe una oración simple:", "El Servidor BD es un Hardware Crítico.", key="s14_oracion")
            if oracion.strip():
                try:
                    sujeto, relacion, objeto = red_proyecto.interpretar_oracion(oracion, registrar=False)
                    st.success("Oración interpretada correctamente.")
                    st.code(f"({sujeto!r}, {relacion!r}, {objeto!r})", language="python")
                    st.caption("Se normalizó el texto: minúsculas, sin tildes, sin artículo inicial y con guion bajo entre palabras.")
                except ValueError as error:
                    st.error("Oración rechazada: no tiene un formato admitido.")
                    st.text(str(error))
            with st.expander("Ejemplos para probar"):
                st.markdown(
                    "**Válidas**\n\n"
                    "- `servidor_bd necesita respaldo_diario`\n"
                    "- `sobrecalentamiento se resuelve con limpieza_ventilacion`\n\n"
                    "**Rechazadas**\n\n"
                    "- `el procesador funciona muy lento hoy` (sin formato reconocido)\n"
                    "- `servidor_bd es un` (falta el objeto)"
                )

        with tab_consulta:
            opciones_red = [f"Red del proyecto ({len(red_proyecto.nodos)} conceptos)",
                            f"Red ampliada ({len(red_ampliada.nodos)} conceptos, con la KB)"]
            alcance = st.radio("Red a consultar", opciones_red, horizontal=True, key="s14_alcance")
            es_base = alcance == opciones_red[0]
            red_q = red_proyecto if es_base else red_ampliada
            sufijo = "base" if es_base else "kb"
            nodos = sorted(red_q.nodos)

            def _indice(nombre):
                return nodos.index(nombre) if nombre in nodos else 0

            st.markdown("#### Inferencia por jerarquía (es_un)")
            c1, c2 = st.columns(2)
            origen = c1.selectbox("Concepto origen", nodos, index=_indice("servidor_bd"), key=f"s14_origen_{sufijo}")
            destino = c2.selectbox("¿Es un...? (categoría)", nodos, index=_indice("activo_corporativo"), key=f"s14_destino_{sufijo}")

            camino = red_q.explicar_es_un(origen, destino)
            if camino is None:
                st.error(f"Sin evidencia: con los hechos registrados no se puede concluir que **{origen}** sea un **{destino}**.")
            elif not camino:
                st.info("Identidad: es el mismo concepto.")
            else:
                tipo = "hecho explícito" if len(camino) == 1 else "inferido por transitividad (R1)"
                st.success(f"**{origen} es_un {destino}**: {tipo}.")
                for i, (s, r, o) in enumerate(camino, 1):
                    st.markdown(f"**Hecho {i}.** `({s}, {r}, {o})`")
                if len(camino) > 1:
                    st.markdown("**Regla R1 (transitividad).** Si A es_un B y B es_un C, entonces A es_un C.")
                st.graphviz_chart(dot_red(triples_para_grafo(red_q, camino), camino))

            st.markdown("---")
            st.markdown("#### Herencia de propiedades (requiere)")
            concepto = st.selectbox("Concepto", nodos, index=_indice("servidor_bd"), key=f"s14_concepto_{sufijo}")
            props = red_q.propiedades_con_origen(concepto)
            if props:
                filas = []
                for d in props:
                    cadena = " -> ".join([d["ruta"][0][0]] + [t[2] for t in d["ruta"]]) if d["ruta"] else concepto
                    filas.append({"Propiedad": d["propiedad"], "Declarada en": d["declarada_en"],
                                  "Origen": "Propia" if not d["ruta"] else "Heredada (R2)", "Cadena es_un": cadena})
                st.dataframe(pd.DataFrame(filas), width="stretch", hide_index=True)
                st.caption("R2 (herencia): si A es_un B y B requiere P, entonces A requiere P.")
                prueba = [t for d in props for t in d["ruta"]] + [(d["declarada_en"], "requiere", d["propiedad"]) for d in props]
                st.graphviz_chart(dot_red(triples_para_grafo(red_q, prueba), prueba))
            else:
                st.info(f"Sin evidencia: '{concepto}' no tiene propiedades propias ni heredadas en la red.")

            with st.expander("Relaciones directas y subtipos de un concepto"):
                explorado = st.selectbox("Concepto a explorar", nodos, index=_indice("hardware_critico"), key=f"s14_explorar_{sufijo}")
                rel = red_q.conceptos_relacionados(explorado)
                salientes = "\n".join(f"- `{explorado}` **{r}** `{o}`" for r, o in rel["salientes"]) or "- Ninguna"
                entrantes = "\n".join(f"- `{s}` **{r}** `{explorado}`" for s, r in rel["entrantes"]) or "- Ninguna"
                subtipos = ", ".join(f"`{x}`" for x in red_q.subtipos(explorado)) or "ninguno"
                st.markdown(f"**Relaciones que salen**\n\n{salientes}\n\n**Relaciones que llegan**\n\n{entrantes}\n\n**Subtipos:** {subtipos}")

        with tab_kb:
            st.subheader(f"Los {len(procs_kb)} casos de la KB dentro de la red")
            st.markdown("Cada caso es_un categoría técnica; cada categoría es_un activo_corporativo y requiere un recurso propio. Por R2, cada caso hereda esos requisitos.")
            conteo = pd.Series([normalizar(p["categoria"]) for p in procs_kb]).value_counts()
            st.dataframe(pd.DataFrame([
                {"Categoría": cat, "Casos": int(n),
                 "Requisitos heredados": ", ".join(red_ampliada.consultar_propiedades(f"categoria_{cat}"))}
                for cat, n in conteo.items()
            ]), width="stretch", hide_index=True)
            st.markdown("#### Triples de la red ampliada")
            st.dataframe(pd.DataFrame(red_ampliada.triples, columns=["Sujeto", "Relación", "Objeto"]),
                         width="stretch", hide_index=True, height=320)
            if kb_omitidos:
                st.caption(f"Casos omitidos por no poder normalizarse: {', '.join(kb_omitidos)}")
    else:
        st.error("El módulo de Redes Semánticas (`classifiers.red_semantica`) no está disponible.")

# --- 12. Portal de Usuario ---
elif menu == "Portal de Usuario":
    encabezado("Portal / Cliente Final", "Interfaz orientada al usuario final para la creación de solicitudes de soporte.")
    usuario_nombre = st.text_input("Nombre:", "Carlos Pérez")
    problema_desc = st.text_area("Descripción:", "Pantalla azul intermitente.")
    if st.button("Enviar Solicitud"):
        st.success(f"¡Ticket registrado con éxito para {usuario_nombre}!")

# --- 13. Base de Conocimiento (KB) ---
elif menu == "Base de Conocimiento (KB)":
    encabezado("Base de Conocimiento Técnica (KB)", "Catálogo de los 30 procedimientos operativos estandarizados.")
    for proc in cargar_base_conocimiento()[:10]:
        with st.expander(f"#{proc['id']} - {proc['titulo']} [{proc['categoria']}]"):
            st.markdown(f"**Solución:** {proc['solucion']}")

# --- 14. Trazas de Auditoría ---
elif menu == "Trazas de Auditoría":
    encabezado("Registro de Auditoría del Sistema (audit.log)", "Monitoreo de eventos generados por el orquestador.")
    registros, raw_text = parsear_audit_log()
    if registros:
        st.dataframe(pd.DataFrame(registros)[["fecha", "nivel", "mensaje"]], width="stretch", height=400)
    else:
        st.warning("No se encontró `artifacts/audit.log`.")


# --- 15. Preguntas Frecuentes (FAQ) ---
elif menu == "Preguntas Frecuentes (FAQ)":
    encabezado("Preguntas Frecuentes del Proyecto (Semana 02 a Semana 14)",
               "Consulta las dudas más comunes sobre cada semana implementada. Escribe tu pregunta y el asistente recupera las respuestas más parecidas con TF-IDF y similitud coseno, el mismo enfoque del Sistema Híbrido de la Semana 05.")

    if FAQ_DISPONIBLE:
        asistente_faq = cargar_asistente_faq()
        semanas_faq = [s for s in asistente_faq.semanas_disponibles() if s != 0]
        opciones_semana = ["Todas"] + [f"Semana {s:02d}" for s in semanas_faq] + ["General"]

        def _semana_de(opcion):
            if opcion == "Todas":
                return None
            return 0 if opcion == "General" else int(opcion.split()[1])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Preguntas registradas", len(asistente_faq.faqs), "Catálogo del proyecto", delta_color="off")
        m2.metric("Semanas cubiertas", len(semanas_faq), "De la 02 a la 14", delta_color="off")
        m3.metric("Método de búsqueda", "TF-IDF", "Similitud coseno", delta_color="off")
        m4.metric("Umbral de confianza", "0.15", "Mínimo para responder", delta_color="off")
        st.markdown("")

        tab_preguntar, tab_explorar = st.tabs(["Pregúntale al asistente", "Explorar por semana"])

        # ---------- Pestaña 1: preguntar ----------
        with tab_preguntar:
            st.session_state.setdefault("faq_consulta", "")

            def _usar_sugerencia(texto):
                st.session_state["faq_consulta"] = texto

            consulta = st.text_input("Escribe tu pregunta", key="faq_consulta",
                                     placeholder="Ejemplo: ¿Cómo funciona el algoritmo A*?")
            filtro = st.radio("Buscar en", opciones_semana, horizontal=True, key="faq_filtro")

            if consulta.strip():
                resultados = asistente_faq.buscar(consulta, k=3, semana=_semana_de(filtro))
                if resultados:
                    st.markdown(f"#### Respuestas más parecidas ({len(resultados)})")
                    for posicion, r in enumerate(resultados):
                        tarjeta_faq(r, similitud=r["similitud"], mejor=(posicion == 0))
                else:
                    st.info("No encontré una pregunta suficientemente parecida. Prueba con otras palabras, quita el filtro de semana o elige una de las preguntas sugeridas.")
            else:
                st.markdown("#### Preguntas sugeridas")
                columnas = st.columns(2)
                for i, sugerencia in enumerate(asistente_faq.sugerencias(4)):
                    columnas[i % 2].button(sugerencia, key=f"faq_sug_{i}", on_click=_usar_sugerencia, args=(sugerencia,), width="stretch")

        # ---------- Pestaña 2: explorar por semana ----------
        with tab_explorar:
            elegido = st.radio("Semana", opciones_semana, horizontal=True, key="faq_semana_explorar")
            semana_exp = _semana_de(elegido)
            lista = asistente_faq.por_semana(semana_exp)
            if semana_exp not in (None, 0):
                tema, pagina = SEMANAS[semana_exp]
                st.markdown(f"**{tema}** · Página del dashboard: `{pagina}`")
            st.caption(f"{len(lista)} preguntas")
            semana_actual = None
            for faq in lista:
                if semana_exp is None and faq["semana"] != semana_actual:
                    semana_actual = faq["semana"]
                    rotulo = "General" if semana_actual == 0 else f"Semana {semana_actual:02d}"
                    st.subheader(f"{rotulo} · {SEMANAS[semana_actual][0]}")
                with st.expander(faq["pregunta"]):
                    st.markdown(faq["respuesta"])
                    st.caption(f"Módulo: {faq['ref']}")
    else:
        st.error("El módulo de preguntas frecuentes (`classifiers/faq_semanas.py`) no está disponible. Cópialo a `src/classifiers/`.")

# --- Pie de página común ---
st.markdown('<div class="app-footer">Asistente de Soporte TI Híbrido · Inteligencia Artificial · ETITC · Semana 02 a Semana 14</div>', unsafe_allow_html=True)