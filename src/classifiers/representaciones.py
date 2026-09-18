import numpy as np

def ejecutar_representaciones():
    """
    Ejecuta las tres representaciones del reconocimiento adaptadas al
    proyecto del Asistente de Soporte TI Híbrido.
    """
    
    print("=== 1. REPRESENTACIÓN NUMÉRICA (Telemetría de Servidores) ===")
    # Representación Numérica: Vector de características de rendimiento de un servidor.
    # Características (Alfabeto numérico): [Uso CPU (%), Uso RAM (%), Latencia de Red (ms)]
    
    # Muestra: Estado reportado en un ticket de soporte actual
    ticket_actual = np.array([95.0, 92.0, 350.0])  
    
    # Referencia: Perfil estadístico de un servidor al borde del colapso crítico
    perfil_colapso = np.array([98.0, 95.0, 400.0]) 
    
    # Cálculo de la medida de distancia (Norma Euclidiana)
    distancia = np.linalg.norm(ticket_actual - perfil_colapso)
    
    print(f"Vector Ticket Actual: {ticket_actual}")
    print(f"Vector Perfil Crítico: {perfil_colapso}")
    print(f"Distancia numérica (similitud a colapso): {round(float(distancia), 3)}")
    if distancia < 60.0:
        print("-> Alerta de Reconocimiento: El servidor actual es altamente similar al perfil de colapso.\n")


    print("=== 2. REPRESENTACIÓN SIMBÓLICA (Reglas de Diagnóstico) ===")
    # Representación Simbólica: Base de hechos extraídos del lenguaje natural del usuario.
    
    hechos_ticket = {"ping_fallido", "servidor_no_responde", "luces_rojas_switch"}
    
    print(f"Hechos detectados en el ticket: {hechos_ticket}")
    
    # Regla Experta: SI se cumplen ciertas condiciones -> ENTONCES disparar un diagnóstico
    if {"ping_fallido", "servidor_no_responde"}.issubset(hechos_ticket):
        print("-> Conclusión simbólica: diagnostico_caida_red_masiva")
        print("-> Acción recomendada: Ejecutar protocolo de contingencia y aislar el nodo (Nivel 3).\n")


    print("=== 3. AUTÓMATA (Reconocimiento de Patrones de Logs) ===")
    # Autómata Finito Determinista (AFD) para analizar secuencias de eventos técnicos.
    # Alfabeto: 'O' (Estado Operativo), 'E' (Error de aplicación), 'T' (Timeout de base de datos)
    # Objetivo: Reconocer si la secuencia de logs termina exactamente en "ET" (Error seguido inmediatamente por Timeout), 
    # lo cual es el patrón clásico de una falla en cascada.
    
    def acepta_patron_falla_cascada(secuencia_logs):
        state = "q0" # Estado inicial
        
        # Tabla de transiciones
        transitions = {
            # Estando en q0 (Sistema estable)
            ("q0", "O"): "q0", 
            ("q0", "T"): "q0", 
            ("q0", "E"): "q1", # Se detecta un Error, avanza a q1
            
            # Estando en q1 (Error detectado)
            ("q1", "O"): "q0", # Se recupera el sistema, vuelve a q0
            ("q1", "E"): "q1", # Continúan los errores, se mantiene en q1
            ("q1", "T"): "q2", # Ocurre Timeout tras el Error, avanza a q2 (Estado de Aceptación)
            
            # Estando en q2 (Patrón 'ET' detectado)
            ("q2", "O"): "q0", # Se recupera, vuelve a q0
            ("q2", "T"): "q0", # Otro Timeout rompe el patrón exacto "ET", vuelve a q0
            ("q2", "E"): "q1", # Nuevo Error, vuelve a rastrear el patrón en q1
        }
        
        for simbolo in secuencia_logs:
            if (state, simbolo) in transitions:
                state = transitions[(state, simbolo)]
            else:
                return False # Rechaza símbolos que no pertenecen al alfabeto
                
        # Estado de Aceptación
        return state == "q2"

    # Casos de prueba adaptados al soporte técnico
    casos_prueba = [
        "OOET",    # Termina en ET -> Falla en cascada (Aceptada)
        "OEE",     # Termina en Errores, pero sin Timeout -> (Rechazada)
        "ETOO",    # Tuvo la falla pero se estabilizó al final -> (Rechazada)
        "OOOEET"   # Múltiples errores y luego Timeout final -> (Aceptada)
    ]
    
    for seq in casos_prueba:
        resultado = acepta_patron_falla_cascada(seq)
        estado = "Aceptada (Falla Crítica Confirmada)" if resultado else "Rechazada (Comportamiento Normal/Recuperado)"
        print(f"Secuencia de logs '{seq}': {estado}")

if __name__ == "__main__":
    ejecutar_representaciones()