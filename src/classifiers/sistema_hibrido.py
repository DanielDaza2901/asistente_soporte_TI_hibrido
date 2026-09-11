from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

# 1. Configuración de rutas relativas para ubicar data y reportes desde la estructura del repositorio
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

KB_PATH = DATA_DIR / "base_conocimiento.txt"
REPORT_PATH = REPORTS_DIR / "semana05.md"

# 2. Base de reglas expertas (Motor Simbólico): Evalúa palabras clave para asignar etiquetas de diagnóstico inmediatas
RULES = [
    (lambda q: "caliente" in q or "ventilador" in q or "temperatura" in q or "ruidoso" in q, "diagnostico_hardware_temperatura"),
    (lambda q: "internet" in q or "red" in q or "wifi" in q or "ethernet" in q or "conexion" in q, "diagnostico_conectividad_red"),
    (lambda q: "lenta" in q or "rendimiento" in q or "memoria" in q or "cpu" in q or "arrancar" in q, "optimizacion_recursos_sistema"),
    (lambda q: "virus" in q or "malware" in q or "phishing" in q or "firewall" in q, "seguridad_amenazas_detectadas"),
    (lambda q: "disco" in q or "almacenamiento" in q or "espacio" in q, "gestion_almacenamiento"),
    (lambda q: "impresora" in q or "imprime" in q or "tinta" in q, "soporte_perifericos_impresion"),
    (lambda q: "servidor" in q or "ping" in q or "vpn" in q, "soporte_redes_servidores"),
    (lambda q: "password" in q or "contrasena" in q or "bloqueada" in q, "gestion_identidad_accesos")
]

# 3. Conjunto de datos de entrenamiento sintético para el clasificador estadístico (ML)
TRAIN_X = [
    # Hardware (temperatura, fuentes, pantallas, periféricos básicos)
    "el equipo esta muy caliente y el ventilador suena fuerte", "temperatura elevada en el chasis del computador",
    "el computador no enciende y la fuente de poder no responde", "pantalla azul con error de drivers o memoria ram",
    "el ventilador hace un ruido muy fuerte y vibra", "la bateria de la laptop no carga al conectar el cargador",
    "el disco duro tiene sectores danados y genera errores de lectura", "el teclado o monitor no da senal de video por hdmi",

    # Red (conectividad, wifi, cableado, servidores, vpn)
    "se cayo el internet y no hay conexion de red", "la conexion a internet cae constantemente y falla el enlace",
    "la red wifi esta muy lenta e intermitente", "el wifi no conecta en la oficina y rechaza la contrasena",
    "puerto ethernet sin conexion de red local", "la vpn corporativa no permite conectar",
    "el servidor no responde a las solicitudes de ping",

    # Rendimiento (memoria, cpu, procesos colgados, lentitud general)
    "la aplicacion esta muy lenta y consume mucha memoria ram", "problema de rendimiento por alto consumo de cpu",
    "el sistema esta muy lento al iniciar sesion", "aplicacion colgada que no responde y bloquea el equipo",
    "el navegador web consume demasiados recursos con muchas pestanas", "bajo rendimiento general del sistema operativo",

    # Seguridad (virus, malware, cuentas bloqueadas, accesos no autorizados)
    "alerta de virus detectado en el directorio temporal", "posible malware o amenaza troyana detectada por antivirus",
    "la cuenta de usuario corporativa se encuentra bloqueada", "error de autenticacion y credenciales corporativas invalidas",
    "correo de phishing sospechoso solicitando contrasena", "el firewall corporativo bloquea el trafico de la aplicacion",

    # Almacenamiento (espacio en disco, particiones, limpieza)
    "el disco duro esta lleno y no hay espacio libre disponible", "problema de almacenamiento por falta de espacio en particion",
    "liberar espacio en disco eliminando archivos temporales",

    # Software y soporte de impresión
    "la impresora presenta un error critico de conexion o atasco", "la impresora no imprime documentos en la cola de impresion",
    "error al instalar la actualizacion de software corporativo"
]

TRAIN_Y = [
    # Categorías asociadas a los ejemplos de TRAIN_X
    "hardware", "hardware", "hardware", "hardware", "hardware", "hardware", "hardware", "hardware",
    "red", "red", "red", "red", "red", "red", "red",
    "rendimiento", "rendimiento", "rendimiento", "rendimiento", "rendimiento", "rendimiento",
    "seguridad", "seguridad", "seguridad", "seguridad", "seguridad", "seguridad",
    "almacenamiento", "almacenamiento", "almacenamiento",
    "software", "software", "software"
]

def load_documents() -> list[str]:
    """Carga y limpia las 30 líneas de procedimientos de la base de conocimiento."""
    if not KB_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo en {KB_PATH}")
    raw_lines = [line.strip() for line in KB_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    docs = []
    for line in raw_lines:
        parts = line.split(". ", 1)
        # Remueve la numeración inicial de cada línea (ej. "1. Texto" -> "Texto")
        if len(parts) == 2 and parts[0].isdigit():
            docs.append(parts[1])
        else:
            docs.append(line)
    return docs

class SistemaHibridoSoporte:
    """Clase principal que integra Reglas + RAG (TF-IDF + Coseno) + ML (Regresión Logística)."""
    def __init__(self):
        # Carga los documentos e inicializa la matriz vectorial TF-IDF para RAG
        self.docs = load_documents()
        self.vectorizer = TfidfVectorizer()
        self.doc_matrix = self.vectorizer.fit_transform(self.docs)
        
        # Entrena el pipeline clasificador multiclase (Texto -> Vector -> Categoría)
        self.classifier = make_pipeline(
            TfidfVectorizer(),
            LogisticRegression(max_iter=1000, random_state=42)
        )
        self.classifier.fit(TRAIN_X, TRAIN_Y)

    def procesar(self, query: str) -> dict:
        """Procesa una consulta procesando las 3 capas: Reglas, RAG y Clasificación ML."""
        q = query.lower()
        # 1. Componente Simbólico: Evalúa si activa alguna regla experta
        fired_rules = [name for condition, name in RULES if condition(q)]
        
        # 2. Componente RAG: Vectoriza la consulta y encuentra la mejor evidencia por similitud coseno
        query_vec = self.vectorizer.transform([q])
        sims = cosine_similarity(query_vec, self.doc_matrix)[0]
        best_idx = int(sims.argmax())
        
        # 3. Componente ML: Predice la categoría técnica global
        pred_class = str(self.classifier.predict([q])[0])
        
        # Retorna el diagnóstico completo estructurado
        return {
            "consulta": query,
            "reglas": fired_rules if fired_rules else ["regla_generica_soporte"],
            "evidencia": self.docs[best_idx],
            "similitud": float(sims[best_idx]),
            "clase": pred_class
        }

def generar_reporte(resultados: list[dict]):
    """Genera y guarda el archivo Markdown `semana05.md` con las evidencias de ejecución y la tabla."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Reporte de Pruebas - Semana 05: Asistente de Soporte TI",
        "",
        "## Integrantes del Proyecto",
        "* **Marco Molina Molina**",
        "* **Daniel Eduardo Daza Cuello**",
        "* **Institución / Curso:** ETITC - 10º Semestre",
        "",
        "## Enlace al Repositorio",
        "[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)",
        "",
        "---",
        "",
        "Registro automatizado de ejecución del sistema híbrido utilizando la base de conocimiento de 30 entradas.",
        ""
    ]
    # Iteración sobre los resultados obtenidos para formatear cada prueba en el informe
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
    
    # Secciones finales con la tabla comparativa por categorías y conclusiones
    lines.extend([
        "---",
        "",
        "# Tabla de distribución por categorías de la Base de Conocimiento",
        "",
        "| **Categoría** | **Situación / Casos Registrados** | **Acción Recomendada / Evidencia** |",
        "|---|---|---|",
        "| **Hardware** | Equipo caliente / ventilador ruidoso | Revisar ventilación y limpiar ventilador; verificar piezas visibles; lubricar partes móviles |",
        "| | Sistema no enciende o placa base falla | Verificar fuente de poder; revisar conexiones de cables; inspeccionar condensadores |",
        "| | Pantalla azul en sistema operativo | Actualizar controladores de video y chipset; ejecutar diagnóstico de RAM |",
        "| | Fallas físicas en disco duro | Ejecutar comando chkdsk; verificar sectores defectuosos; respaldar información |",
        "| | Periféricos y componentes adicionales | Revisar puertos USB; cambiar cables de datos; reinstalar drivers |",
        "| **Red** | Conexión de internet intermitente | Revisar DNS y enlace de red; comprobar router; reiniciar módem; verificar cableado |",
        "| | Falla total de conectividad local | Comprobar IP estático/DHCP; verificar estado de switch; probar ping al gateway |",
        "| | Interferencia en red Wi-Fi | Cambiar canal inalámbrico; acercar al punto de acceso; actualizar firmware |",
        "| **Seguridad** | Alerta de virus o troyano detectado | Ejecutar análisis completo; aislar el equipo; poner en cuarentena archivos |",
        "| | Intento de acceso no autorizado | Revisar registros de eventos de seguridad; bloquear direcciones IP sospechosas |",
        "| | Compromiso de credenciales de usuario | Forzar cambio inmediato de contraseña; revocar sesiones activas |",
        "| **Rendimiento** | Aplicación lenta y alto consumo de memoria | Monitorear procesos en Administrador de tareas; finalizar procesos pesados |",
        "| | Procesador (CPU) al 100% de uso | Identificar procesos en bucle; optimizar inicio; aplicar parches del SO |",
        "| **Almacenamiento** | Disco lleno y falta de espacio libre | Liberar espacio eliminando temporales y caché; vaciar papelera; migrar datos |",
        "| **Software** | Error crítico en aplicación o spooler | Revisar logs de aplicación; reiniciar servicio spooler; reinstalar drivers |",
        "",
        "---",
        "",
        "### Conclusiones:",
        "",
        "#### 1. Funcionamiento del enfoque híbrido:",
        "Combinar reglas lógicas con un sistema de búsqueda basado en texto permite aprovechar lo mejor de ambos mundos. Por un lado, las reglas aseguran que las alertas críticas sean detectadas con precisión determinista, y por otro, la similitud coseno recupera el procedimiento técnico más afín cuando el usuario describe un problema en lenguaje natural libre.",
        "",
        "#### 2. Crecimiento y orden en la base de conocimiento:",
        "Al estructurar las 30 entradas técnicas en el archivo `data/base_conocimiento.txt`, el asistente cuenta con una fuente de referencia amplia y organizada para soporte de hardware, red, seguridad, rendimiento y almacenamiento. Esto, junto con el registro en `artifacts/audit.log`, garantiza trazabilidad de extremo a extremo.",
        "",
        "#### 3. Evolución global del proyecto:",
        "La integración de la taxonomía (Semana 03), el planificador $A^*$ (Semana 04) y el sistema híbrido con TF-IDF (Semana 05) en un panel interactivo (`dashboard.py`) demuestra un avance técnico sólido para la entrega del Corte 1."
    ])
    
    # Guarda el contenido generado en el archivo `.md` de reporte
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[✔] Reporte generado exitosamente en: {REPORT_PATH}")