import random
import time


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
