import heapq


def run_a_star(graph, heuristics, start_city, target_city):
    if start_city == target_city:
        path, distance = [start_city], 0
        print('A* path:', ' -> '.join(path))
        print('A* total distance:', distance, 'miles')
        return path, distance

    pq = [(heuristics.get(start_city, {}).get(target_city, 0), 0, start_city, [start_city])]
    g_scores = {start_city: 0}
    closed_set = set()

    while pq:
        _, g, current, path = heapq.heappop(pq)

        if current == target_city:
            print('A* path:', ' -> '.join(path))
            print('A* total distance:', g, 'miles')
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
                heuristic = heuristics.get(neighbor, {}).get(target_city, 0)
                heapq.heappush(
                    pq,
                    (tentative_g + heuristic, tentative_g, neighbor, path + [neighbor]),
                )

    print('A*: No route found.')
    return None, float('inf')