# 1. Importación de módulos internos del proyecto (Auditoría, Reglas, Clasificadores e IA)
from audit.logger_audit import registrar_traza
from rules.prioritizer import calcular_prioridad
from classifiers.taxonomia import classify_problem
from classifiers.evaluacion_modelo import ejecutar_validacion
from classifiers.astar import astar_soporte_ti, START_STATE, GOAL_STATE
from classifiers.minimax import best_move, board as minimax_board, simular_ciberdefensa
from classifiers.sistema_hibrido import SistemaHibridoSoporte, generar_reporte

def main():
    # === SECCIÓN 1: Validación del Modelo Base ===
    # Ejecuta la evaluación reproducible (Semana 02) imprimiendo la matriz de confusión y el accuracy del 92.1%
    print("=== 1. VALIDACIÓN DEL MODELO BASE (MATRIZ DE CONFUSIÓN) ===")
    ejecutar_validacion()
    
    print("\n" + "="*50 + "\n")
    
    # Datos de prueba para simular la recepción de un ticket de soporte real
    ticket_id = "TICK-2026-001"
    descripcion = "El departamento de Contabilidad reporta que la aplicacion de nomina se cierra inesperadamente al generar el informe fiscal mensual."
    impacto = "Alto"
    urgencia = "Alto"

    # === SECCIÓN 2: Triage y Clasificación de Ticket ===
    print(f"=== 2. PROCESANDO TICKET DE SOPORTE: {ticket_id} ===")
    
    # 1. Registra el evento de recepción en el archivo persistente 'artifacts/audit.log'
    registrar_traza(ticket_id, "RECEPCION", f"Ticket recibido con descripción: '{descripcion}'")

    # 2. Asigna la categoría técnica usando la taxonomía de palabras clave (Semana 03)
    categoria_principal, categorias_detectadas, _ = classify_problem(descripcion)
    registrar_traza(ticket_id, "TAXONOMIA", f"Categoría principal: '{categoria_principal}' | Detectadas: {categorias_detectadas}")

    # 3. Calcula el nivel de prioridad (Crítico, Alto, Medio, Bajo) según el impacto y urgencia
    prioridad = calcular_prioridad(impacto, urgencia)
    registrar_traza(ticket_id, "PRIORIZACION", f"Impacto: {impacto}, Urgencia: {urgencia} -> Asignada Prioridad: {prioridad}")

    # Muestra los resultados del triage inicial por consola
    print(f"\nResultado del análisis:")
    print(f"- Categoría de Software (IA): **{categoria_principal}**")
    print(f"- Prioridad asignada: **{prioridad}**")
    print(f"- Traza guardada correctamente en artifacts/audit.log.")

    print("\n" + "="*50 + "\n")
    
    # === SECCIÓN 3: Planificación de Secuencia de Solución con A* ===
    # Calcula la ruta óptima de menor esfuerzo para reparar los componentes (Semana 04)
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
    
    # === SECCIÓN 4: Ciberdefensa Adversarial con Minimax ===
    # Simula la toma de decisión óptima para blindar la red ante una amenaza externa (Semana 04)
    print("=== 4. CIBERDEFENSA Y DECISIÓN ADVERSARIAL CON MINIMAX (SEMANA 4) ===")
    print(f"Estado de red actual (Matriz 3x3): {minimax_board}")
    diag_minimax = simular_ciberdefensa(minimax_board)
    print(f"Mejor posición estratégica seleccionada por Minimax: {diag_minimax['posicion']} ({diag_minimax['nodo']})")
    print(f"Acción defensiva recomendada: {diag_minimax['accion']}")
    print(f"Justificación técnica: {diag_minimax['justificacion']}")

    print("\n" + "="*50 + "\n")
    
    # === SECCIÓN 5: Motor Híbrido (Reglas + TF-IDF + ML + RAG) ===
    # Procesa consultas en lenguaje natural consultando la base de conocimiento de 30 procedimientos (Semana 05)
    print("=== 5. SISTEMA HÍBRIDO E INFORMES DE CONOCIMIENTO (SEMANA 05) ===")
    sistema = SistemaHibridoSoporte()
    
    pruebas = [
        "El equipo esta muy caliente y el ventilador hace ruido",
        "La conexion de internet cae constantemente y falla el enlace",
        "El disco duro esta lleno y la aplicacion esta muy lenta"
    ]
    
    # Procesa cada consulta de prueba a través de las 3 capas del sistema híbrido
    resultados = [sistema.procesar(p) for p in pruebas]
    
    for idx, r in enumerate(resultados, start=1):
        print(f"\n--- Prueba Híbrida {idx} ---")
        print(f"Consulta:   {r['consulta']}")
        print(f"Reglas:     {r['reglas']}")
        print(f"Evidencia:  {r['evidencia']}")
        print(f"Similitud:  {r['similitud']:.4f}")
        print(f"Clase:      {r['clase']}")
        
    # Genera el reporte final de Markdown 'reports/semana05.md' y registra la traza final de ejecución
    generar_reporte(resultados)
    registrar_traza(ticket_id, "SISTEMA_HIBRIDO", "Ejecución completa del sistema híbrido de la Semana 05 con base de conocimiento.")
    print("==================================================")

# Punto de entrada para ejecutar la orquestación completa al correr 'python src/main.py'
if __name__ == "__main__":
    main()