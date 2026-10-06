import json
import heapq

def load_data(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['graph'], data['heuristics']

def run_a_star(filename, start_city, target_city):
    """
    Main function called by your main program.
    Accepts the filename parameter, loads data, and executes A* search algorithm.
    """

    graph, heuristics = load_data(filename)

    if start_city == target_city:
        return [start_city], 0

    pq = [(heuristics.get(start_city, 0), 0, start_city, [start_city])]
    g_scores = {start_city:0}
    closed_set = set()

    while pq:
        f, g, current, path = heapq.heappop(pq)

        if current == target_city:
            return path, g

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbor, weight in graph.get(current, {}).items():
            if neighbor in closed_set:
                continue

            tentative_g = g + weight

            if tentative_g < g_scores.get(neighbor, float('inf')):
                g_scores[neighbor] = tentative_g
                f = tentative_g + heuristics.get(neighbor, 0)
                heapq.heappush(pq, (f, tentative_g, neighbor, path + [neighbor]))

    return None, float('inf')