import logging
from datetime import datetime
from pathlib import Path

# Ruta raíz absoluta del proyecto (sube 2 niveles desde src/audit/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
LOG_FILE = ARTIFACTS_DIR / "audit.log"

# Crear carpeta artifacts si no existe en la raíz
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# Configurar el sistema de logging para trazabilidad con ruta absoluta segura
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def registrar_traza(ticket_id: str, accion: str, detalles: str):
    """Registra una acción en el sistema de auditoría con marca de tiempo."""
    mensaje = f"TICKET_ID: {ticket_id} | ACCIÓN: {accion} | DETALLES: {detalles}"
    logging.info(mensaje)
    print(f"[AUDIT TRAZA] {mensaje}")