import csv
import time #use for time tracking later
"""
PROJECT DESCRIPTION
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
        for destination in moves:
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
                break

        return best_score, best_move

    def play(self, police, thief, depth, use_pruning=False, order_moves=False):
        self.nodes_expanded = 0
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


def main():
    graph = Graph(CITIES)
    graph.load_edges("CS362_Project_Data(edge_weights).csv")
    graph.load_heuristics("CS362_Project_Data(heuristics).csv")
    run_part_a(graph)
if __name__ == "__main__":
    main()