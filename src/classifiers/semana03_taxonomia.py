from dataclasses import dataclass
from pathlib import Path
import csv
import re
import unicodedata

# Ruta raíz del proyecto (sube dos niveles desde src/classifiers/)
ROOT = Path(__file__).resolve().parent.parent.parent
CSV_FILE = ROOT / "data" / "casos_ia.csv"
REPORT_FILE = ROOT / "reports" / "semana03.md"

@dataclass(frozen=True)
class Category:
    name: str
    keywords: tuple[str, ...]

CATEGORIES = [
    Category("Procesamiento de Lenguaje Natural (PLN)", (
        "chatbot", "consulten", "clasificar", "tickets", "correo", "corporativo", "solicitudes", "texto"
    )),
    Category("Aprendizaje Automático Predictivo", (
        "predecir", "bloqueo", "memoria", "picos", "consumo", "recursos", "historial", "estacion"
    )),
    Category("Búsqueda y Optimización de PC", (
        "optimizar", "rendimiento", "cache", "limpiar", "espacio", "disco", "energia", "suspension"
    )),
    Category("Sistemas Expertos y Reglas de Soporte", (
        "reglas", "impedir", "autorizado", "requisitos", "prioridades", "impacto", "politicas"
    )),
    Category("Automatización y Mantenimiento de Software", (
        "respaldo", "copia", "script", "restablecer", "dns", "sfc", "integridad", "automatizada"
    )),
    Category("Seguridad y Análisis de Errores (Logs)", (
        "troyano", "antivirus", "bloquea", "conexiones", "externos", "trafico", "analizar", "seguridad"
    )),
    Category("Sistemas de Recomendación y Diagnóstico", (
        "recomendar", "parches", "instalacion", "licencias", "equipos", "actualizaciones", "software"
    ))
]

CUSTOM_RULES = {
    "Seguridad y Análisis de Errores (Logs)": ("troyano", "antivirus", "financiero", "logistica"),
    "Automatización y Mantenimiento de Software": ("respaldo", "sfc", "dns", "administracion"),
    "Búsqueda y Optimización de PC": ("ventas", "comercial", "rendimiento", "cache"),
    "Sistemas Expertos y Reglas de Soporte": ("gerencia", "operaciones", "impacto", "prioridades"),
    "Procesamiento de Lenguaje Natural (PLN)": ("contabilidad", "recursos humanos", "chatbot", "tickets")
}

MANUAL_REFERENCE = [
    "Seguridad y Análisis de Errores (Logs)",
    "Sistemas de Recomendación y Diagnóstico",
    "Aprendizaje Automático Predictivo",
    "Búsqueda y Optimización de PC",
    "Sistemas de Recomendación y Diagnóstico",
    "Seguridad y Análisis de Errores (Logs)",
    "Búsqueda y Optimización de PC",
    "Procesamiento de Lenguaje Natural (PLN)",
    "Aprendizaje Automático Predictivo",
    "Sistemas Expertos y Reglas de Soporte",
    "Automatización y Mantenimiento de Software",
    "Procesamiento de Lenguaje Natural (PLN)",
    "Automatización y Mantenimiento de Software",
    "Sistemas Expertos y Reglas de Soporte",
    "Seguridad y Análisis de Errores (Logs)",
    "Sistemas de Recomendación y Diagnóstico",
    "Seguridad y Análisis de Errores (Logs)",
    "Sistemas Expertos y Reglas de Soporte",
    "Automatización y Mantenimiento de Software",
    "Búsqueda y Optimización de PC"
]

def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9]+", "", text)
    return re.sub(r"\s+", "", text).strip()

def normalize_header(text: str) -> str:
    return normalize(text).replace("_", "")

def contains_keyword(text: str, keyword: str) -> bool:
    normalized_text = f" {normalize(text)} "
    normalized_keyword = normalize(keyword)
    return f"{normalized_keyword}" in normalized_text

def build_categories() -> list[Category]:
    result = []
    for category in CATEGORIES:
        extra = CUSTOM_RULES.get(category.name, ())
        result.append(Category(category.name, category.keywords + tuple(extra)))
    return result

def classify_problem(text: str) -> tuple[str, list[str], dict[str, int]]:
    scores = {}
    for category in build_categories():
        score = sum(contains_keyword(text, keyword) for keyword in category.keywords)
        scores[category.name] = score
    
    matches = [
        (score, index, category.name)
        for index, category in enumerate(build_categories())
        if (score := scores[category.name]) > 0
    ]
    matches.sort(key=lambda item: (-item[0], item[1]))
    detected = [name for _, _, name in matches]
    primary = detected[0] if detected else "Requiere análisis"
    return primary, detected or ["Requiere análisis"], scores

def read_cases() -> list[str]:
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"No existe {CSV_FILE}.")
    
    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("El CSV está vacío.")
        reader.fieldnames = [normalize_header(name) for name in reader.fieldnames]
        
        cases = []
        for row in reader:
            description = (row.get("descripcion") or "").strip()
            if description:
                cases.append(description)
        return cases

def write_report(results: list[dict]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    reference_count = min(len(results), len(MANUAL_REFERENCE))
    matches = sum(1 for i in range(reference_count) if results[i]["primary"] == MANUAL_REFERENCE[i])
    accuracy = 100 * matches / reference_count if reference_count else 0.0

    lines = [
        "# Semana 03: Taxonomía de IA en Entorno Empresarial (Soporte TI)",
        "## Resultado automático frente a clasificación manual de referencia",
        "| Caso | Categoría automática principal | Categorías detectadas | Manual | Estado |",
        "|---|---|---|---|---|",
    ]
    for i, result in enumerate(results, start=1):
        manual = MANUAL_REFERENCE[i - 1] if i - 1 < len(MANUAL_REFERENCE) else "Pendiente"
        status = "Coincide" if result["primary"] == manual else "Revisar"
        detected = ", ".join(result["detected"])
        lines.append(f"| {i} | {result['primary']} | {detected} | {manual} | {status} |")
    
    lines.append(f"\nCoincidencia con la referencia: **{accuracy:.2f}%** ({matches}/{reference_count}).")
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
    cases = read_cases()
    results = []
    for case in cases:
        primary, detected, scores = classify_problem(case)
        results.append({"description": case, "primary": primary, "detected": detected, "scores": scores})
    write_report(results)
    print(f"Reporte generado en: {REPORT_FILE}")

if __name__ == "__main__":
    main()