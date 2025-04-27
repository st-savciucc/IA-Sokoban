"""
Simulated Annealing pentru Sokoban (versiune generică).
"""

import math, random
from copy import deepcopy

class SimulatedAnnealing:
    def __init__(self, map_obj, heuristic_fn,
                 T0=1000.0, alpha=0.995, min_T=1e-3,
                 max_steps=200_000, seed=0):
        self.initial_map = map_obj.copy()
        self.h = heuristic_fn
        self.T0, self.alpha, self.min_T = T0, alpha, min_T
        self.max_steps = max_steps
        random.seed(seed)

    # ------------------------------------------------------- neighbourhood logic
    def _random_action(self, state):
        """Returnează o acțiune legală aleatoare (push SAU pull)."""
        acts = state.legal_actions()
        return random.choice(acts) if acts else None

    def _neighbour(self, state):
        """Aplică 1 acțiune aleatoare și întoarce noua stare + acțiunea."""
        action = self._random_action(state)
        if action is None:
            return None, None
        new_state = state.apply(action)
        return new_state, action

    # ------------------------------------------------------------- SA main loop
    def solve(self):
        current = self.initial_map
        best = current
        best_cost = self.h(current)
        T = self.T0
        trajectory = []          # pentru reconstituirea drumului

        for step in range(self.max_steps):
            if current.is_goal():
                return trajectory

            neighbour, action = self._neighbour(current)
            if neighbour is None:
                break            # dead‑end

            delta = self.h(neighbour) - self.h(current)
            if delta < 0 or random.random() < math.exp(-delta / T):
                current = neighbour
                trajectory.append(action)
                if self.h(current) < best_cost:
                    best, best_cost = current, self.h(current)

            T *= self.alpha
            if T < self.min_T:
                T = self.T0       # “restart” ușor ca să evităm blocarea

        # Dacă nu s‑a atins goal‑ul, întoarce cea mai bună încercare
        return trajectory  # posibil nevalid – tratează în codul de evaluare
