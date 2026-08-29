import heapq

START_STATE = (0, 0, 0)
GOAL_STATE = (2, 2, 2)

def h(node, goal):
    return sum(abs(n - g) for n, g in zip(node, goal))

def neighbors(node):
    net, db, app = node
    possible_actions = []
    if net < 2:
        possible_actions.append(((net + 1, db, app), 1, "Reiniciar interfaces de red"))
    if db < 2:
        possible_actions.append(((net, db + 1, app), 2, "Aplicar script de recuperación en Base de Datos"))
    if app < 2:
        possible_actions.append(((net, db, app + 1), 3, "Desplegar hotfix en microservicio backend"))
    return possible_actions

def astar_soporte_ti(start, goal):
    frontier = [(0, start, [])]
    cost_so_far = {start: 0}
    
    while frontier:
        current_priority, current_node, path = heapq.heappop(frontier)
        if current_node == goal:
            return path, cost_so_far[current_node]
            
        for nxt_node, step_cost, action_desc in neighbors(current_node):
            new_cost = cost_so_far[current_node] + step_cost
            if nxt_node not in cost_so_far or new_cost < cost_so_far[nxt_node]:
                cost_so_far[nxt_node] = new_cost
                priority = new_cost + h(nxt_node, goal)
                heapq.heappush(frontier, (priority, nxt_node, path + [(current_node, nxt_node, action_desc, step_cost)]))
                
    return None, float('inf')

if __name__ == "__main__":
    ruta, costo = astar_soporte_ti(START_STATE, GOAL_STATE)
    print("Ruta A*:", ruta, "Costo:", costo)