import json
from pathlib import Path
import time

import a_star
import BFS_DFS
import UCS


def load_data(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["cities"], data["graph"], data["heuristics"]


def main():
    start_time = time.perf_counter()
    data_file = Path(__file__).parent.parent / "input.json"
    cities, graph, heuristics = load_data(data_file)

    for _ in range(5):
        start, target = BFS_DFS.generator(cities)
        print(f"Start : {start}")
        print(f"Target : {target}")

        BFS_DFS.run_dfs_bfs(graph, cities, start, target)
        UCS.run_ucs(graph, cities, start, target)
        a_star.run_a_star(graph, heuristics, cities, start, target)
        print("-" * 40)
        
    elapsed_time = time.perf_counter() - start_time
    print(f"Total runtime: {elapsed_time:.4f} seconds")


if __name__ == "__main__":
    main()
