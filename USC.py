import heapq

def uniform_cost_search(graph, start, goal):
    #priority queue: (total_cost, current_city)
    frontier = [(0, start)]

    # Lowest known cost to each city
    cost_so_far = {start: 0}

    #Used to reconstruct the route
    came_from = {start: None}

    while frontier:
        current_cost, current_city = heapq.heappop(frontier)

        #Ignore an outdated entry in the priority queue
        if current_cost > cost_so_far[current_city]:
            continue

        # We reached the destination
        if current_city == goal:
            break

        #check neighboring cities
        for neighbor, distance in graph.get(current_city, []):
            new_cost = current_cost + distance

            #found cheaper
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current_city

                heapq.heappush(frontier, (new_cost, neighbor))

    #no route exists
    if goal not in cost_so_far:
        return None, None

    #reconstruct the route
    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()

    return path, cost_so_far[goal]

graph = {}

start = "Chicago"
goal = "South Bend"

path, distance = uniform_cost_search(graph, start, goal)

if path is None:
    print("No route found.")
else:
    print("Route:", " -> ".join(path))
    print("Total distance:", distance, "miles")



