import collections
import csv
import heapq
import json
import random

"""
This program implements various graph search algorithms (DFS, BFS, UCS, A*) to find paths
between cities in a graph. We are comparing the difference between uninformed and informed search algorithms. 
The graph is represented as an adjacency matrix, and the edge weights and heuristics are loaded from CSV files. 
The program randomly selects pairs of cities and runs the search algorithms to find paths and distances between them.
"""
"""
Authors: Alek R.
         Jonathan G.
         Josh B
         Justin B
         Brennen C
         Feranmi M

"""
# list of cities in the graph
cities = [
    "Phoenix", "Los Angeles", "Denver", "Boise", "Wichita",
    "Bozeman", "Omaha", "Las Vegas", "Albuquerque", "Fargo",
    "Oklahoma City", "Portland", "Sioux Falls", "Dallas",
    "Salt Lake City", "Seattle", "Jackson",
]


def load_data():
    # function to load city names, edge weights, and heuristics from CSV files and store them in appropriate data structures
    # author Alek R.
    graph = [[0 for _ in cities] for _ in cities]
    # load edge weights from CSV file

    try:
        #checking for file not found error, if file is not found, return None for all three variables
        with open("CS362_Project1_Data(edge_weights).csv", encoding="utf-8") as file:
            # open the CSV file and read its contents

            reader = csv.reader(file)
            header = [city.strip() for city in next(reader)[1:]]

            for row in reader:
                source = row[0].strip()
                # source is first column of each row, which is the city name
                if not source:
                    # skip rows with empty source city names, shouldnt happen with provided data
                    continue
                source_index = cities.index(source)

                for column in range(1, len(row)):
                    # Step through the edge-weight columns after the city-name column.
                    value = row[column].strip()
                    if not value:
                        # skip empty values, which indicate no adjacency between cities
                        continue

                    destination_index = cities.index(header[column - 1])
                    # get index of destination city from top row of CSV file
                    cost = float(value)
                    graph[source_index][destination_index] = cost
                    graph[destination_index][source_index] = cost

    except FileNotFoundError:
        print("Error: Edge weights CSV file not found.")
        return None, None, None

    heuristics = [[0 for _ in cities] for _ in cities]

    try:
        #checking for file not found error, if file is not found, return None for all three variables
        with open("CS362_Project1_Data(heuristics).csv", encoding="utf-8") as file:
            # open the CSV file and read its contents

            reader = csv.reader(file)
            header = [city.strip() for city in next(reader)[1:]]

            for row in reader:
                source = row[0].strip()
                # source is first column of each row, which is the city name
                if not source:
                    # skip rows with empty source city names, shouldnt happen with provided data
                    continue
                source_index = cities.index(source)

                for column in range(1, len(row)):
                    # Step through the heuristic columns after the city-name column.
                    value = row[column].strip()
                    if not value:
                        # skip empty values, for heuristics empty values only occur when the source and destination are the same
                        continue

                    destination_index = cities.index(header[column - 1])
                    # get index of destination city from top row of CSV file
                    heuristic = float(value)
                    heuristics[source_index][destination_index] = heuristic
                    heuristics[destination_index][source_index] = heuristic

    except FileNotFoundError:
        print("Error: Heuristics CSV file not found.")
        return None, None, None

    try:
        with open("input.json", "w", encoding="utf-8") as file:
            # don't need to read from input.json anymore, just write the data to it for future use
            json.dump(
                {"cities": cities, "graph": graph, "heuristics": heuristics},
                file,
                indent=4,
            )
    except IOError:
        print("Error: Could not write to input.json.")
        return None, None, None

    return cities, graph, heuristics


def generator():
    # generate start and end cities for testing algorithms
    return random.sample(cities, 2)


def dfs(graph, start, target, visited=None, path=None):
    # DFS implementation to find a path from start to target in the graph
    # Uses recursive call stack as the stack, boolean list of visited nodes, and a list to store the current path
    # author: Jonathan G.

    if visited is None:
        visited = [False] * len(graph)
    if path is None:
        path = []

    visited[start] = True
    path.append(start)

    if start == target:
        # base case: if the current node is the target, return the path as a list of city names
        return [cities[city_index] for city_index in path.copy()]

    for next_city in range(len(graph[start])):
        cost = graph[start][next_city]
        # step through the matrix row of the current node, checking for unvisited neighbors
        if cost != 0 and not visited[next_city]:
            # if cost is zero, there is no edge between the two cities, so skip it
            result = dfs(graph, next_city, target, visited, path)
            if result is not None:
                # if a path is found, return it
                return result

    path.pop()
    return None


def bfs(graph, root_index, target_index):
# BFS implementation to find a path from root to target in the graph
# Uses a queue to explore nodes level by level, a boolean list of visited nodes, 
# and a dictionary to store parent nodes for path reconstruction.
# author: Jonathan G.

    visited = [False] * len(graph)
    queue = collections.deque([root_index])
    parent = {root_index: None}
    visited[root_index] = True

    while queue:
        vertex = queue.popleft()
        if vertex == target_index:
            # when target found, reconstruct the path from the target back to the root using the parent dictionary
            path = []
            while vertex is not None:
                path.append(vertex)
                vertex = parent[vertex]
            path.reverse()
            # return the path as a list of city names
            return [cities[city_index] for city_index in path]

        for neighbour in range(len(graph[vertex])):
            cost = graph[vertex][neighbour]
            # enqueue unvisited valid neighbors of the current vertex
            if cost != 0 and not visited[neighbour]:
                visited[neighbour] = True
                parent[neighbour] = vertex
                queue.append(neighbour)

    return None


def distance(graph, path):
    # used by run_dfs_bfs to calculate the total distance of a path found by DFS or BFS
    # author: Jonathan G.

    total = 0
    for i in range(len(path) - 1):
        source = path[i]
        destination = path[i + 1]
        total += graph[cities.index(source)][cities.index(destination)]
        # graph[source][destination] is the lookup of the edge weight between the two cities in the adjacency matrix
    return total


def run_dfs_bfs(graph, start, target):
    # running and printing the results of DFS and BFS for a given start and target city
    # author: Jonathan G.
    
    dfs_path = dfs(graph, cities.index(start), cities.index(target))
    bfs_path = bfs(graph, cities.index(start), cities.index(target))

    if dfs_path is None:
        print("DFS: No path found")
    else:
        print("DFS path:", " -> ".join(dfs_path))
        print("DFS distance:", distance(graph, dfs_path), "miles")

    if bfs_path is None:
        print("BFS: No path found")
    else:
        print("BFS path:", " -> ".join(bfs_path))
        print("BFS distance:", distance(graph, bfs_path), "miles")


def uniform_cost_search(graph, start_index, goal_index):
    # UCS implementation to find the least-cost path from start to goal in the graph
    # Uses a priority queue to explore nodes based on cumulative cost, a dictionary to track the cost so far for each node, 
    # and a dictionary to reconstruct the path once the goal is reached.
    # Priority queue entries contain (total_cost, current_city).
    # author: Brennen C.
    frontier = [(0, start_index)]

    # Keep the lowest known cost to each city.
    cost_so_far = {start_index: 0}

    # Track each city's predecessor so the route can be reconstructed.
    came_from = {start_index: None}

    while frontier:
        current_cost, current_city = heapq.heappop(frontier)

        # Ignore an outdated queue entry if a cheaper route was found later.
        if current_cost > cost_so_far[current_city]:
            continue

        # Stop once the destination is reached at its lowest known cost.
        if current_city == goal_index:
            break

        # Check each city connected to the current city in the adjacency matrix.
        for neighbour in range(len(graph[current_city])):
            edge_cost = graph[current_city][neighbour]
            if edge_cost == 0:
                continue

            new_cost = current_cost + edge_cost

            # Record the route when it is the first or a cheaper way to the neighbor.
            if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                cost_so_far[neighbour] = new_cost
                came_from[neighbour] = current_city
                heapq.heappush(frontier, (new_cost, neighbour))

    # No route exists if the destination was never reached.
    if goal_index not in cost_so_far:
        return None, None

    # Reconstruct the route by following predecessors from goal to start.
    path = []
    current = goal_index
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()

    return [cities[city_index] for city_index in path], cost_so_far[goal_index]


def run_ucs(graph, start, goal):
    # runs and prints the results of UCS for a given start and goal city
    # author: Brennen C.
    start_index = cities.index(start)
    goal_index = cities.index(goal)
    path, total_distance = uniform_cost_search(graph, start_index, goal_index)
    if path is None:
        print("No route found.")
    else:
        print("UCS path:", " -> ".join(path))
        print("Total distance:", total_distance, "miles")


def run_a_star(graph, heuristics, start_city, target_city):
    # runs and prints the results of A* search for a given start and target city
    # A* search uses a priority queue to explore nodes based on the sum of the cost so far and the heuristic estimate to the target.
    # author: Josh B.

    if start_city == target_city:
        # if the start and target cities are the same, return the city and a distance of 0
        print("A* path:", start_city)
        print("A* total distance:", 0, "miles")
        return [start_city], 0

    start_index = cities.index(start_city)
    target_index = cities.index(target_city)

    priority_queue = [
        (heuristics[start_index][target_index], 0, start_index, [start_index])
    ]
    g_scores = {start_index: 0}
    closed_set = set()

    while priority_queue:
        _, cost_so_far, current, path = heapq.heappop(priority_queue)

        if current == target_index:
            city_path = [cities[city_index] for city_index in path]
            print("A* path:", " -> ".join(city_path))
            print("A* total distance:", cost_so_far, "miles")
            return city_path, cost_so_far

        if current in closed_set:
            continue
        closed_set.add(current)

        for neighbour in range(len(graph[current])):
            edge_cost = graph[current][neighbour]
            if edge_cost == 0 or neighbour in closed_set:
                continue

            new_cost = cost_so_far + edge_cost
            if new_cost < g_scores.get(neighbour, float("inf")):
                g_scores[neighbour] = new_cost
                heuristic = heuristics[neighbour][target_index]
                heapq.heappush(
                    priority_queue,
                    (
                        new_cost + heuristic,
                        new_cost,
                        neighbour,
                        path + [neighbour],
                    ),
                )

    print("A*: No route found.")
    return None, float("inf")


def main():
    city_names, graph, heuristics = load_data()

    for _ in range(5):
        start, target = random.sample(city_names, 2)
        print(f"Start : {start}")
        print(f"Target : {target}")
        # passing start and target as names to the search functions, which will convert them to indices internally

        run_dfs_bfs(graph, start, target)
        run_ucs(graph, start, target)
        run_a_star(graph, heuristics, start, target)
        print("-" * 40)


if __name__ == "__main__":
    main()
