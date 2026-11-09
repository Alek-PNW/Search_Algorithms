import random
import time


class ChaseGame:
    def __init__(self, graph, max_moves=10):
        self.graph = graph
        self.max_moves = max_moves
        self.nodes_expanded = 0
        self.branches_pruned = 0
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
        if turns % 2 == 0:
            caught = destination != police and destination == thief
            return destination, thief, turns + 1, caught
        return police, destination, turns + 1, False

    def search(self, state, depth, use_pruning=False, order_moves=False,
               alpha=float("-inf"), beta=float("inf"), is_root=True):
        police, thief, turns, _ = state

        winner = self.winner(state)
        if winner == "Police":
            return self.win_score, None
        if winner == "Thief":
            return -self.win_score, None
        if depth == 0:
            return -self.graph.h[police][thief], None

        self.nodes_expanded += 1
        police_turn = turns % 2 == 0
        if police_turn:
            current, opponent = police, thief
            best_score = float("-inf")
        else:
            current, opponent = thief, police
            best_score = float("inf")

        moves = self.graph.neighbors(current) + [current]
        if order_moves and not is_root:
            moves.sort(key=lambda city: self.graph.h[city][opponent])

        best_move = None
        for move_index, destination in enumerate(moves):
            next_state = self.move(state, destination)
            score, _ = self.search(
                next_state, depth - 1, use_pruning, order_moves,
                alpha, beta, is_root=False)

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

            if use_pruning and alpha >= beta:
                self.branches_pruned += len(moves) - move_index - 1
                break

        return best_score, best_move

    def play(self, police, thief, depth, use_pruning=False, order_moves=False):
        self.nodes_expanded = 0
        self.branches_pruned = 0
        state = (police, thief, 0, False)
        history = [state]
        start = time.perf_counter()

        while self.winner(state) is None:
            _, destination = self.search(
                state, depth, use_pruning, order_moves)
            state = self.move(state, destination)
            history.append(state)

        seconds = time.perf_counter() - start
        return history, self.winner(state), self.nodes_expanded, seconds


def chase_results(graph, depth, method, ordering, compare=False):
    pairs = [(police, thief) for police in range(graph.n)
             for thief in range(graph.n) if police != thief]
    starts = random.Random(362).sample(pairs, 5)
    versions = [(method, method == "Alpha-beta", ordering)]
    depths = [depth]
    if compare:
        versions = [("Minimax", False, False),
                    ("Alpha-beta", True, False),
                    ("Alpha-beta + ordering", True, True)]
        depths = [2, 4, 6]
    rows, replays = [], []
    for chase, (police, thief) in enumerate(starts, 1):
        for limit in depths:
            results = []
            base_nodes = None
            for name, pruning, ordered in versions:
                game = ChaseGame(graph)
                history, winner, nodes, seconds = game.play(
                    police, thief, limit, pruning, ordered)
                savings = ""
                if compare and name == "Alpha-beta":
                    base_nodes = nodes
                if compare and name == "Alpha-beta + ordering":
                    savings = base_nodes - nodes
                rows.append((chase, limit, name, "Yes" if ordered else "No",
                             winner, nodes, game.branches_pruned,
                             f"{seconds:.6f}", savings))
                results.append(history)
                label = f"{chase} | depth {limit} | {name}"
                replays.append((label, history, winner))
            if compare:
                minimax_path = results[0]
                for path in results[1:]:
                    if path != minimax_path:
                        raise RuntimeError(
                            "Minimax and alpha-beta chose different moves.")
    return rows, replays
