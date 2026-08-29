from audit.logger_audit import registrar_traza
from rules.prioritizer import calcular_prioridad
from classifiers.taxonomia import classify_problem
from classifiers.evaluacion_modelo import ejecutar_validacion
from classifiers.astar import astar_soporte_ti, START_STATE, GOAL_STATE
from classifiers.minimax import best_move, board as minimax_board

def main():
    print("=== 1. VALIDACIÓN DEL MODELO BASE (MATRIZ DE CONFUSIÓN) ===")
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

    print("\n" + "="*50 + "\n")
    print("=== 3. PLANIFICADOR DE SOPORTE TI CON A* (SEMANA 4) ===")
    print(f"Estado Inicial: {START_STATE} -> Estado Meta: {GOAL_STATE}")
    ruta, costo_total = astar_soporte_ti(START_STATE, GOAL_STATE)
    print(f"Costo acumulado mínimo de resolución: {costo_total}")
    print("Secuencia óptima de acciones técnicas:")
    if ruta:
        for idx, (orig, dest, desc, c) in enumerate(ruta, 1):
            print(f"  {idx}. [{desc}] (Costo: {c}) | Transición: {orig} -> {dest}")
    else:
        print("No se encontró una ruta válida.")

    print("\n" + "="*50 + "\n")
    print("=== 4. DECISIÓN ADVERSARIAL CON MINIMAX (SEMANA 4) ===")
    print(f"Tablero actual de recursos/jugada: {minimax_board}")
    mejor_pos = best_move(minimax_board)
    print(f"Mejor posición estratégica seleccionada por Minimax: {mejor_pos}")
    print("==================================================")

if __name__ == "__main__":
    main()