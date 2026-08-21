import logging
import os
from datetime import datetime

# Crear carpeta artifacts si no existe
os.makedirs("artifacts", exist_ok=True)

# Configurar el sistema de logging para trazabilidad
logging.basicConfig(
    filename="artifacts/audit.log",
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def registrar_traza(ticket_id: str, accion: str, detalles: str):
    """Registra una acción en el sistema de auditoría con marca de tiempo."""
    mensaje = f"TICKET_ID: {ticket_id} | ACCIÓN: {accion} | DETALLES: {detalles}"
    logging.info(mensaje)
    print(f"[AUDIT TRAZA] {mensaje}")