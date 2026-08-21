def calcular_prioridad(impacto: str, urgencia: str) -> str:
    """
    Calcula la prioridad del incidente basándose en matrices de impacto y urgencia.
    Valores esperados: 'Bajo', 'Medio', 'Alto'
    """
    impacto = impacto.capitalize()
    urgencia = urgencia.capitalize()

    matriz = {
        ("Alto", "Alto"): "Crítica",
        ("Alto", "Medio"): "Alta",
        ("Alto", "Bajo"): "Media",
        ("Medio", "Alto"): "Alta",
        ("Medio", "Medio"): "Media",
        ("Medio", "Bajo"): "Baja",
        ("Bajo", "Alto"): "Media",
        ("Bajo", "Medio"): "Baja",
        ("Bajo", "Bajo"): "Baja"
    }

    return matriz.get((impacto, urgencia), "Media")