import collections
import random


def generator(cities):
    return random.sample(cities, 2)


def dfs(graph, cities, start, target, visited=None, path=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []

    visited.add(start)
    path.append(start)

    if start == target:
        return [cities[city_index] for city_index in path.copy()]

    for next_city, cost in enumerate(graph[start]):
        if cost != 0 and next_city not in visited:
            result = dfs(graph, cities, next_city, target, visited, path)
            if result is not None:
                return result

    path.pop()
    return None


def bfs(graph, cities, root, target):
    visited = set()
    root_index = cities.index(root)
    target_index = cities.index(target)
    queue = collections.deque([root_index])
    parent = {root_index: None}
    visited.add(root_index)

    while queue:
        vertex = queue.popleft()
        if vertex == target_index:
            path = []
            while vertex is not None:
                path.append(vertex)
                vertex = parent[vertex]
            path.reverse()
            return [cities[city_index] for city_index in path]

        for neighbour, cost in enumerate(graph[vertex]):
            if cost != 0 and neighbour not in visited:
                visited.add(neighbour)
                parent[neighbour] = vertex
                queue.append(neighbour)

    return None


def distance(graph, cities, path):
    total = 0
    for source, destination in zip(path, path[1:]):
        total += graph[cities.index(source)][cities.index(destination)]
    return total


def run_dfs_bfs(graph, cities, start, target):
    dfs_path = dfs(graph, cities, cities.index(start), cities.index(target))
    bfs_path = bfs(graph, cities, start, target)

    if dfs_path is None:
        print("DFS: No path found")
    else:
        print("DFS path:", " -> ".join(dfs_path))
        print("DFS distance:", distance(graph, cities, dfs_path), "miles")

    if bfs_path is None:
        print("BFS: No path found")
    else:
        print("BFS path:", " -> ".join(bfs_path))
        print("BFS distance:", distance(graph, cities, bfs_path), "miles")


def run_bfs_dfs(graph, cities, start, target):
    run_dfs_bfs(graph, cities, start, target)
