import json
from pathlib import Path

import a_star
import BFS_DFS
import UCS


def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['graph'], data['heuristics']


def main():
    data_file = Path(__file__).parent / 'input.json'
    graph, heuristics = load_data(data_file)

    for _ in range(5):
        start, target = BFS_DFS.generator(graph)
        print(f"Start : {start}")
        print(f"Target : {target}")

        BFS_DFS.run_dfs_bfs(graph, start, target)
        UCS.run_ucs(graph, start, target)

        a_star.run_a_star(graph, heuristics, start, target)

        print('-' * 40)


if __name__ == '__main__':
    main()
