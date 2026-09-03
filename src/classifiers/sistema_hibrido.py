from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

KB_PATH = DATA_DIR / "base_conocimiento.txt"
REPORT_PATH = REPORTS_DIR / "semana05.md"

# Reglas expertas lógicas SI -> ENTONCES adaptadas al dominio
RULES = [
    (lambda q: "caliente" in q or "ventilador" in q or "temperatura" in q, "diagnostico_hardware_temperatura"),
    (lambda q: "internet" in q or "red" in q or "wifi" in q or "ethernet" in q, "diagnostico_conectividad_red"),
    (lambda q: "lenta" in q or "rendimiento" in q or "memoria" in q, "optimizacion_recursos_sistema"),
    (lambda q: "virus" in q or "malware" in q or "phishing" in q, "seguridad_amenazas_detectadas"),
    (lambda q: "disco" in q or "almacenamiento" in q, "gestion_almacenamiento")
]

# Ejemplos de entrenamiento etiquetados para el clasificador
TRAIN_X = [
    "el equipo esta muy caliente y suena fuerte",
    "temperatura elevada en el chasis del servidor",
    "se cayo el internet y no hay conexion de red",
    "la red wifi esta muy intermitente y lenta",
    "la aplicacion esta muy lenta y consume mucha memoria",
    "problema de rendimiento por alto consumo de cpu",
    "alerta de virus detectado en el directorio temporal",
    "posible malware o amenaza troyana detectada",
    "el disco duro esta lleno y no hay espacio libre",
    "problema de almacenamiento en la particion principal",
    "la cuenta de usuario se encuentra bloqueada",
    "error de autenticacion y credenciales invalidas",
    "pantalla azul de error en el sistema operativo",
    "el servidor no responde a las solicitudes ping",
    "la impresora presenta un error critico de conexion"
]

TRAIN_Y = [
    "hardware", "hardware",
    "red", "red",
    "rendimiento", "rendimiento",
    "seguridad", "seguridad",
    "almacenamiento", "almacenamiento",
    "seguridad", "seguridad",
    "sistema",
    "servidor",
    "perifericos"
]

def load_documents() -> list[str]:
    """Carga los documentos desde el archivo de base de conocimiento."""
    if not KB_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo en {KB_PATH}")
    docs = [line.strip() for line in KB_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    return docs

class SistemaHibridoSoporte:
    def __init__(self):
        self.docs = load_documents()
        self.vectorizer = TfidfVectorizer()
        self.doc_matrix = self.vectorizer.fit_transform(self.docs)
        
        self.classifier = make_pipeline(
            TfidfVectorizer(),
            LogisticRegression(max_iter=1000, random_state=42)
        )
        self.classifier.fit(TRAIN_X, TRAIN_Y)

    def procesar(self, query: str) -> dict:
        q = query.lower()
        fired_rules = [name for condition, name in RULES if condition(q)]
        
        query_vec = self.vectorizer.transform([q])
        sims = cosine_similarity(query_vec, self.doc_matrix)[0]
        best_idx = int(sims.argmax())
        
        pred_class = str(self.classifier.predict([q])[0])
        
        return {
            "consulta": query,
            "reglas": fired_rules if fired_rules else ["regla_generica_soporte"],
            "evidencia": self.docs[best_idx],
            "similitud": float(sims[best_idx]),
            "clase": pred_class
        }

def generar_reporte(resultados: list[dict]):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Reporte de Pruebas - Semana 05: Asistente de Soporte TI",
        "",
        "Registro automatizado de ejecucion del sistema hibrido utilizando la base de conocimiento de 30 entradas.",
        ""
    ]
    for i, r in enumerate(resultados, start=1):
        lines.extend([
            f"## Prueba {i}",
            f"- **Consulta:** `{r['consulta']}`",
            f"- **Reglas Activadas:** `{', '.join(r['reglas'])}`",
            f"- **Evidencia (Base de Conocimiento):** {r['evidencia']}",
            f"- **Similitud Coseno:** `{r['similitud']:.4f}`",
            f"- **Clase Predicha:** `{r['clase']}`",
            ""
        ])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[✔] Reporte generado exitosamente en: {REPORT_PATH}")