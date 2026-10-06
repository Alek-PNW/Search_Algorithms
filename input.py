graph = {
    "Phoenix": {
        "Los Angeles": 372,
        "Las Vegas": 302,
        "Albuquerque": 418,
        "Salt Lake City": 663
    },

    "Los Angeles": {
        "Phoenix": 372,
        "Las Vegas": 281,
        "Portland": 963
    },

    "Denver": {
        "Wichita": 518,
        "Omaha": 539,
        "Albuquerque": 447,
        "Oklahoma City": 677,
        "Salt Lake City": 519,
        "Jackson": 513
    },

    "Boise": {
        "Bozeman": 476,
        "Las Vegas": 624,
        "Portland": 430,
        "Salt Lake City": 339,
        "Seattle": 494,
        "Jackson": 369
    },

    "Wichita": {
        "Denver": 518,
        "Omaha": 302,
        "Oklahoma City": 162
    },

    "Bozeman": {
        "Boise": 476,
        "Fargo": 749,
        "Sioux Falls": 801,
        "Jackson": 216
    },

    "Omaha": {
        "Denver": 539,
        "Wichita": 302,
        "Sioux Falls": 181,
        "Jackson": 928
    },

    "Las Vegas": {
        "Phoenix": 302,
        "Los Angeles": 281,
        "Boise": 624,
        "Portland": 971,
        "Salt Lake City": 421
    },

    "Albuquerque": {
        "Phoenix": 418,
        "Denver": 447,
        "Oklahoma City": 543,
        "Dallas": 649
    },

    "Fargo": {
        "Bozeman": 749,
        "Sioux Falls": 243
    },

    "Oklahoma City": {
        "Denver": 677,
        "Wichita": 162,
        "Albuquerque": 543,
        "Dallas": 206
    },

    "Portland": {
        "Los Angeles": 963,
        "Boise": 430,
        "Las Vegas": 971,
        "Seattle": 174
    },

    "Sioux Falls": {
        "Bozeman": 801,
        "Omaha": 181,
        "Fargo": 243,
        "Jackson": 885
    },

    "Dallas": {
        "Albuquerque": 649,
        "Oklahoma City": 206
    },

    "Salt Lake City": {
        "Phoenix": 663,
        "Denver": 519,
        "Boise": 339,
        "Las Vegas": 421,
        "Jackson": 280
    },

    "Seattle": {
        "Boise": 494,
        "Portland": 174
    },

    "Jackson": {
        "Denver": 513,
        "Boise": 369,
        "Bozeman": 216,
        "Omaha": 928,
        "Sioux Falls": 885,
        "Salt Lake City": 280
    }
}
import csv
import json

cities = [
    "Phoenix","Los Angeles","Denver","Boise","Wichita",
    "Bozeman","Omaha","Las Vegas","Albuquerque","Fargo",
    "Oklahoma City","Portland","Sioux Falls","Dallas",
    "Salt Lake City","Seattle","Jackson"
]

heuristics = {city: {} for city in cities}

with open("CS362_Project1_Data(heuristics).csv") as f:
    reader = csv.reader(f)

    header = next(reader)[1:]

    for row in reader:
        source = row[0]

        for i in range(1, len(row)):
            value = row[i].strip()

            if value == "":
                continue

            destination = header[i - 1]

            h = float(value)

            heuristics[source][destination] = h
            heuristics[destination][source] = h
data = {
    "graph": graph,
    "heuristics": heuristics
}

with open("input.json", "w") as f:
    json.dump(data, f, indent=4)