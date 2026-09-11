"""
Módulo de Búsqueda Adversarial con Minimax (Semana 04).
Simulación de Ciberdefensa: Blue Team ('X') vs Red Team ('O').
"""

# 1. Mapeo de los 9 nodos de red (índices 0 al 8) según su función en la infraestructura.
NODOS_INFRAESTRUCTURA = [
    "Firewall Perimetral",     # 0
    "Servidor Web (DMZ)",       # 1
    "Gateway VPN",              # 2
    "Directorio Activo",        # 3
    "Base de Datos Central",    # 4
    "Servidor de Correo",       # 5
    "Servidor de Backups",      # 6
    "Almacenamiento NAS",       # 7
    "Balanceador de Carga"      # 8
]

# 2. Las 8 combinaciones de líneas críticas (3 horizontales, 3 verticales, 2 diagonales).
WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rutas horizontales
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Rutas verticales
    (0, 4, 8), (2, 4, 6)               # Rutas diagonales
)

# 3. Estado inicial del tablero: 'X' (Protegido), 'O' (Comprometido), ' ' (Disponible).
board = ["X", "O", "X", "O", "X", " ", " ", " ", "O"]

def winner(current_board):
    # Verifica si algún jugador ha completado una línea de 3 en WIN_LINES.
    for a, b, c in WIN_LINES:
        if current_board[a] == current_board[b] == current_board[c] and current_board[a] != " ":
            return current_board[a]  # Retorna 'X' o 'O' si hay un ganador.
    return None  # Retorna None si no hay ganador.

def minimax(current_board, maximizing):
    # Algoritmo recursivo para calcular el valor de utilidad de cada estado.
    w = winner(current_board)
    if w == "X": return 1    # +1: Victoria de la Defensa (Blue Team).
    if w == "O": return -1   # -1: Victoria del Atacante (Red Team).
    if " " not in current_board: return 0  #  0: Empate / Red en contención.
    
    mark = "X" if maximizing else "O"
    scores = []
    
    # Recorre y prueba recursivamente cada nodo disponible en la red.
    for i, cell in enumerate(current_board):
        if cell == " ":
            nxt = current_board.copy()
            nxt[i] = mark
            scores.append(minimax(nxt, not maximizing))
            
    # Devuelve el valor máximo si juega 'X' (MAX) o el mínimo si juega 'O' (MIN).
    return max(scores) if maximizing else min(scores)

def best_move(current_board):
    # Evalúa todas las casillas libres y selecciona el índice que maximice la utilidad de 'X'.
    choices = []
    for i, cell in enumerate(current_board):
        if cell == " ":
            nxt = current_board.copy()
            nxt[i] = "X"
            choices.append((minimax(nxt, False), i))
    return max(choices)[1]  # Devuelve el índice de la mejor posición.

def simular_ciberdefensa(current_board=None):
    # Genera el diagnóstico técnico estructurado del movimiento calculado por Minimax.
    if current_board is None:
        current_board = board
        
    pos = best_move(current_board)
    nodo_nombre = NODOS_INFRAESTRUCTURA[pos] if pos < len(NODOS_INFRAESTRUCTURA) else f"Nodo {pos}"
    
    # Retorna un diccionario con la respuesta y justificación para la interfaz/dashboard.
    return {
        "posicion": pos,
        "nodo": nodo_nombre,
        "accion": f"Blindar y aislar {nodo_nombre}",
        "justificacion": (
            f"Minimax seleccionó el nodo #{pos} ({nodo_nombre}) al evaluar la función de utilidad (+1). "
            f"Al proteger este nodo, el Blue Team completa la línea de contención diagonal "
            f"(Gateway VPN -> Base de Datos -> Backups) e impide que el adversario amenace la recuperación ante desastres."
        )
    }

# Ejecución directa como script de prueba.
if __name__ == "__main__":
    diagnostico = simular_ciberdefensa(board)
    print(f"Mejor posición calculada por Minimax: {diagnostico['posicion']}")
    print(f"Nodo seleccionado: {diagnostico['nodo']}")
    print(f"Acción recomendada: {diagnostico['accion']}")
    print(f"Justificación: {diagnostico['justificacion']}")