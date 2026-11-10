# Search Algorithms

This repository contains two Python projects that demonstrate search and
constraint-satisfaction algorithms on a highway map of western U.S. cities.
Both projects use the included CSV data files.

## Requirements

- Python 3.11 or newer
- Tkinter for the Project 2 graphical interface (usually included with Python;
  some Linux distributions provide it as a separate package)
- A desktop or forwarded graphical display to show the Project 2 window

No third-party Python packages are required.

## Run from the repository folder

Open a terminal in the folder containing `project1.py`, `project2.py`, and
the two CSV files.

### Project 1: graph search

Project 1 runs DFS, BFS, Uniform-Cost Search, and A* on five randomly selected
start/target city pairs, reporting the routes and distances.

Windows:

```cmd
py project1.py
```

Linux or macOS:

```bash
python3 project1.py
```

### Project 2: coloring and police/thief game

Project 2 opens a Tkinter window. It lets you configure and compare map
coloring methods (backtracking, heuristics, forward checking, and AC-3), run
police/thief chase searches (minimax and alpha-beta), and view chase replays.

Implemented Algorithms

Part A: Constraint Satisfaction(Map Coloring)
- Backtracking Search
- Minimum Remaining Values(MRV)
- Degree Heuristic
- Least Constraining Value(LCV)
- Forward Checking
- AC-3(Arc Consistency)

Part B: Adversarial Search(Police vs. Thief)
- Minimax Search
- Alpha-Beta Pruning
- Move Ordering
- Depth-Limited Search

Windows:

```cmd
py project2.py
```

Linux or macOS:

```bash
python3 project2.py
```

The GUI needs access to a graphical display. In a headless terminal without a
display, Tkinter cannot open a visible window. To run Project 2's text-based
algorithm reports instead, use:

```bash
python -c "import project2; project2.run_cli()"
```

On systems where the command is `python3`, replace `python` with `python3`.

## Separated modules

The `legacyp1/` and `legacyp2/` folders contain separated versions of the
projects. Run them from the repository root:

```bash
python legacyp1/search_algorithms.py
python -m legacyp2.main_legacy
```

The Project 1 separated runner reads `input.json`. The Project 2 modules
separate graph loading, CSP coloring, the police/thief game, graphics, and the
runner. Its runner opens the same Tkinter GUI and therefore also requires a
display. On systems where the command is `python3`, replace `python` with
`python3`.

## Data files

- `CS362_Project_Data(edge_weights).csv` provides highway connections and
  their distances.
- `CS362_Project_Data(heuristics).csv` provides straight-line distance
  estimates used by A* and the chase game.

Keep both CSV files in the repository root when running `project1.py` or
`project2.py`. The separated Project 1 runner instead reads the included
`input.json`.

## Authors

- Alek R
- Jonathan G
- Josh B
- Justin B
- Brennen C
- Feranmi M
