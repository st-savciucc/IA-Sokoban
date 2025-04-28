#!/usr/bin/env python3
"""
main.py – Driver adaptiv pt Tema 1 Sokoban
"""

import argparse
import time
import os
import shutil
from pathlib import Path

import imageio.v2 as imageio

from sokoban.map import Map
from search_methods.solver import (
    get_solver,
    LrtaStarSolver,
    GreedySolver,
    SimulatedAnnealingSolver
)


def load_map(path: str) -> Map:
    return Map.from_yaml(path)


def save_gif(states, yaml_path, out_dir="images", fps=5):
    name = Path(yaml_path).stem
    os.makedirs(out_dir, exist_ok=True)

    tmp_dir = Path("tmp_frames")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()

    frames = []
    for i, st in enumerate(states):
        png_name = f"{name}_{i:04d}.png"
        # Map.save_map(dir_path, save_name)
        st.save_map(str(tmp_dir), png_name)
        frames.append(imageio.imread(tmp_dir / png_name))

    gif_path = Path(out_dir) / f"{name}.gif"
    imageio.mimsave(gif_path, frames, fps=fps)
    print(f"[GIF] salvat în {gif_path}")

    shutil.rmtree(tmp_dir)

def run_solver(
    algorithm: str,
    heuristic_type: str,
    map_path: str,
    make_gif: bool = False,
    max_steps: int | None = None
):
    print(f"DEBUG: {algorithm}  h={heuristic_type}  map={map_path}")

    # 1) Incarca harta
    state = load_map(map_path)

    # 2) Buget implicit
    if max_steps is None:
        if 'super_hard' in map_path:
            max_steps = 400_000
        elif 'large' in map_path:
            max_steps = 300_000
        else:
            max_steps = 150_000

    # 3) Upgrade euristica
    auto_h = heuristic_type
    if auto_h == 'base' and ('large' in map_path or 'super_hard' in map_path):
        auto_h = 'enhanced'
        print("  INFO: folosim euristica enhanced pe harta mare")

    # 4) Construieste solver
    solver = get_solver(algorithm, state, auto_h, max_steps)

    # 5) Ruleaza
    t0 = time.perf_counter()
    try:
        states = solver.solve()
    except Exception as e:
        print(f"[{algorithm}] {map_path} | ERROR: {e}")
        return
    dt = time.perf_counter() - t0

    # 6) Metrici
    solved = states and states[-1].is_solved()
    steps = len(states) - 1 if states else 0
    pulls = 0

    extra = ""
    if isinstance(solver, LrtaStarSolver):
        extra = f" | H_size: {len(solver._solver.H)}"
    elif isinstance(solver, GreedySolver):
        extra = f" | Greedy_iters: {solver.last_steps}"
    elif isinstance(solver, SimulatedAnnealingSolver):
        extra = f" | SA_iters: {solver.last_steps}"

    status = "SOLVED" if solved else "NOT_SOLVED"
    print(f"[{algorithm}] {map_path} | h={auto_h} | time: {dt:.2f}s | "
          f"steps: {steps} | pulls: {pulls} | status: {status}{extra}")

    # 7) GIF
    if make_gif and solved:
        save_gif(states, map_path)


def parse_cli():
    p = argparse.ArgumentParser(description="Sokoban adaptive driver")
    p.add_argument('algorithm', choices=['lrta*', 'sa'])
    p.add_argument('--heuristic', choices=['base', 'enhanced'], default='base')
    p.add_argument('yaml_map', help="Fișier .yaml cu harta Sokoban")
    p.add_argument('--max-steps', type=int, default=None,
                   help="Buget pași LRTA*/Greedy")
    p.add_argument('--gif', action='store_true', help="Salveaza solutia ca GIF")
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
