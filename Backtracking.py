
    def backtrack(self):
        #pick the next city that needs a color
        free = self.unnasigned_cities()

        #all cities have been colored
        if not free:
            return True

        city = free[0]


        #try the available colors for this city
        for color in self.order_values(city, False):
            self.assignment[city] = color
            self.assignments_made += 1

            #move on to the next city
            if self.backtrack():
                return True

            #if it doesnt work, remove the color and try again
            self.assignment[city] = None
            self.backtracks += 1

        return False

    def solve(self):
        #reset assignments and stats before starting
        self.assignment = [None] * self.graph.n
        self.assignments_made = 0
        self.backtracks = 0

        #track how long the search takes
        start = time.perf_counter()
        success = self.backtrack()
        runtime = time.perf_counter() - start

        return success, runtime


def find_minimum_colors(graph):
    color_names = ["red", "green", "blue", "yellow"]

    #start with one color and increase if needed
    for num_colors in range(1, 5):
        solver = ColoringCSP(graph, num_colors)
        success, runtime = solver.solve()

        print(f"\nTesting with {num_colors} colors")
        print(f"Solution found: {success}")
        print(f"Assignments made: {solver.assignments_made}")
        print(f"Backtracks: {solver.backtracks}")
        print(f"Runtime: {runtime:.6f} seconds")

        if success:
            #make sure neighboring cities have different colors
            if not solver.is_valid_coloring():
                raise ValueError("Invalid coloring found")

            print(f"\nMinimum colors needed: {num_colors}")

            for i, city in enumerate(graph.cities):
                color = color_names[solver.assignment[i]]
                print(f"{city}: {color}")

            return num_colors, solver.assignment.copy()

    print("No solution found with up to 4 colors")
    return None, None
