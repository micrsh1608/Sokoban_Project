"""Preserve spaces; flood-fill exterior to distinguish padding from floor."""
from collections import deque
from pathlib import Path
from .model import Board, Layout


def parse_map(text: str, competitive: bool = False) -> Layout:
    lines = text.splitlines()
    if not lines or any(not line for line in lines):
        raise ValueError("Map is empty or contains an empty row.")
    allowed = set("%ABDC ") | ({"P"} if competitive else set())
    invalid = set("".join(lines)) - allowed
    if invalid:
        raise ValueError(f"Unsupported map characters: {sorted(invalid)!r}")
    height, width = len(lines), max(map(len, lines))
    walls, goals, boxes = set(), set(), set()
    agents = {"A": [], "P": []}
    for r, line in enumerate(lines):
        for c, char in enumerate(line):
            pos = (r, c)
            if char == "%": walls.add(pos)
            if char in "DC": goals.add(pos)
            if char in "BC": boxes.add(pos)
            if char in agents: agents[char].append(pos)
    if len(agents["A"]) != 1 or len(agents["P"]) != int(competitive):
        raise ValueError("Use one A; competitive maps also require one P.")
    if not boxes or len(boxes) != len(goals):
        raise ValueError("Team convention: equal, nonzero numbers of boxes and goals.")
    # One-cell padding surrounds even rectangular maps. Any non-wall cell
    # connected to this exterior is VOID, not a playable space.
    outside = {(-1, -1)}
    queue = deque(outside)
    while queue:
        r, c = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            p = (r + dr, c + dc)
            if (-1 <= p[0] <= height and -1 <= p[1] <= width
                    and p not in walls and p not in outside):
                outside.add(p)
                queue.append(p)
    entities = goals | boxes | set(agents["A"] + agents["P"])
    if entities & outside:
        raise ValueError("Map is not enclosed: an entity is connected to exterior.")
    floors = {(r, c) for r in range(height) for c in range(width)
              if (r, c) not in walls and (r, c) not in outside}
    players = tuple(agents["A"] + agents["P"])
    return Layout(Board(width, height, frozenset(walls), frozenset(floors),
                        frozenset(goals)), players, frozenset(boxes))


def load_map(path: str | Path, competitive: bool = False) -> Layout:
    return parse_map(Path(path).read_text(encoding="utf-8-sig"), competitive)
