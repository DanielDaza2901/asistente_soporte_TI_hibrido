"""
Motor de referencia inteligente (Semana 16)
Asistente de Soporte TI Híbrido
"""
import re
import unicodedata
from typing import Dict, Any, List, Optional
from classifiers.base_conocimiento import BaseConocimiento, VALIDADO

def normalizar_texto(texto: str) -> set:
    """
    Normalizador de texto: convierte a minúsculas (casefold), elimina tildes y caracteres especiales,
    y extrae tokens alfanuméricos únicos.
    """
    if not isinstance(texto, str) or not texto.strip():
        return set()
    base = unicodedata.normalize("NFD", texto.casefold().strip())
    sin_tildes = "".join(c for c in base if unicodedata.category(c) != "Mn")
    return set(re.findall(r"[a-z0-9]+", sin_tildes))

class MotorReferencia:
    """
    Motor de búsqueda y recuperación de información basado exclusivamente 
    en fuentes validadas de la Base de Conocimiento (Semana 15).
    """
    
    def __init__(self, bc: Optional[BaseConocimiento] = None):
        self.bc = bc if bc else BaseConocimiento()

    def consultar(self, pregunta: str) -> Dict[str, Any]:
        """
        Consulta el motor de referencia con una pregunta del usuario.
        Gestiona los tres escenarios de control de calidad:
        - VACIA: Si no se ingresa texto válido.
        - ENCONTRADA: Si existe al menos una referencia validada relevante.
        - SIN_REFERENCIA: Si no hay información aprobada (el sistema se abstiene de inventar).
        """
        if not isinstance(pregunta, str) or not pregunta.strip():
            return {
                "estado": "VACIA",
                "pregunta": pregunta,
                "mensaje": "Debe ingresar una pregunta válida para consultar el sistema inteligente.",
                "referencia": None
            }

        tokens_pregunta = normalizar_texto(pregunta)
        if not tokens_pregunta:
            return {
                "estado": "VACIA",
                "pregunta": pregunta,
                "mensaje": "La pregunta no contiene términos alfanuméricos válidos para procesar.",
                "referencia": None
            }

        # Recuperar estrictamente artículos con estado VALIDADO (excluyendo BORRADOR)
        articulos_validados = self.bc.listar_publicados()
        
        candidatos = []
        for art in articulos_validados:
            # Combinar campos clave del artículo para el análisis de coincidencia
            texto_referencia = f"{art['titulo']} {art['contenido']} {art['aplicacion']} {art['dominio']}"
            tokens_art = normalizar_texto(texto_referencia)
            
            # Calcular intersección de tokens (coincidencias de palabras clave)
            coincidencias = tokens_pregunta.intersection(tokens_art)
            puntaje = len(coincidencias)
            
            if puntaje > 0:
                candidatos.append({
                    "id": f"REF-{art['id_articulo']:03d}",
                    "id_articulo": art['id_articulo'],
                    "titulo": art['titulo'],
                    "respuesta": art['contenido'],
                    "fuente": art['fuente'],
                    "dominio": art['dominio'],
                    "aplicacion": art['aplicacion'],
                    "experto": art['experto'],
                    "estado": art['estado'],
                    "puntaje": puntaje,
                    "coincidencias": list(coincidencias)
                })

        # Control de calidad: Si no hay candidatos o ninguno está validado, abstenerse de responder
        if not candidatos:
            return {
                "estado": "SIN_REFERENCIA",
                "pregunta": pregunta,
                "mensaje": "No se encontró información aprobada o validada que responda a su consulta. El sistema se abstiene de inventar respuestas.",
                "referencia": None
            }

        # Ordenar candidatos de mayor a menor puntaje de coincidencia
        candidatos.sort(key=lambda x: x["puntaje"], reverse=True)
        mejor_match = candidatos[0]

        return {
            "estado": "ENCONTRADA",
            "pregunta": pregunta,
            "mensaje": "Se encontró una referencia validada relevante.",
            "referencia": mejor_match,
            "candidatos_alternativos": candidatos[1:]
        }

if __name__ == "__main__":
    print("=== PRUEBA RÁPIDA: MOTOR DE REFERENCIA (SEMANA 16) ===")
    motor = MotorReferencia()
    if not motor.bc.existe_base():
        motor.bc.crear_esquema(con_datos=True)
    
    res = motor.consultar("Cómo calcular la prioridad con matriz impacto urgencia")
    print(f"Estado: {res['estado']}")
    if res["referencia"]:
        print(f"Referencia: {res['referencia']['id']} - {res['referencia']['titulo']}")
        print(f"Fuente: {res['referencia']['fuente']}")