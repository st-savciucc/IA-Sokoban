"""
Heuristics for Sokoban – full code with deadlock detection using internal wall checks.
"""

import math
from functools import lru_cache

def _xy(obj):
    if isinstance(obj, tuple):
        if len(obj) == 3 and isinstance(obj[0], str):
            return obj[1], obj[2]
        if len(obj) == 2:
            return obj[0], obj[1]
    if hasattr(obj, 'x') and hasattr(obj, 'y'):
        return obj.x, obj.y
    if hasattr(obj, 'row') and hasattr(obj, 'col'):
        return obj.col, obj.row
    raise TypeError(f"Cannot extract coordinates from {obj!r}")

def _manhattan(a, b):
    ax, ay = _xy(a)
    bx, by = _xy(b)
    return abs(ax - bx) + abs(ay - by)

def _is_wall(state, x, y):
    if hasattr(state, 'walls'):
        return (x, y) in state.walls
    if hasattr(state, 'static_map'):
        try:
            return state.static_map[y][x] == '#'
        except Exception:
            pass
    if hasattr(state, 'width') and hasattr(state, 'height'):
        if x < 0 or y < 0 or x >= state.width or y >= state.height:
            return True
    return False

def _is_corner_deadlock(state, box):
    x, y = _xy(box)
    horz = _is_wall(state, x - 1, y) or _is_wall(state, x + 1, y)
    vert = _is_wall(state, x, y - 1) or _is_wall(state, x, y + 1)
    return horz and vert and (x, y) not in state.targets

def sum_boxes_min_goal_distance(state):
    boxes = state.boxes.values() if isinstance(state.boxes, dict) else state.boxes
    for box in boxes:
        if _is_corner_deadlock(state, box):
            return math.inf
    return _cached_sum(id(state), state)

@lru_cache(maxsize=None)
def _cached_sum(_state_id, state):
    boxes = state.boxes.values() if isinstance(state.boxes, dict) else state.boxes
    goals = list(state.targets)
    total = 0
    for box in boxes:
        dists = [_manhattan(box, g) for g in goals]
        idx = min(range(len(dists)), key=dists.__getitem__)
        total += dists[idx]
        goals.pop(idx)
    return total

def sum_boxes_plus_player(state):
    base = sum_boxes_min_goal_distance(state)
    if base == math.inf:
        return math.inf
    px, py = _xy(state.player)
    boxes = state.boxes.values() if isinstance(state.boxes, dict) else state.boxes
    mind = min(_manhattan((px, py), box) for box in boxes)
    return base + mind
