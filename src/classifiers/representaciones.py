import numpy as np

def ejecutar_representaciones_hibridas():
    """
    Ejecuta las tres representaciones del reconocimiento adaptadas al
    Asistente de Soporte TI Híbrido (Triaje numérico, Diagnóstico simbólico y Autómata de Fallas en Cascada).
    """
    
    print("=== 1. REPRESENTACIÓN NUMÉRICA (Triaje Híbrido de Tickets) ===")
    # Vector de características: [Impacto de Infraestructura (1-10), Urgencia de Tiempo (1-10), Sentimiento Negativo NLP (0.0-1.0)]
    ticket_entrada = np.array([8.5, 9.0, 0.95])  
    perfil_critico = np.array([10.0, 10.0, 1.0]) 
    
    distancia = np.linalg.norm(ticket_entrada - perfil_critico)
    
    print(f"Vector Ticket Actual: {ticket_entrada}")
    print(f"Vector Perfil Crítico: {perfil_critico}")
    print(f"Distancia numérica (similitud a escalamiento inmediato): {round(float(distancia), 3)}")
    
    if distancia < 3.0:
        print("-> Alerta de Triaje: Clasificación prioritaria. Asignando directamente a Especialista Humano.\n")


    print("=== 2. REPRESENTACIÓN SIMBÓLICA (Enrutamiento y Diagnóstico General) ===")
    hechos_ticket = {"pantalla_azul", "reinicio_constante", "codigo_stop", "equipo_portatil"}
    print(f"Hechos detectados por el Asistente: {hechos_ticket}")
    
    regla_hardware_critico = {"pantalla_azul", "reinicio_constante"}
    regla_accesos = {"olvido_contrasena", "active_directory"}
    
    if regla_hardware_critico.issubset(hechos_ticket):
        print("-> Conclusión simbólica: diagnostico_falla_hardware_fisico")
        print("-> Acción recomendada: Desviar al módulo de Soporte de Campo (Presencial).\n")
    elif regla_accesos.issubset(hechos_ticket):
        print("-> Conclusión simbólica: diagnostico_restablecimiento_credenciales")
        print("-> Acción recomendada: Ejecutar script de automatización de reseteo (Nivel 1 - Bot).\n")


    print("=== 3. AUTÓMATA (Validación de Cronologías / Falla en Cascada) ===")
    # Autómata Finito Determinista (AFD) para analizar secuencias de eventos técnicos en logs.
    # Alfabeto: 'O' (Operativo), 'E' (Error), 'T' (Timeout)
    # Objetivo: Reconocer si la secuencia termina en "ET" (Error seguido inmediatamente de Timeout).
    
    def acepta_patron_falla_cascada(secuencia_logs):
        state = "q0" # Estado inicial
        
        transitions = {
            ("q0", "O"): "q0", 
            ("q0", "T"): "q0", 
            ("q0", "E"): "q1", # Detecta Error, avanza a q1
            
            ("q1", "O"): "q0", # Se recupera, vuelve a q0
            ("q1", "E"): "q1", # Continúan errores
            ("q1", "T"): "q2", # Timeout tras Error -> Estado de Aceptación (q2)
            
            ("q2", "O"): "q0", 
            ("q2", "T"): "q0", 
            ("q2", "E"): "q1",
        }
        
        for simbolo in secuencia_logs:
            if (state, simbolo) in transitions:
                state = transitions[(state, simbolo)]
            else:
                return False 
                
        return state == "q2"

    casos_prueba = [
        "OOET",   # Termina en ET -> Falla en cascada (Aceptada)
        "OEE",    # Termina en Errores, pero sin Timeout -> (Rechazada)
        "ETOO",   # Tuvo la falla pero se estabilizó al final -> (Rechazada)
        "OOOEET"  # Múltiples errores y luego Timeout final -> (Aceptada)
    ]
    
    for seq in casos_prueba:
        resultado = acepta_patron_falla_cascada(seq)
        estado = "Aceptada (Falla Crítica Confirmada)" if resultado else "Rechazada (Comportamiento Normal/Recuperado)"
        print(f"Secuencia de logs '{seq}': {estado}")

if __name__ == "__main__":
    ejecutar_representaciones_hibridas()