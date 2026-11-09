import math
import tkinter as tk
from tkinter import messagebox, ttk

from .csp import coloring_results
from .graph import COLORS, load_graph
from .policegame import chase_results


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
                self.stats.insert(
                    "end", " | ".join(str(value) for value in row) + "\n")
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
