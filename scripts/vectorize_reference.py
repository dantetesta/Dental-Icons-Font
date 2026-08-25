#!/usr/bin/env python3
"""Convert the isolated reference PNG glyphs into uniform monoline SVGs."""

from __future__ import annotations

import math
import re
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "reference-glyphs"
DESTINATION = ROOT / "assets" / "reference-vectors"


def remove_small_components(mask: np.ndarray, minimum: int = 6) -> np.ndarray:
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    cleaned = mask.copy()
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or seen[y, x]:
                continue
            queue = deque([(y, x)])
            seen[y, x] = True
            component: list[tuple[int, int]] = []
            while queue:
                cy, cx = queue.popleft()
                component.append((cy, cx))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if not (dx or dy):
                            continue
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            queue.append((ny, nx))
            if len(component) < minimum:
                for cy, cx in component:
                    cleaned[cy, cx] = False
    return cleaned


def skeletonize(source: np.ndarray) -> np.ndarray:
    image = np.pad(source.astype(np.uint8), 1)
    changed = True
    while changed:
        changed = False
        for phase in (0, 1):
            p2 = image[:-2, 1:-1]
            p3 = image[:-2, 2:]
            p4 = image[1:-1, 2:]
            p5 = image[2:, 2:]
            p6 = image[2:, 1:-1]
            p7 = image[2:, :-2]
            p8 = image[1:-1, :-2]
            p9 = image[:-2, :-2]
            center = image[1:-1, 1:-1]
            neighbors = (p2, p3, p4, p5, p6, p7, p8, p9)
            count = sum(neighbors)
            transitions = sum((neighbors[index] == 0) & (neighbors[(index + 1) % 8] == 1) for index in range(8))
            if phase == 0:
                condition_a = (p2 * p4 * p6) == 0
                condition_b = (p4 * p6 * p8) == 0
            else:
                condition_a = (p2 * p4 * p8) == 0
                condition_b = (p2 * p6 * p8) == 0
            remove = (center == 1) & (count >= 2) & (count <= 6) & (transitions == 1) & condition_a & condition_b
            if np.any(remove):
                center[remove] = 0
                changed = True
    return image[1:-1, 1:-1].astype(bool)


def point_distance(point: tuple[float, float], start: tuple[float, float], end: tuple[float, float]) -> float:
    sx, sy = start
    ex, ey = end
    px, py = point
    dx, dy = ex - sx, ey - sy
    if dx == 0 and dy == 0:
        return math.hypot(px - sx, py - sy)
    return abs(dy * px - dx * py + ex * sy - ey * sx) / math.hypot(dx, dy)


def simplify(points: list[tuple[int, int]], epsilon: float = 1.08) -> list[tuple[float, float]]:
    converted = [(float(x), float(y)) for y, x in points]
    if len(converted) <= 2:
        return converted

    def rdp(items: list[tuple[float, float]]) -> list[tuple[float, float]]:
        if len(items) <= 2:
            return items
        distances = [point_distance(point, items[0], items[-1]) for point in items[1:-1]]
        maximum = max(distances, default=0)
        if maximum <= epsilon:
            return [items[0], items[-1]]
        index = distances.index(maximum) + 1
        return rdp(items[: index + 1])[:-1] + rdp(items[index:])

    return rdp(converted)


def neighbors(point: tuple[int, int], pixels: set[tuple[int, int]]) -> list[tuple[int, int]]:
    y, x = point
    connected: list[tuple[int, int]] = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if not (dx or dy) or (y + dy, x + dx) not in pixels:
                continue
            # A diagonal next to a cardinal connection is the same visual
            # segment, not a new branch. Pruning that redundant graph edge
            # prevents false junctions and keeps the fitted curves continuous.
            if dx and dy and ((y, x + dx) in pixels or (y + dy, x) in pixels):
                continue
            connected.append((y + dy, x + dx))
    return connected


def trace_paths(skeleton: np.ndarray) -> list[tuple[list[tuple[int, int]], bool]]:
    pixels = set(map(tuple, np.argwhere(skeleton)))
    adjacency = {point: neighbors(point, pixels) for point in pixels}
    nodes = {point for point, connected in adjacency.items() if len(connected) != 2}
    visited: set[frozenset[tuple[int, int]]] = set()
    paths: list[tuple[list[tuple[int, int]], bool]] = []

    def edge(a: tuple[int, int], b: tuple[int, int]) -> frozenset[tuple[int, int]]:
        return frozenset((a, b))

    for start in nodes:
        for next_point in adjacency[start]:
            if edge(start, next_point) in visited:
                continue
            path = [start, next_point]
            visited.add(edge(start, next_point))
            previous, current = start, next_point
            while current not in nodes:
                options = [candidate for candidate in adjacency[current] if candidate != previous]
                if not options:
                    break
                following = options[0]
                visited.add(edge(current, following))
                path.append(following)
                previous, current = current, following
            if len(path) >= 2:
                paths.append((path, False))

    for start in pixels:
        available = [point for point in adjacency[start] if edge(start, point) not in visited]
        if not available:
            continue
        path = [start]
        previous = None
        current = start
        closed = False
        while True:
            options = [point for point in adjacency[current] if point != previous and edge(current, point) not in visited]
            if not options:
                break
            following = options[0]
            visited.add(edge(current, following))
            path.append(following)
            previous, current = current, following
            if current == start:
                closed = True
                break
        if len(path) >= 3:
            paths.append((path, closed))
    return paths


def smooth_path(points: list[tuple[float, float]], closed: bool) -> str:
    if closed and points[0] == points[-1]:
        points = points[:-1]
    if len(points) < 3:
        return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in points)
    if not closed:
        padded = [points[0], *points, points[-1]]
        commands = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
        for index in range(1, len(padded) - 2):
            p0, p1, p2, p3 = padded[index - 1:index + 3]
            # A slightly tighter Catmull-Rom conversion avoids overshoot at
            # cusps and root bifurcations while removing the source pixels'
            # staircase wobble.
            cp1 = (p1[0] + (p2[0] - p0[0]) / 8, p1[1] + (p2[1] - p0[1]) / 8)
            cp2 = (p2[0] - (p3[0] - p1[0]) / 8, p2[1] - (p3[1] - p1[1]) / 8)
            commands.append(f"C {cp1[0]:.2f} {cp1[1]:.2f} {cp2[0]:.2f} {cp2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}")
        return " ".join(commands)

    commands = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]
    length = len(points)
    for index in range(length):
        p0 = points[(index - 1) % length]
        p1 = points[index]
        p2 = points[(index + 1) % length]
        p3 = points[(index + 2) % length]
        cp1 = (p1[0] + (p2[0] - p0[0]) / 8, p1[1] + (p2[1] - p0[1]) / 8)
        cp2 = (p2[0] - (p3[0] - p1[0]) / 8, p2[1] - (p3[1] - p1[1]) / 8)
        commands.append(f"C {cp1[0]:.2f} {cp1[1]:.2f} {cp2[0]:.2f} {cp2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}")
    commands.append("Z")
    return " ".join(commands)


def vectorize(source: Path, destination: Path) -> None:
    rgba = np.asarray(Image.open(source).convert("RGBA"))
    alpha = rgba[:, :, 3]
    mask = remove_small_components(alpha > 54)
    # The supplied upper-profile reference has the six molars vertically
    # inverted relative to the anterior teeth. Normalize that arch so every
    # root points superiorly and every crown faces the occlusal plane.
    is_upper_profile_molar = source.stem.startswith("upper-profile-") and re.search(r"-m[123]$", source.stem)
    if is_upper_profile_molar:
        mask = np.flipud(mask)
    skeleton = skeletonize(mask)
    height, width = mask.shape
    is_profile = "profile" in source.stem
    canvas_width = 112
    canvas_height = 194 if is_profile else 112
    offset_x = (canvas_width - width) / 2
    offset_y = (canvas_height - height) / 2
    path_data: list[str] = []
    for raw_points, closed in trace_paths(skeleton):
        points = simplify(raw_points)
        if len(points) < 2:
            continue
        positioned = [(x + offset_x, y + offset_y) for x, y in points]
        path_data.append(smooth_path(positioned, closed))

    paths = "\n    ".join(f'<path d="{data}"/>' for data in path_data)
    skeleton_pixels = set(map(tuple, np.argwhere(skeleton)))
    junctions = [point for point in skeleton_pixels if len(neighbors(point, skeleton_pixels)) != 2]
    junction_dots = "\n    ".join(
        f'<circle cx="{x + offset_x:.2f}" cy="{y + offset_y:.2f}" r="1.6"/>'
        for y, x in junctions
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
  width="{canvas_width}" height="{canvas_height}"
  viewBox="0 0 {canvas_width} {canvas_height}"
  fill="none" color="#0b6914" shape-rendering="geometricPrecision">
  <g stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">
    {paths}
  </g>
  <g fill="currentColor">{junction_dots}</g>
</svg>\n'''
    destination.write_text(svg, encoding="utf-8")


def main() -> None:
    DESTINATION.mkdir(parents=True, exist_ok=True)
    files = sorted(SOURCE.glob("*.png"))
    if len(files) != 64:
        raise SystemExit(f"Expected 64 source glyphs, found {len(files)}")
    for source in files:
        vectorize(source, DESTINATION / f"{source.stem}.svg")
    print(f"Created {len(files)} SVG glyphs in {DESTINATION}")


if __name__ == "__main__":
    main()
