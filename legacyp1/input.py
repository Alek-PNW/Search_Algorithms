import csv
import json

cities = [
    "Phoenix", "Los Angeles", "Denver", "Boise", "Wichita",
    "Bozeman", "Omaha", "Las Vegas", "Albuquerque", "Fargo",
    "Oklahoma City", "Portland", "Sioux Falls", "Dallas",
    "Salt Lake City", "Seattle", "Jackson",
]

with open("CS362_Project1_Data(edge_weights).csv", encoding="utf-8") as file:
    reader = csv.reader(file)
    header = [city.strip() for city in next(reader)[1:]]
    graph = [[0 for _ in cities] for _ in cities]

    for row in reader:
        source = row[0].strip()
        if not source:
            continue
        source_index = cities.index(source)

        for column, value in enumerate(row[1:]):
            value = value.strip()
            if not value:
                continue

            destination_index = cities.index(header[column])
            cost = float(value)
            graph[source_index][destination_index] = cost
            graph[destination_index][source_index] = cost

heuristics = [[0 for _ in cities] for _ in cities]

with open("CS362_Project1_Data(heuristics).csv", encoding="utf-8") as file:
    reader = csv.reader(file)
    header = [city.strip() for city in next(reader)[1:]]

    for row in reader:
        source = row[0].strip()
        if not source:
            continue
        source_index = cities.index(source)

        for column, value in enumerate(row[1:]):
            value = value.strip()
            if not value:
                continue

            destination_index = cities.index(header[column])
            heuristic = float(value)
            heuristics[source_index][destination_index] = heuristic
            heuristics[destination_index][source_index] = heuristic

data = {
    "cities": cities,
    "graph": graph,
    "heuristics": heuristics,
}

with open("input.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4)
