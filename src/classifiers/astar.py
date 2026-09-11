# Importa la librería estándar 'heapq' que proporciona funciones para manejar 
# listas como colas de prioridad basadas en un montículo binario (min-heap).
import heapq

# Estado inicial del sistema representado como la tupla (Red, Base de Datos, Aplicación).
# Los valores (0, 0, 0) indican que ningún componente ha recibido mantenimiento/reparación.
START_STATE = (0, 0, 0)

# Estado objetivo a alcanzar (2, 2, 2): los 3 componentes están en nivel 2 (100% restablecidos).
GOAL_STATE = (2, 2, 2)

# Define la función heurística h(n) que estima el costo restante desde el estado actual hasta la meta.
def h(node, goal):
    # Utiliza la distancia de Manhattan: suma las diferencias absolutas entre cada componente
    # del estado actual (n) y del estado meta (g).
    return sum(abs(n - g) for n, g in zip(node, goal))

# Función generadora de vecinos (transiciones de estado / acciones posibles).
def neighbors(node):
    # Desempaqueta la tupla del estado actual en variables independientes: Red, DB y App.
    net, db, app = node
    # Lista vacía donde se almacenarán las acciones válidas que se pueden ejecutar desde este estado.
    possible_actions = []
    
    # Si la red no ha alcanzado el nivel máximo (2), se añade la acción de reparar red.
    if net < 2:
        # Retorna: ((nuevo_estado), costo_de_la_acción, "descripción")
        possible_actions.append(((net + 1, db, app), 1, "Reiniciar interfaces de red"))
        
    # Si la base de datos no está en nivel 2, añade la acción de recuperación de DB (costo 2).
    if db < 2:
        possible_actions.append(((net, db + 1, app), 2, "Aplicar script de recuperación en Base de Datos"))
        
    # Si la aplicación no está en nivel 2, añade la acción de aplicar hotfix (costo 3).
    if app < 2:
        possible_actions.append(((net, db, app + 1), 3, "Desplegar hotfix en microservicio backend"))
        
    # Retorna la lista con todos los estados vecinos alcanzables desde el estado actual.
    return possible_actions

# Algoritmo principal A* para encontrar la secuencia de pasos con el costo mínimo.
def astar_soporte_ti(start, goal):
    # Inicializa la frontera (min-heap) con el estado inicial. 
    # Estructura de la tupla: (prioridad_f, estado_actual, lista_de_pasos_recorridos)
    frontier = [(0, start, [])]
    
    # Diccionario 'cost_so_far' que guarda el costo real mínimo g(n) conocido para llegar a cada nodo.
    cost_so_far = {start: 0}
    
    # Bucle principal: se ejecuta mientras existan nodos por explorar en la frontera.
    while frontier:
        # Extrae de la frontera el nodo con la prioridad f(n) más baja (el más prometedor).
        current_priority, current_node, path = heapq.heappop(frontier)
        
        # Evalúa si hemos llegado al estado meta (criterio de parada del algoritmo).
        if current_node == goal:
            # Retorna el camino de acciones acumulado y el costo total real consumido.
            return path, cost_so_far[current_node]
            
        # Explora cada uno de los nodos vecinos generados a partir del nodo actual.
        for nxt_node, step_cost, action_desc in neighbors(current_node):
            # Calcula el nuevo costo real g(n) para llegar al nodo vecino:
            # costo acumulado del nodo actual + costo del paso hacia el vecino.
            new_cost = cost_so_far[current_node] + step_cost
            
            # Comprueba si el vecino es nuevo O si encontramos una ruta con un costo menor hacia él.
            if nxt_node not in cost_so_far or new_cost < cost_so_far[nxt_node]:
                # Registra o actualiza el costo real óptimo g(n) para este nodo vecino.
                cost_so_far[nxt_node] = new_cost
                
                # Calcula la función de evaluación A*: f(n) = g(n) + h(n)
                # f(n) = Costo real acumulado + Estimación heurística restante.
                priority = new_cost + h(nxt_node, goal)
                
                # Agrega el vecino a la frontera con su prioridad f(n) y el camino actualizado.
                heapq.heappush(frontier, (priority, nxt_node, path + [(current_node, nxt_node, action_desc, step_cost)]))
                
    # Si la frontera se vacía y no se encontró camino al objetivo, retorna None e infinito.
    return None, float('inf')

# Bloque condicional estándar de Python para ejecutar el código si se corre como script directo.
if __name__ == "__main__":
    # Llama a la función A* con los estados inicial y objetivo configurados.
    ruta, costo = astar_soporte_ti(START_STATE, GOAL_STATE)
    
    # Muestra por consola el resultado de la secuencia óptima obtenida y el costo total.
    print("Ruta A*:", ruta, "Costo:", costo)