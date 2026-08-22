from audit.logger_audit import registrar_traza
from rules.prioritizer import calcular_prioridad
from classifiers.taxonomia import classify_problem
from classifiers.evaluacion_modelo import ejecutar_validacion

def procesar_ticket_prueba():
    print("=== 1. VALIDACIÓN DEL MODELO BASE (MATRIZ DE CONFUSIÓN) ===")
    # Llamamos a la matriz de confusión solicitada en la guía del profesor
    ejecutar_validacion()
    
    print("\n" + "="*50 + "\n")
    
    ticket_id = "TICK-2026-001"
    descripcion = "El departamento de Contabilidad reporta que la aplicacion de nomina se cierra inesperadamente al generar el informe fiscal mensual."
    impacto = "Alto"
    urgencia = "Alto"

    print(f"=== 2. PROCESANDO TICKET DE SOPORTE: {ticket_id} ===")
    
    # 1. Trazabilidad de entrada
    registrar_traza(ticket_id, "RECEPCION", f"Ticket recibido con descripción: '{descripcion}'")

    # 2. Clasificación automática por Taxonomía de IA (Semana 03)
    categoria_principal, categorias_detectadas, _ = classify_problem(descripcion)
    registrar_traza(ticket_id, "TAXONOMIA", f"Categoría principal: '{categoria_principal}' | Detectadas: {categorias_detectadas}")

    # 3. Aplicar Motor de Reglas / Priorización
    prioridad = calcular_prioridad(impacto, urgencia)
    registrar_traza(ticket_id, "PRIORIZACION", f"Impacto: {impacto}, Urgencia: {urgencia} -> Asignada Prioridad: {prioridad}")

    print(f"\nResultado del análisis:")
    print(f"- Categoría de Software (IA): **{categoria_principal}**")
    print(f"- Prioridad asignada: **{prioridad}**")
    print(f"- Traza guardada correctamente en artifacts/audit.log.")

if __name__ == "__main__":
    procesar_ticket_prueba()