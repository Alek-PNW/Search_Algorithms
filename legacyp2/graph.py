import csv
from pathlib import Path


CITIES = [
    "Phoenix", "Los Angeles", "Denver", "Boise", "Wichita",
    "Bozeman", "Omaha", "Las Vegas", "Albuquerque", "Fargo",
    "Oklahoma City", "Portland", "Sioux Falls", "Dallas",
    "Salt Lake City", "Seattle", "Jackson",
]
COLORS = ["red", "green", "blue", "yellow"]
DATA_FOLDER = Path(__file__).resolve().parent.parent


def read_csv_matrix(filename):
    cells = []
    with open(filename, encoding="utf-8") as file:
        reader = csv.reader(file)
        header = [city.strip() for city in next(reader)[1:]]

        for row in reader:
            source = row[0].strip()
            if not source:
                continue
            for column in range(1, len(row)):
                value = row[column].strip()
                if value:
                    cells.append((source, header[column - 1], float(value)))
    return cells


class Graph:
    def __init__(self, cities):
        self.cities = cities
        self.n = len(cities)
        self.g = [[None] * self.n for _ in range(self.n)]
        self.h = [[0] * self.n for _ in range(self.n)]

    def add_edge(self, u, v, weight):
        self.g[u][v] = weight
        self.g[v][u] = weight

    def set_heuristic(self, u, v, value):
        self.h[u][v] = value
        self.h[v][u] = value

    def load_edges(self, filename):
        for source, dest, value in read_csv_matrix(filename):
            s = self.cities.index(source)
            d = self.cities.index(dest)
            if s != d and self.g[s][d] is None:
                self.add_edge(s, d, value)

    def load_heuristics(self, filename):
        for source, dest, value in read_csv_matrix(filename):
            s = self.cities.index(source)
            d = self.cities.index(dest)
            self.set_heuristic(s, d, value)

    def neighbors(self, v):
        return [j for j in range(self.n) if self.g[v][j] is not None]


def load_graph():
    graph = Graph(CITIES)
    graph.load_edges(DATA_FOLDER / "CS362_Project_Data(edge_weights).csv")
    graph.load_heuristics(DATA_FOLDER / "CS362_Project_Data(heuristics).csv")
    return graph
