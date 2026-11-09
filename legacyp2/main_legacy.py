import random
import tkinter as tk
from tkinter import messagebox

from .csp import ColoringCSP
from .graph import COLORS, load_graph
from .graphics import Graphics
from .policegame import ChaseGame


def find_min_colors(graph):
    for num_colors in range(1, len(COLORS) + 1):
        solver = ColoringCSP(graph, num_colors)
        success, runtime = solver.solve()

        print(f"\nTesting with {num_colors} colors")
        print(f"Solution found: {success}")
        print(f"Assignments made: {solver.assignments_made}")
        print(f"Backtracks: {solver.backtracks}")
        print(f"Runtime: {runtime:.6f} seconds")

        if success:
            if not solver.is_valid_coloring():
                raise ValueError("Invalid coloring found")
            print(f"\nMinimum colors needed: {num_colors}")
            return num_colors, solver.assignment.copy()

    print(f"No solution found with up to {len(COLORS)} colors")
    return None, None


def run_part_a(graph):
    print("=" * 66)
    print("PART A: CONSTRAINT SATISFACTION - COLORING THE HIGHWAY MAP")
    print("=" * 66)

    min_colors, _ = find_min_colors(graph)
    print("Minimum number of colors needed:", min_colors)
    if min_colors is None:
        return

    num_colors = max(3, min_colors)
    print("Comparing versions with", num_colors, "colors\n")
    versions = [
        ("Plain backtracking", False, None),
        ("With heuristics", True, None),
        ("Heuristics + forward check", True, "fc"),
        ("Heuristics + AC-3", True, "ac3"),
    ]

    print(f"{'Version':<28}{'Assignments':>12}{'Backtracks':>12}"
          f"{'Time (s)':>11}  Valid")
    last_csp = None
    for name, heuristics, inference in versions:
        csp = ColoringCSP(graph, num_colors)
        solved, seconds = csp.solve(heuristics, inference)
        valid = solved and csp.is_valid_coloring()
        print(f"{name:<28}{csp.assignments_made:>12}"
              f"{csp.backtracks:>12}{seconds:>11.6f}  {valid}")
        last_csp = csp

    print("\nColoring found (heuristics + AC-3):")
    if last_csp is None or not last_csp.is_valid_coloring():
        raise RuntimeError("Heuristics + AC-3 did not produce a valid coloring")
    for city in range(graph.n):
        print(f"  {graph.cities[city]:<16}{COLORS[last_csp.assignment[city]]}")
    print()


def run_part_b(graph):
    game = ChaseGame(graph)
    versions = [
        ("Minimax", False, False),
        ("Alpha-beta", True, False),
        ("Alpha-beta + ordering", True, True),
    ]
    pairs = [(police, thief) for police in range(graph.n)
             for thief in range(graph.n) if police != thief]
    starting_pairs = random.Random(362).sample(pairs, 5)
    chase_histories = []

    for police, thief in starting_pairs:
        print(f"\nPolice starts in {graph.cities[police]}. "
              f"Thief starts in {graph.cities[thief]}.")
        for depth in (2, 4, 6):
            print(f"Depth {depth}")
            results = []
            for name, pruning, ordering in versions:
                result = game.play(police, thief, depth, pruning, ordering)
                history, winner, nodes, seconds = result
                results.append(result)
                print(f"  {name}: {winner} wins, {nodes} nodes, "
                      f"{seconds:.6f} s")
            minimax, alpha_beta, ordered = results
            minimax_path, _, _, _ = minimax
            alpha_beta_path, _, alpha_beta_nodes, _ = alpha_beta
            ordered_path, _, ordered_nodes, _ = ordered
            if minimax_path != alpha_beta_path or minimax_path != ordered_path:
                raise RuntimeError("Search methods chose different moves.")
            saved = alpha_beta_nodes - ordered_nodes
            print(f"  Nodes saved by move ordering: {saved:+d}")
            if depth == 6:
                chase_histories.append(minimax_path)
    return chase_histories


def run_cli():
    graph = load_graph()
    run_part_a(graph)
    run_part_b(graph)


def main():
    root = tk.Tk()
    try:
        Graphics(root)
        root.mainloop()
    except (OSError, ValueError) as error:
        messagebox.showerror("Could not load CSVs", str(error))
        root.destroy()


if __name__ == "__main__":
    main()
