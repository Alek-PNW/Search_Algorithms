import time


class ColoringCSP:
    def __init__(self, graph, num_colors=3):
        self.graph = graph
        self.num_colors = num_colors
        self.assignment = [None] * graph.n
        self.domains = [list(range(num_colors)) for _ in range(graph.n)]
        self.assignments_made = 0
        self.backtracks = 0

    def is_consistent(self, v, color):
        for neighbor in self.graph.neighbors(v):
            if self.assignment[neighbor] == color:
                return False
        return True

    def legal_values(self, v):
        return [c for c in self.domains[v] if self.is_consistent(v, c)]

    def unassigned_cities(self):
        return [v for v in range(self.graph.n)
                if self.assignment[v] is None]

    def is_valid_coloring(self):
        for v in range(self.graph.n):
            if self.assignment[v] is None:
                return False
            for neighbor in self.graph.neighbors(v):
                if self.assignment[neighbor] == self.assignment[v]:
                    return False
        return True

    def select_variable(self, use_heuristics):
        free = self.unassigned_cities()
        if not use_heuristics:
            return free[0]

        def key(v):
            remaining = len(self.legal_values(v))
            free_neighbors = sum(
                self.assignment[neighbor] is None
                for neighbor in self.graph.neighbors(v))
            return remaining, -free_neighbors

        return min(free, key=key)

    def order_values(self, v, use_heuristics):
        values = self.legal_values(v)
        if not use_heuristics:
            return values

        def ruled_out(color):
            count = 0
            for neighbor in self.graph.neighbors(v):
                if (self.assignment[neighbor] is None
                        and color in self.legal_values(neighbor)):
                    count += 1
            return count

        return sorted(values, key=ruled_out)

    def forward_check(self, v, color):
        for neighbor in self.graph.neighbors(v):
            if (self.assignment[neighbor] is None
                    and color in self.domains[neighbor]):
                self.domains[neighbor].remove(color)
                if not self.domains[neighbor]:
                    return False
        return True

    def revise(self, xi, xj):
        removed = False
        for a in list(self.domains[xi]):
            if not any(a != b for b in self.domains[xj]):
                self.domains[xi].remove(a)
                removed = True
        return removed

    def all_arcs(self):
        return [(u, v) for u in range(self.graph.n)
                for v in self.graph.neighbors(u)]

    def ac3(self, arcs):
        queue = list(arcs)
        while queue:
            xi, xj = queue.pop(0)
            if self.revise(xi, xj):
                if not self.domains[xi]:
                    return False
                for xk in self.graph.neighbors(xi):
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def backtrack(self, use_heuristics, inference):
        free = self.unassigned_cities()
        if not free:
            return True

        city = self.select_variable(use_heuristics)
        for color in self.order_values(city, use_heuristics):
            saved_domains = [list(domain) for domain in self.domains]
            self.assignment[city] = color
            self.assignments_made += 1

            valid = True
            if inference == "fc":
                valid = self.forward_check(city, color)
            elif inference == "ac3":
                self.domains[city] = [color]
                arcs = [(neighbor, city)
                        for neighbor in self.graph.neighbors(city)
                        if self.assignment[neighbor] is None]
                valid = self.ac3(arcs)

            if valid and self.backtrack(use_heuristics, inference):
                return True

            self.assignment[city] = None
            self.domains = saved_domains
            self.backtracks += 1

        return False

    def solve(self, use_heuristics=False, inference=None):
        self.assignment = [None] * self.graph.n
        self.domains = [
            list(range(self.num_colors)) for _ in range(self.graph.n)]
        self.assignments_made = 0
        self.backtracks = 0

        start = time.perf_counter()
        valid = True
        if inference == "ac3":
            valid = self.ac3(self.all_arcs())
        success = valid and self.backtrack(use_heuristics, inference)
        runtime = time.perf_counter() - start
        return success, runtime


class MeasuredCSP(ColoringCSP):
    """Track colors removed by forward checking and AC-3."""

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
