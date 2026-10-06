import random
import collections


def generator(graph):
    start, target = random.sample(list(graph), 2)
    return start, target


def dfs(graph, start, target, visited=None, path=None):
    if visited is None:
        visited = set()

    if path is None:
        path = []

    visited.add(start)
    path.append(start)

    if start == target:
        return path.copy()

    for next_city in graph[start]:
        if next_city not in visited:
            result = dfs(graph, next_city, target, visited, path)

            if result is not None:
                return result

    path.pop()
    return None


def bfs(graph, root, target):
    visited = set()
    queue = collections.deque([root])
    parent = {root: None}
    visited.add(root)

    while queue:
        vertex = queue.popleft()

        if vertex == target:
            path = []

            while vertex is not None:
                path.append(vertex)
                vertex = parent[vertex]

            path.reverse()
            return path

        for neighbour in graph[vertex]:
            if neighbour not in visited:
                visited.add(neighbour)
                parent[neighbour] = vertex
                queue.append(neighbour)

    return None


def distance(graph, path):
    total = 0

    for i in range(len(path) - 1):
        total += graph[path[i]][path[i + 1]]

    return total


def run_dfs_bfs(graph, start, target):

    dfs_path = dfs(graph, start, target)
    bfs_path = bfs(graph, start, target)

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


def run_bfs_dfs(graph, start, target):
    run_dfs_bfs(graph, start, target)
