"""
Heuristics for Sokoban – full code with deadlock detection using internal wall checks.
"""

import math
from functools import lru_cache

# --------------------------------------------------------- utility: extract coordinates
def _xy(obj):
    """
    Extracts (x, y) from various representations:
      • tuple (x, y)                       – target coordinates
      • tuple ('id', x, y)                 – raw box data
      • Box object with .x and .y attributes
    """
    if isinstance(obj, tuple):
        if len(obj) == 3 and isinstance(obj[0], str):  # ('id', x, y)
            return obj[1], obj[2]
        if len(obj) == 2:  # (x, y)
            return obj[0], obj[1]
    if hasattr(obj, 'x') and hasattr(obj, 'y'):
        return obj.x, obj.y
    if hasattr(obj, 'row') and hasattr(obj, 'col'):
        return obj.col, obj.row
    raise TypeError(f"Cannot extract coordinates from {obj!r}")

# --------------------------------------------------------- utility: Manhattan distance
def _manhattan(a, b):
    ax, ay = _xy(a)
    bx, by = _xy(b)
    return abs(ax - bx) + abs(ay - by)

# --------------------------------------------------------- utility: is_wall fallback
def _is_wall(state, x, y):
    """
    Returns True if (x, y) is outside bounds or a wall in the Sokoban map.
    Checks:
      • state.walls (set of coords)
      • state.static_map (grid of chars '#')
      • state.width/height bounds
    """
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

# --------------------------------------------------------- deadlock detection
def _is_corner_deadlock(state, box):
    """
    Detects corner deadlock: box is adjacent to walls on two axes
    and not on a target.
    """
    x, y = _xy(box)
    horz = _is_wall(state, x - 1, y) or _is_wall(state, x + 1, y)
    vert = _is_wall(state, x, y - 1) or _is_wall(state, x, y + 1)
    return horz and vert and (x, y) not in state.targets

# --------------------------------------------------------- basic heuristic
def sum_boxes_min_goal_distance(state):
    """
    Sum of Manhattan distances from each box to nearest goal.
    Returns math.inf if any box is in a corner deadlock.
    """
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

# --------------------------------------------------------- enhanced heuristic
def sum_boxes_plus_player(state):
    """
    Combines box-to-goal sum with distance from player to nearest box.
    """
    base = sum_boxes_min_goal_distance(state)
    if base == math.inf:
        return math.inf
    px, py = _xy(state.player)
    boxes = state.boxes.values() if isinstance(state.boxes, dict) else state.boxes
    mind = min(_manhattan((px, py), box) for box in boxes)
    return base + mind
