import heapq


def run_a_star(graph, heuristics, cities, start_city, target_city):
    if start_city == target_city:
        path, distance = [start_city], 0
        print("A* path:", " -> ".join(path))
        print("A* total distance:", distance, "miles")
        return path, distance

    start_index = cities.index(start_city)
    target_index = cities.index(target_city)
    frontier = [
        (heuristics[start_index][target_index], 0, start_index, [start_index])
    ]
    g_scores = {start_index: 0}
    closed_set = set()

    while frontier:
        _, cost_so_far, current, path = heapq.heappop(frontier)
        if current == target_index:
            city_path = [cities[city_index] for city_index in path]
            print("A* path:", " -> ".join(city_path))
            print("A* total distance:", cost_so_far, "miles")
            return city_path, cost_so_far

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbour, weight in enumerate(graph[current]):
            if weight == 0 or neighbour in closed_set:
                continue

            tentative_g = cost_so_far + weight
            if tentative_g < g_scores.get(neighbour, float("inf")):
                g_scores[neighbour] = tentative_g
                heuristic = heuristics[neighbour][target_index]
                heapq.heappush(
                    frontier,
                    (
                        tentative_g + heuristic,
                        tentative_g,
                        neighbour,
                        path + [neighbour],
                    ),
                )

    print("A*: No route found.")
    return None, float("inf")
