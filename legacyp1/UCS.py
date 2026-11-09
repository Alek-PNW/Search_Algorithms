import heapq


def uniform_cost_search(graph, cities, start, goal):
    start_index = cities.index(start)
    goal_index = cities.index(goal)
    frontier = [(0, start_index)]
    cost_so_far = {start_index: 0}
    came_from = {start_index: None}

    while frontier:
        current_cost, current_city = heapq.heappop(frontier)
        if current_cost > cost_so_far[current_city]:
            continue
        if current_city == goal_index:
            break

        for neighbour, distance in enumerate(graph[current_city]):
            if distance == 0:
                continue

            new_cost = current_cost + distance
            if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                cost_so_far[neighbour] = new_cost
                came_from[neighbour] = current_city
                heapq.heappush(frontier, (new_cost, neighbour))

    if goal_index not in cost_so_far:
        return None, None

    path = []
    current = goal_index
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return [cities[city_index] for city_index in path], cost_so_far[goal_index]


def run_ucs(graph, cities, start, goal):
    path, distance = uniform_cost_search(graph, cities, start, goal)
    if path is None:
        print("No route found.")
    else:
        print("UCS path:", " -> ".join(path))
        print("Total distance:", distance, "miles")
