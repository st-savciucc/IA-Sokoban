# main.py
#!/usr/bin/env python3
"""
main.py – Driver adaptiv pentru Tema 1 Sokoban
"""

import argparse
import time
import os

from sokoban.map import Map
from search_methods.solver import (
    get_solver,
    LrtaStarSolver,
    GreedySolver,
    SimulatedAnnealingSolver
)

def load_map(path: str) -> Map:
    return Map.from_yaml(path)

def save_gif(state: Map, states, out_dir: str = "images"):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{state.name}.gif")
    state.visualize(states, save_gif=True, path=path)

def run_solver(
    algorithm: str,
    heuristic_type: str,
    map_path: str,
    make_gif: bool = False,
    max_steps: int | None = None
):
    print(f"DEBUG: {algorithm}  h={heuristic_type}  map={map_path}")

    # 1) Încarcă harta
    state = load_map(map_path)

    # 2) Setează buget implicit dacă nu ai dat --max-steps
    if max_steps is None:
        if 'super_hard' in map_path:
            max_steps = 400_000
        elif 'large' in map_path:
            max_steps = 300_000
        else:
            max_steps = 150_000

    # 3) Upgrade euristică pe hărţi mari
    auto_h = heuristic_type
    if auto_h == 'base' and ('large' in map_path or 'super_hard' in map_path):
        auto_h = 'enhanced'
        print("  INFO: folosim euristica enhanced pe hartă mare")

    # 4) Obține solver-ul corect
    solver = get_solver(algorithm, state, auto_h, max_steps)

    # 5) Rulează și cronometează
    t0 = time.perf_counter()
    try:
        states = solver.solve()
    except Exception as e:
        print(f"[{algorithm}] {map_path} | ERROR: {e}")
        return
    dt = time.perf_counter() - t0

    # 6) Colectează metrici generale
    solved = states and states[-1].is_solved()
    steps = len(states) - 1 if states else 0
    pulls = 0  # în continuare toate testele tale au 0 pull

    # 7) Detalii adiționale pe tip de solver
    extra = ""
    if isinstance(solver, LrtaStarSolver):
        H_size = len(solver._solver.H)
        extra = f" | H_size: {H_size}"
    elif isinstance(solver, GreedySolver):
        extra = f" | Greedy_iters: {solver.last_steps}"
    elif isinstance(solver, SimulatedAnnealingSolver):
        extra = f" | SA_iters: {solver.last_steps}"

    status = "SOLVED" if solved else "NOT_SOLVED"
    print(
        f"[{algorithm}] {map_path} | h={auto_h} | time: {dt:.2f}s | "
        f"steps: {steps} | pulls: {pulls} | status: {status}{extra}"
    )

    # 8) GIF opțional
    if make_gif and solved:
        save_gif(state, states)

def parse_cli():
    p = argparse.ArgumentParser(description="Sokoban adaptive driver")
    p.add_argument('algorithm', choices=['lrta*', 'sa'])
    p.add_argument('--heuristic', choices=['base', 'enhanced'], default='base')
    p.add_argument('yaml_map', help="Fișierul .yaml cu harta Sokoban")
    p.add_argument('--max-steps', type=int, default=None,
                   help="Buget pași pentru LRTA* / Greedy")
    p.add_argument('--gif', action='store_true', help="Salvează soluția ca GIF")
    return p.parse_args()

if __name__ == '__main__':
    args = parse_cli()
    run_solver(
        args.algorithm,
        args.heuristic,
        args.yaml_map,
        args.gif,
        args.max_steps
    )
