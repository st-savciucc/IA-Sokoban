"""
LRTA* (Learning Real-Time A*) solver for Sokoban
Adapted to use internal deadlock pruning, cycle avoidance, and periodic feedback.
"""
import math

class LRTAStar:
    def __init__(self, start_state, heuristic_fn):
        self.start = start_state.copy()
        self.h = heuristic_fn
        self.H = {}              
        self.max_steps = 1000000 

    @staticmethod
    def _key(state):
        boxes = (state.boxes.values() if isinstance(state.boxes, dict) else state.boxes)
        boxes_key = tuple(sorted((b.x, b.y) for b in boxes))
        player_key = (state.player.x, state.player.y)
        return boxes_key, player_key

    def solve(self, max_steps=None):
        max_steps = max_steps or self.max_steps or 1_000_000
        current = self.start
        path = [current]
        visited = {self._key(current)}

        for step in range(1, max_steps + 1):
            if step % 5000 == 0:
                print(f"  LRTA*: pasul {step}/{max_steps}…")

            if current.is_solved():
                return path

            all_succs = current.get_neighbours()
            pruned = [s for s in all_succs if self.h(s) < math.inf]
            if not pruned:
                raise RuntimeError("Blocaj: toate succesele sunt deadlock")

            non_visited = [s for s in pruned if self._key(s) not in visited]
            succs = non_visited if non_visited else pruned

            curr_k = self._key(current)
            f_vals = []
            for s in succs:
                k = self._key(s)
                h_s = self.H.get(k, self.h(s))
                f_vals.append(1 + h_s)
            self.H[curr_k] = max(self.h(current), min(f_vals))

            f_min = min(f_vals)
            candidates = [i for i, f in enumerate(f_vals) if f == f_min]
            best_idx = min(candidates, key=lambda i: self.h(succs[i]))
            next_state = succs[best_idx]

            visited.add(self._key(next_state))
            path.append(next_state)
            current = next_state

        raise TimeoutError(f"Nu s‑a găsit soluție în {max_steps} pași")
