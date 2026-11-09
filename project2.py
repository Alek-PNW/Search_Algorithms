import csv
import math
import random
import time 
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
"""
This program uses a highway map of western U.S. cities to demonstrate constraint-satisfaction and adversarial search.
It colors the map by comparing backtracking strategies with heuristics, forward checking, and AC-3, then simulates a police-and-thief chase using minimax, alpha-beta pruning, and move ordering.
The graph's highway connections and straight-line distances are loaded from CSV files.
A Tkinter interface lets users select algorithm settings, compare results, and step through saved chase replays.
"""
"""
Authors: Alek R.
         Jonathan G.
         Josh B
         Justin B
         Brennen C
         Feranmi M

"""

# list of cities in the graph, the indices here
# correlate to the row/column in the matrices and indices in lists
CITIES = [
    "Phoenix", "Los Angeles", "Denver", "Boise", "Wichita",
    "Bozeman", "Omaha", "Las Vegas", "Albuquerque", "Fargo",
    "Oklahoma City", "Portland", "Sioux Falls", "Dallas",
    "Salt Lake City", "Seattle", "Jackson",
]
COLORS = ["red", "green", "blue", "yellow"]

def read_csv_matrix(filename):
    #Read a CSV laid out as a matrix (city names across the top and downthe left side).
    #Returns a list of (source, destination, value) tuples for every non-empty cell.
    # in project one, this section was repeated twice for g(n) and h(n) so now its a function
    cells = []
    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file)
        header = [city.strip() for city in next(reader)[1:]] #first row

        for row in reader:
            source = row[0].strip()
            #source is first column of each row (city name)
            if not source: #empty cell
                continue
            for column in range(1, len(row)):
                # step through columns
                value = row[column].strip()
                if value:
                    cells.append((source, header[column - 1], float(value)))
    return cells

class Graph:
#graph data structure used by both the csp and chase game
    def __init__(self, cities):
        #graph constructor, initializes matrices to empty
        self.cities = cities
        self.n = len(cities)
        # g[i][j] = driving distance, or None if no direct highway
        self.g = [[None] * self.n for _ in range(self.n)]
        # h[i][j] = straight-line distance between any two cities (positive)
        self.h = [[0] * self.n for _ in range(self.n)]

    def add_edge(self, u, v, weight):
        self.g[u][v] = weight
        self.g[v][u] = weight

    def set_heuristic(self, u, v, value):
        self.h[u][v] = value
        self.h[v][u] = value

    def load_edges(self, filename):
        # loads data from csv file with helper function to get a (source, dest, edge_weight) tuple
        for source, dest, value in read_csv_matrix(filename):
            # read indices of cities in matrix
            s = self.cities.index(source)
            d = self.cities.index(dest)

            if s != d and self.g[s][d] is None:
                #skip diagonal and edges already added from mirrored cell across diagonal
                self.add_edge(s, d, value)

    def load_heuristics(self, filename):
        # loads data from csv file with helper function to get a (source, dest, heuristic) tuple
        for source, dest, value in read_csv_matrix(filename):
            s = self.cities.index(source)
            d = self.cities.index(dest)
            self.set_heuristic(s, d, value)

    def neighbors(self, v):
        #return all neighbors of city v.
        return [j for j in range(self.n) if self.g[v][j] is not None]

class ColoringCSP:

    def __init__(self, graph, num_colors=3):
        self.graph = graph
        # set what map to build off

        self.num_colors = num_colors
        self.assignment = [None] * graph.n
        # assignment[v] = color of city v (0, 1, 2, ...), or None if not
        # colored yet. A color's number matches its position in the domain.

        self.domains = [list(range(num_colors)) for _ in range(graph.n)]
        # domains[v] = list of colors city v could still use. Used by forward
        # checking and AC-3, which remove colors from these lists.

        self.assignments_made = 0
        self.backtracks = 0

    def is_consistent(self, v, color):
        #return true if no neighbors of city v have assigned color
        for neighbor in self.graph.neighbors(v):
            if self.assignment[neighbor] == color:
                return False
        return True

    def legal_values(self, v):
        #check possible allowed values for this domain
        return [c for c in self.domains[v] if self.is_consistent(v, c)]

    def unassigned_cities(self):
        #return every vertex with no assignment(color)
        return [v for v in range(self.graph.n) if self.assignment[v] is None]

    def is_valid_coloring(self):
        #final check for validity
        for v in range(self.graph.n):
            if self.assignment[v] is None: #checking for forgotten nodes
                return False
            for neighbor in self.graph.neighbors(v):
                #for every neigbor of every node, check if it has the same color as node v
                if self.assignment[neighbor] == self.assignment[v]:
                    return False
        return True

    def select_variable(self, use_heuristics):
        """Pick the next city to color

        use_heuristics False -> select next uncolored city
        use_heuristics True -> use MRV and LCV in finding next city
        """

        free = self.unassigned_cities()
        if not use_heuristics:
            return free[0]

        def key(v):
            remaining = len(self.legal_values(v))
            # number of remaining colors, used in MRV
            free_neighbors = 0
            for neighbor in self.graph.neighbors(v):
                #count how many neighbors have no value
                if self.assignment[neighbor] is None:
                    free_neighbors += 1
            return (remaining, -free_neighbors)

        #return the minimum value between unassigned cities,
        #prioritizing cities with the least options left,
        #and using number of free naighbors for tie-breakers
        return min(free, key=key)

    def order_values(self, v, use_heuristics):
        """search possible colors of city v and order if heuristic

        use_heuristics False -> return values in order defined in COLORS
        use_heursitics True -> return values in order of removing least options from neighbors
        """
        values = self.legal_values(v)
        if not use_heuristics:
            return values

        def ruled_out(color):
            count = 0
            for neighbor in self.graph.neighbors(v):
                if self.assignment[neighbor] is None and color in self.legal_values(neighbor):
                    #if this color would eliminate an option from a neighbor
                    count += 1
            return count

        #return all values sorted by least number of constraints on neighbors
        return sorted(values, key=ruled_out)

    def forward_check(self, v, color):
        """remove color from domains of neighbors,
           returning False when a neighbor is left with no colors"""
        for neighbor in self.graph.neighbors(v):
            if self.assignment[neighbor] is None and color in self.domains[neighbor]:
                #if color is unnasigned for neighbor and still a possibility,
                #remove color from domain and check if it breaks search
                self.domains[neighbor].remove(color)
                if len(self.domains[neighbor]) == 0:
                    return False
        return True

    def revise(self, xi, xj):
        """Remove colors from xi's domain that have no different color
        available in xj's domain. Returns True if anything was removed.
        xi -> domain that can shrink
        xj -> domain compared to xi"""
        removed = False
        for a in list(self.domains[xi]):
            supported = False # changes to true once there is a differing value
            for b in self.domains[xj]:
                if a != b:
                    supported = True
                    break
            if not supported:
                self.domains[xi].remove(a)
                removed = True
        return removed

    def all_arcs(self):
        """Every (city, neighbor) pair, in both directions."""
        arcs = []
        for u in range(self.graph.n):
            for v in self.graph.neighbors(u):
                arcs.append((u, v))
        return arcs

    def ac3(self, arcs):
        """AC-3. arcs is a list of (xi, xj) pairs to start from.
        Returns False if some domain becomes empty(no colors left)."""
        queue = list(arcs)
        while queue:
            xi, xj = queue.pop(0)
            if self.revise(xi, xj): #if color removed
                if len(self.domains[xi]) == 0: #check for final
                    return False
                for xk in self.graph.neighbors(xi): #append all neighbors of pruned node
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def backtrack(self, use_heuristics, inference):
        """Recursive backtracking. inference is None, "fc", or "ac3"."""
        free = self.unassigned_cities()
        if not free:
            return True

        city = self.select_variable(use_heuristics)
        for color in self.order_values(city, use_heuristics):
            saved_domains = [list(d) for d in self.domains]  # to undo pruning
            self.assignment[city] = color
            self.assignments_made += 1

            valid = True
            if inference == "fc":
                valid = self.forward_check(city, color)
            elif inference == "ac3":
                self.domains[city] = [color]
                arcs = [(nb, city) for nb in self.graph.neighbors(city)
                        if self.assignment[nb] is None]
                valid = self.ac3(arcs)

            if valid and self.backtrack(use_heuristics, inference):
                return True

            # this color failed: undo it
            self.assignment[city] = None
            self.domains = saved_domains
            self.backtracks += 1

        return False
    def solve(self, use_heuristics=False, inference=None):
        #reset assignments and stats before starting
        self.assignment = [None] * self.graph.n
        self.domains = [list(range(self.num_colors)) for _ in range(self.graph.n)]
        self.assignments_made = 0
        self.backtracks = 0

        #track how long the search takes
        start = time.perf_counter()
        valid = True
        if inference == "ac3":
            valid = self.ac3(self.all_arcs())
        success = valid and self.backtrack(use_heuristics, inference)
        runtime = time.perf_counter() - start

        return success, runtime


class ChaseGame:
    def __init__(self, graph, max_moves=10):
        self.graph = graph
        self.max_moves = max_moves
        self.nodes_expanded = 0
        self.branches_pruned = 0

        # A win or loss must matter more than any straight-line distance.
        self.win_score = 1 + max(max(row) for row in graph.h)

    def winner(self, state):
        _, _, turns, caught = state
        if caught:
            return "Police"
        if turns >= self.max_moves:
            return "Thief"
        return None

    def move(self, state, destination):
        police, thief, turns, _ = state

        # Police starts, so even turn counts mean Police moves next.
        if turns % 2 == 0:
            # Capture happens when Police moves into the Thief's city.
            caught = destination != police and destination == thief
            return destination, thief, turns + 1, caught

        return police, destination, turns + 1, False

    def search(self, state, depth, use_pruning=False, order_moves=False,
               alpha=float("-inf"), beta=float("inf"), is_root=True):
        """Return (score, best destination) for the player whose turn it is."""
        police, thief, turns, _ = state

        # Check the real game result before estimating a score.
        winner = self.winner(state)
        if winner == "Police":
            return self.win_score, None
        if winner == "Thief":
            return -self.win_score, None
        if depth == 0:
            # Closer is better for Police: -5 is higher than -20.
            return -self.graph.h[police][thief], None

        # Count a position only when we explore moves from it.
        self.nodes_expanded += 1
        police_turn = turns % 2 == 0
        if police_turn:
            current, opponent = police, thief
            best_score = float("-inf")
        else:
            current, opponent = thief, police
            best_score = float("inf")

        # A player can drive to any neighbor or stay in the current city.
        moves = self.graph.neighbors(current) + [current]

        # Try closer cities first deeper in the search. Keep the same order
        # for the actual decision so all versions break ties the same way.
        if order_moves and not is_root:
            moves.sort(key=lambda city: self.graph.h[city][opponent])

        best_move = None
        for move_index, destination in enumerate(moves):
            # Imagine the move, then let the other player respond.
            next_state = self.move(state, destination)
            score, _ = self.search(
                next_state, depth - 1, use_pruning, order_moves,
                alpha, beta, is_root=False,
            )

            if police_turn:
                if score > best_score:
                    best_score = score
                    best_move = destination
                if use_pruning:
                    alpha = max(alpha, best_score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = destination
                if use_pruning:
                    beta = min(beta, best_score)

            # Alpha is what MAX can already get. Beta is what MIN can
            # already hold the score to. If they meet or cross, the rest
            # of this branch cannot improve the earlier player's choice.
            if use_pruning and alpha >= beta:
                self.branches_pruned += len(moves) - move_index - 1
                break

        return best_score, best_move

    def play(self, police, thief, depth, use_pruning=False, order_moves=False):
        self.nodes_expanded = 0
        self.branches_pruned = 0
        # State: (police city, thief city, turns taken, whether caught).
        state = (police, thief, 0, False)
        history = [state]
        start = time.perf_counter()

        # Search imagines moves. This loop actually plays one move at a time.
        while self.winner(state) is None:
            _, destination = self.search(state, depth, use_pruning, order_moves)
            state = self.move(state, destination)
            history.append(state)

        seconds = time.perf_counter() - start
        return history, self.winner(state), self.nodes_expanded, seconds


def run_part_b(graph):
    game = ChaseGame(graph)
    versions = [
        ("Minimax", False, False),
        ("Alpha-beta", True, False),
        ("Alpha-beta + ordering", True, True),
    ]

    # Police and Thief start in different cities. A fixed seed gives all
    # runs the same five random pairs, so the report is reproducible.
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
                print(f"  {name}: {winner} wins, {nodes} nodes, {seconds:.6f} s")

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

    # Keep the starting positions and every move for the graphics later.
    return chase_histories


def find_min_colors(graph):
    # Start with one color and increase if needed.
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

            #for i, city in enumerate(graph.cities):
            #   color = COLORS[solver.assignment[i]]
            #   print(f"{city}: {color}")

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

    # The assignment uses 3 colors (4 if 3 is not enough)
    num_colors = max(3, min_colors)
    print("Comparing versions with", num_colors, "colors\n")

    versions = [
        ("Plain backtracking",         False, None),
        ("With heuristics",            True,  None),
        ("Heuristics + forward check", True,  "fc"),
        ("Heuristics + AC-3",          True,  "ac3"),
    ]

    print(f"{'Version':<28}{'Assignments':>12}{'Backtracks':>12}{'Time (s)':>11}  Valid")
    last_csp = None

    for name, heuristics, inference in versions:
        csp = ColoringCSP(graph, num_colors)  # fresh CSP so counters start at 0
        solved, seconds = csp.solve(heuristics, inference) #is it solved, how long did it take
        valid = solved and csp.is_valid_coloring() #check solution
        print(f"{name:<28}{csp.assignments_made:>12}{csp.backtracks:>12}"
              f"{seconds:>11.6f}  {valid}")
        last_csp = csp

    print("\nColoring found (heuristics + AC-3):")
    if last_csp is None or not last_csp.is_valid_coloring():
        raise RuntimeError("Heuristics + AC-3 did not produce a valid coloring")
    for v in range(graph.n):
        print(f"  {graph.cities[v]:<16}{COLORS[last_csp.assignment[v]]}")
    print()


class MeasuredCSP(ColoringCSP):
    """Use the team's algorithms and count the colors they remove."""

    def __init__(self, graph, num_colors):
        super().__init__(graph, num_colors)
        self.values_pruned = 0

    def forward_check(self, city, color):
        before = sum(len(domain) for domain in self.domains)
        valid = super().forward_check(city, color)
        after = sum(len(domain) for domain in self.domains)
        self.values_pruned += before - after
        return valid

    def revise(self, source, neighbor):
        before = len(self.domains[source])
        changed = super().revise(source, neighbor)
        self.values_pruned += before - len(self.domains[source])
        return changed

    def solve(self, use_heuristics=False, inference=None):
        self.values_pruned = 0
        return super().solve(use_heuristics, inference)


def load_graph():
    folder = Path(__file__).resolve().parent
    graph = Graph(CITIES)
    graph.load_edges(folder / "CS362_Project_Data(edge_weights).csv")
    graph.load_heuristics(folder / "CS362_Project_Data(heuristics).csv")
    return graph


def coloring_results(graph, colors, heuristics, inference, compare=False):
    versions = [("Selected settings", heuristics, inference)]
    if compare:
        versions = [
            ("Plain backtracking", False, None),
            ("Heuristics", True, None),
            ("Heuristics + FC", True, "fc"),
            ("Heuristics + AC-3", True, "ac3"),
        ]
    rows = []
    coloring = None
    for name, use_heuristics, mode in versions:
        solver = MeasuredCSP(graph, colors)
        solved, seconds = solver.solve(use_heuristics, mode)
        if solved and not solver.is_valid_coloring():
            raise RuntimeError("Invalid coloring returned.")
        rows.append((name, colors, "Yes" if solved else "No",
                     solver.assignments_made, solver.backtracks,
                     solver.values_pruned, f"{seconds:.6f}"))
        if solved:
            coloring = solver.assignment.copy()
    return rows, coloring


def chase_results(graph, depth, method, ordering, compare=False):
    pairs = [(police, thief) for police in range(graph.n)
             for thief in range(graph.n) if police != thief]
    starts = random.Random(362).sample(pairs, 5)
    versions = [(method, method == "Alpha-beta", ordering)]
    depths = [depth]
    if compare:
        versions = [("Minimax", False, False),
                    ("Alpha-beta", True, False),
                    ("Alpha-beta + ordering", True, True)]
        depths = [2, 4, 6]
    rows, replays = [], []
    for chase, (police, thief) in enumerate(starts, 1):
        for limit in depths:
            results = []
            base_nodes = None
            for name, pruning, ordered in versions:
                game = ChaseGame(graph)
                history, winner, nodes, seconds = game.play(
                    police, thief, limit, pruning, ordered)
                savings = ""
                if compare and name == "Alpha-beta":
                    base_nodes = nodes
                if compare and name == "Alpha-beta + ordering":
                    savings = base_nodes - nodes
                rows.append((chase, limit, name, "Yes" if ordered else "No",
                             winner, nodes, game.branches_pruned,
                             f"{seconds:.6f}", savings))
                results.append(history)
                label = f"{chase} | depth {limit} | {name}"
                replays.append((label, history, winner))
            if compare:
                minimax_path = results[0]
                for path in results[1:]:
                    if path != minimax_path:
                        raise RuntimeError(
                            "Minimax and alpha-beta chose different moves.")
    return rows, replays


class Graphics:
    def __init__(self, root):
        self.graph = load_graph()
        self.colors = None
        self.replays = []
        self.turn = 0
        root.title("Highway map — Settings and Statistics")
        root.geometry("1200x850")

        settings = ttk.LabelFrame(root, text="Settings", padding=8)
        settings.pack(fill="x")
        self.color_count = tk.StringVar(value="3")
        self.inference = tk.StringVar(value="AC-3")
        self.depth = tk.StringVar(value="4")
        self.method = tk.StringVar(value="Alpha-beta")
        self.heuristics = tk.BooleanVar(value=True)
        self.ordering = tk.BooleanVar(value=True)
        choices = [
            ("Colors", self.color_count, (1, 2, 3, 4)),
            ("Inference", self.inference,
             ("None", "Forward checking", "AC-3")),
            ("Depth", self.depth, (2, 4, 6)),
            ("Method", self.method, ("Minimax", "Alpha-beta")),
        ]
        for column, (label, variable, values) in enumerate(choices):
            ttk.Label(settings, text=label).grid(row=0, column=column)
            ttk.Combobox(settings, textvariable=variable, values=values,
                         state="readonly", width=18).grid(
                             row=1, column=column, padx=6)
        ttk.Checkbutton(settings, text="Use heuristics",
                        variable=self.heuristics).grid(row=2, column=0)
        ttk.Checkbutton(settings, text="Move ordering",
                        variable=self.ordering).grid(row=2, column=1)
        buttons = [
            ("Run coloring", self.run_coloring),
            ("Compare coloring", self.compare_coloring),
            ("Run 5 chases", self.run_chases),
            ("Compare all depths", self.compare_chases),
        ]
        for column, (label, action) in enumerate(buttons):
            ttk.Button(settings, text=label, command=action).grid(
                row=3, column=column, pady=6)

        controls = ttk.Frame(root)
        controls.pack(fill="x")
        self.picker = ttk.Combobox(controls, state="readonly", width=45)
        self.picker.pack(side="left")
        self.picker.bind("<<ComboboxSelected>>", self.select_chase)
        ttk.Button(controls, text="Previous",
                   command=self.previous).pack(side="left")
        ttk.Button(controls, text="Next", command=self.next).pack(side="left")
        self.canvas = tk.Canvas(root, background="white", height=420)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.resize)
        self.status = tk.StringVar(
            value="Blue square = Police. Orange triangle = Thief.")
        ttk.Label(root, textvariable=self.status).pack()
        ttk.Label(root, text="Statistics — scroll below to see all results").pack()
        self.stats = tk.Text(root, height=10, wrap="none",
                             font=("Courier", 10))
        self.stats.pack(fill="x")

    def run_coloring(self):
        self.run("coloring", False)

    def compare_coloring(self):
        self.run("coloring", True)

    def run_chases(self):
        self.run("chase", False)

    def compare_chases(self):
        self.run("chase", True)

    def run(self, kind, compare):
        try:
            if kind == "coloring":
                mode = None
                if self.inference.get() == "Forward checking":
                    mode = "fc"
                elif self.inference.get() == "AC-3":
                    mode = "ac3"
                rows, self.colors = coloring_results(
                    self.graph, int(self.color_count.get()),
                    self.heuristics.get(), mode, compare)
                headings = (
                    "Version | Colors | Solved | Assignments | Backtracks | "
                    "Colors pruned | Seconds")
                note = (
                    "Colors pruned counts FC / AC-3 removals, including "
                    "failed attempts.")
                self.status.set(
                    "Coloring finished." if self.colors is not None
                    else "No coloring found.")
            else:
                rows, self.replays = chase_results(
                    self.graph, int(self.depth.get()), self.method.get(),
                    self.ordering.get(), compare)
                labels = [label for label, _, _ in self.replays]
                self.picker["values"] = labels
                self.picker.current(0)
                self.turn = 0
                headings = (
                    "Chase | Depth | Method | Ordering | Winner | Nodes | "
                    "Branches pruned | Seconds | Ordering saves")
                note = (
                    "Branches pruned = immediate moves skipped. Ordering "
                    "saves = unordered minus ordered nodes.")
            self.stats.delete("1.0", "end")
            self.stats.insert("end", headings + "\n" + note + "\n\n")
            for row in rows:
                self.stats.insert("end", " | ".join(
                    str(value) for value in row) + "\n")
            self.draw()
        except Exception as error:
            messagebox.showerror("Could not run", str(error))

    def select_chase(self, event):
        self.turn = 0
        self.draw()

    def previous(self):
        if self.turn > 0:
            self.turn -= 1
            self.draw()

    def next(self):
        if self.replays:
            history = self.replays[self.picker.current()][1]
            if self.turn < len(history) - 1:
                self.turn += 1
                self.draw()

    def resize(self, event):
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 300)
        positions = []
        for city in range(self.graph.n):
            angle = 2 * math.pi * city / self.graph.n
            x = width / 2 + (width / 2 - 120) * math.cos(angle)
            y = height / 2 + (height / 2 - 55) * math.sin(angle)
            positions.append((x, y))
        for city in range(self.graph.n):
            for neighbor in self.graph.neighbors(city):
                if city < neighbor:
                    x1, y1 = positions[city]
                    x2, y2 = positions[neighbor]
                    self.canvas.create_line(
                        x1, y1, x2, y2, fill="#bbc3cd")
        if self.replays:
            _, history, winner = self.replays[self.picker.current()]
            for player, color in ((0, "blue"), (1, "#c45100")):
                for step in range(1, self.turn + 1):
                    x1, y1 = positions[history[step - 1][player]]
                    x2, y2 = positions[history[step][player]]
                    self.canvas.create_line(
                        x1, y1, x2, y2, fill=color, width=3, arrow="last")
        for city, (x, y) in enumerate(positions):
            color = "#ddd"
            if self.colors is not None:
                color = COLORS[self.colors[city]]
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=color)
            self.canvas.create_text(x, y-23, text=self.graph.cities[city])
        if self.replays:
            police, thief, _, _ = history[self.turn]
            x, y = positions[police]
            self.canvas.create_rectangle(
                x-22, y+10, x-6, y+26, fill="blue")
            x, y = positions[thief]
            self.canvas.create_polygon(
                x+15, y+8, x+4, y+28, x+26, y+28, fill="#c45100")
            result = "In progress"
            if self.turn == len(history) - 1:
                result = winner + " wins"
            self.status.set(
                f"Turn {self.turn}/{len(history)-1} | {result} | "
                "Blue square = Police. Orange triangle = Thief.")


def main():
    graph = Graph(CITIES)
    graph.load_edges("CS362_Project_Data(edge_weights).csv")
    graph.load_heuristics("CS362_Project_Data(heuristics).csv")
    run_part_a(graph)
    run_part_b(graph)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        Graphics(root)
        root.mainloop()
    except (OSError, ValueError) as error:
        messagebox.showerror("Could not load CSVs", str(error))
        root.destroy()