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
COLORS = ["red", "green", "blue"] #may need more colors after testing

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

    def unnasigned_cities(self):
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

        free = self.unnasigned_cities
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
 
class ChaseGame:
    """Part B settings. A state is (police_city, thief_city, moves_made)."""
 
    def __init__(self, graph, max_moves=10):
        self.graph = graph
        #use this map as the game board

        self.max_moves = max_moves
        #thief wins if not caught by this many moves

        self.nodes_expanded = 0

def main():
    graph = Graph(CITIES)
    graph.load_edges("CS362_Project_Data(edge_weights).csv")
    graph.load_heuristics("CS362_Project_Data(heuristics).csv")

if __name__ == "__main__":
    main()