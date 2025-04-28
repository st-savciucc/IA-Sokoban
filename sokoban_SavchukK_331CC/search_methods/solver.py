# search_methods/solver.py
"""
solver.py – Adaptiv: LRTA*, Greedy (cu buget), Simulated Annealing (multi-restart)
"""

from abc import ABC, abstractmethod
import random
import math
import itertools

from search_methods.lrta_star import LRTAStar
from search_methods.heuristics import (
    sum_boxes_min_goal_distance,
    sum_boxes_plus_player
)


class Solver(ABC):
    def __init__(self, map_obj, heuristic_fn):
        self.map = map_obj
        self.heuristic = heuristic_fn

    @abstractmethod
    def solve(self):
        ...


class LrtaStarSolver(Solver):
    def __init__(self, map_obj, heuristic_fn, max_steps: int = 500_000):
        super().__init__(map_obj, heuristic_fn)
        self._solver = LRTAStar(self.map, self.heuristic)
        self._solver.max_steps = max_steps

    def solve(self):
        return self._solver.solve()


class GreedySolver(Solver):
    def __init__(self, map_obj, heuristic_fn):
        super().__init__(map_obj, heuristic_fn)
        self.last_steps = 0

    def solve(self, max_steps: int | None = None):
        cur = self.map.copy()
        path = [cur]
        for step in itertools.count(1):
            if max_steps and step > max_steps:
                raise TimeoutError("GreedySolver: buget epuizat")
            if cur.is_solved():
                self.last_steps = step - 1
                return path
            succs = [s for s in cur.get_neighbours()
                     if self.heuristic(s) < float('inf')]
            if not succs:
                raise RuntimeError("GreedySolver: dead-end")
            cur = min(succs, key=self.heuristic)
            path.append(cur)


class SimulatedAnnealingSolver(Solver):
    def __init__(
        self,
        map_obj,
        heuristic_fn,
        T0: float = 2000.0,
        alpha: float = 0.999,
        min_T: float = 1e-4,
        max_steps: int = 500_000,
        restarts: int = 5,
        seed: int = 0
    ):
        super().__init__(map_obj, heuristic_fn)
        self.T0 = T0
        self.alpha = alpha
        self.min_T = min_T
        self.max_steps = max_steps
        self.restarts = restarts
        self.seed = seed
        self.last_steps = 0

    def solve(self):
        best_path = []
        best_len = -1
        best_steps = 0

        for r in range(self.restarts):
            random.seed(self.seed + r)
            cur = self.map.copy()
            path = [cur]
            T = self.T0
            steps = 0

            while T > self.min_T and steps < self.max_steps:
                if cur.is_solved():
                    self.last_steps = steps
                    return path
                neigh = random.choice(cur.get_neighbours())
                if self.heuristic(neigh) == float('inf'):
                    steps += 1
                    T *= self.alpha
                    continue
                delta = self.heuristic(neigh) - self.heuristic(cur)
                if delta < 0 or math.exp(-delta / T) > random.random():
                    cur = neigh
                    path.append(cur)
                T *= self.alpha
                steps += 1

            if len(path) > best_len:
                best_len = len(path)
                best_path = path
                best_steps = steps

        self.last_steps = best_steps
        return best_path


class AdaptiveSolver(Solver):
    def __init__(
        self,
        map_obj,
        heuristic_fn,
        greedy_budget: int = 4000,
        lrta_budget: int = 300_000
    ):
        super().__init__(map_obj, heuristic_fn)
        self.greedy_budget = greedy_budget
        self.lrta_budget = lrta_budget

    def solve(self):
        try:
            gs = GreedySolver(self.map, self.heuristic)
            states = gs.solve(max_steps=self.greedy_budget)
            print(f"  AdaptiveSolver: solved greedy in {gs.last_steps} pasi")
            return states
        except TimeoutError:
            print("  AdaptiveSolver: buget greedy epuizat, trec la LRTA*")
        except Exception:
            print("  AdaptiveSolver: greedy a esuat, trec la LRTA*")

        try:
            lrta = LrtaStarSolver(self.map, self.heuristic, max_steps=self.lrta_budget)
            states = lrta.solve()
            print(f"  AdaptiveSolver: solved LRTA* în {len(states)-1} pasi")
            return states
        except TimeoutError:
            print("  AdaptiveSolver: LRTA* timeout, trec la SA")

        sa = SimulatedAnnealingSolver(
            self.map,
            self.heuristic,
            T0=2000.0,
            alpha=0.999,
            min_T=1e-4,
            max_steps=500_000,
            restarts=5,
            seed=0
        )
        states = sa.solve()
        print(f"  AdaptiveSolver: fallback SA dupa {sa.last_steps} iteratii")
        return states


def get_solver(
    algorithm: str,
    map_obj,
    heuristic_type: str = 'base',
    max_steps: int | None = None
):
    heur_fn = (
        sum_boxes_min_goal_distance
        if heuristic_type == 'base'
        else sum_boxes_plus_player
    )

    if algorithm == 'lrta*':
        if max_steps and max_steps > 200_000:
            return AdaptiveSolver(map_obj, heur_fn,
                                  greedy_budget=4000,
                                  lrta_budget=max_steps)
        return LrtaStarSolver(map_obj, heur_fn, max_steps or 500_000)

    if algorithm == 'sa':
        ms = max_steps or 500_000
        return SimulatedAnnealingSolver(
            map_obj,
            heur_fn,
            T0=2000.0,
            alpha=0.999,
            min_T=1e-4,
            max_steps=ms,
            restarts=5,
            seed=0
        )

    raise ValueError(f"Unknown algorithm: {algorithm}")
