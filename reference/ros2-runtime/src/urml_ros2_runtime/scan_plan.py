"""Plan a ``scan``: the waypoints a pattern visits over an area, and the coverage they give.

Substrate-neutral: nothing here imports ROS. An adapter that can move to a pose
and take a reading turns a plan into a scan; ``RclpyAdapter`` does it with Nav2
and a camera or sensor topic.

The spec (Layer 2 §2.9) names the patterns but not their geometry. This
module's reading of them:

- ``serpentine``: parallel lanes along the longer side of the area's bounding
  box, alternating direction (a lawnmower), with a sample every ``step`` metres
  along each lane.
- ``grid``: the serpentine lanes, then the area again in lanes at right angles
  (a double grid, the usual photogrammetry pattern), so each sample point is
  seen from two directions.
- ``spiral``: the serpentine's sample points, visited outward from the middle
  of the area in square rings (an expanding-square search).
- ``adaptive`` is not planned here. Adapting means refining around what the
  scan finds, which needs an anomaly detector.

A sample covers a square ``swath`` metres wide. Neighbouring samples and lanes
sit at most ``swath * (1 - overlap)`` apart, spread evenly so the outermost
footprints reach the edges of the bounding box. Every waypoint lies inside the
area polygon: lattice points outside it are dropped. Each waypoint faces the
next one, so the robot turns once per stop instead of to a fixed heading.

Only the waypoints are checked against the polygon. Between two waypoints the
robot follows the path its own planner chooses; in a concave area that path can
cross outside the polygon, so the substrate's keep-out map carries the
geofence.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

Point = tuple[float, float]
Pattern = Literal["serpentine", "spiral", "grid", "adaptive"]

# Coverage is estimated on a raster of at most this many cells over the
# area's bounding box.
_MAX_COVERAGE_CELLS = 40_000
# A point this close to an edge counts as inside the polygon.
_EDGE_EPS = 1e-9


class ScanPlanError(ValueError):
    """The area or the pattern cannot be planned. ``str(exc)`` is ``"<code>: <why>"``."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


@dataclass(frozen=True)
class Region:
    """A named area in the adapter's configuration: its frame and boundary."""

    frame: str
    polygon: tuple[Point, ...]


@dataclass(frozen=True)
class Waypoint:
    """One sampling point: where to stand and which way to face (radians)."""

    x: float
    y: float
    yaw: float


@dataclass(frozen=True)
class ScanPlan:
    """The waypoints a pattern visits over one area, in visiting order."""

    frame: str
    polygon: tuple[Point, ...]
    pattern: str
    swath: float
    step: float
    waypoints: tuple[Waypoint, ...]

    @property
    def area_m2(self) -> float:
        return polygon_area(self.polygon)


def resolve_area(
    area: Mapping[str, Any],
    *,
    regions: Mapping[str, Region],
    default_frame: str,
) -> tuple[str, tuple[Point, ...]]:
    """Turn a scan ``area`` (a polygon, bounding box or named region) into a frame and a polygon.

    ``area`` is the dict the runtime passes (``ScanArea.model_dump``). A literal
    polygon or bounding box carries no frame, so it is read in ``default_frame``;
    a named region carries the frame of its configured boundary.
    """
    if area.get("named_region") is not None:
        name = str(area["named_region"])
        region = regions.get(name)
        if region is None:
            raise ScanPlanError(
                "region_not_configured",
                f"{name!r} is not mapped to a polygon in the adapter configuration",
            )
        return region.frame, _checked_polygon(region.polygon, f"region {name!r}")
    if area.get("bounding_box") is not None:
        box = area["bounding_box"]
        try:
            min_x, max_x = float(box["min_x"]), float(box["max_x"])
            min_y, max_y = float(box["min_y"]), float(box["max_y"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ScanPlanError(
                "area_invalid", "bounding_box needs numeric min_x, max_x, min_y and max_y"
            ) from exc
        if not (min_x < max_x and min_y < max_y):
            raise ScanPlanError("area_invalid", "bounding_box needs min_x < max_x and min_y < max_y")
        corners = ((min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y))
        return default_frame, corners
    if area.get("polygon") is not None:
        vertices = tuple((float(v["x"]), float(v["y"])) for v in area["polygon"])
        return default_frame, _checked_polygon(vertices, "polygon")
    raise ScanPlanError("area_invalid", "area needs one of polygon, bounding_box or named_region")


def plan_scan(
    polygon: Sequence[Point],
    *,
    frame: str,
    pattern: str,
    overlap: float,
    swath: float,
    max_waypoints: int,
) -> ScanPlan:
    """Plan the waypoints for ``pattern`` over ``polygon``."""
    vertices = _checked_polygon(tuple(polygon), "area")
    if pattern == "adaptive":
        raise ScanPlanError(
            "pattern_not_supported",
            "adaptive refines the scan around what it finds, and this adapter has no anomaly detector; "
            "use serpentine, grid or spiral",
        )
    if pattern not in ("serpentine", "grid", "spiral"):
        raise ScanPlanError("pattern_not_supported", f"unknown pattern {pattern!r}")
    if swath <= 0:
        raise ScanPlanError("swath_invalid", f"the sample footprint must be positive, got {swath}")
    if not 0 <= overlap < 1:
        raise ScanPlanError("overlap_invalid", f"overlap must be at least 0 and below 1, got {overlap}")
    step = swath * (1.0 - overlap)

    min_x, min_y, max_x, max_y = _bounds(vertices)
    # Refuse before building a lattice far past the cap (an overlap near 1
    # shrinks the step toward zero): estimate the points inside the polygon
    # from the lattice size and the polygon's share of its bounding box.
    passes = 2 if pattern == "grid" else 1
    share = polygon_area(vertices) / ((max_x - min_x) * (max_y - min_y))
    lattice = _count(max_x - min_x, swath=swath, step=step) * _count(max_y - min_y, swath=swath, step=step)
    estimate = math.ceil(lattice * share) * passes
    if estimate > 2 * max_waypoints:
        raise _too_many(pattern, estimate, max_waypoints, approximate=True)
    xs = _positions(min_x, max_x, swath=swath, step=step)
    ys = _positions(min_y, max_y, swath=swath, step=step)

    along_x = (max_x - min_x) >= (max_y - min_y)
    first = _lanes(vertices, xs, ys, along_x=along_x)
    points: list[Point]
    if pattern == "serpentine":
        points = _serpentine(first)
    elif pattern == "grid":
        points = _serpentine(first)
        second = _serpentine(_lanes(vertices, xs, ys, along_x=not along_x))
        if points and second and _distance(points[-1], second[-1]) < _distance(points[-1], second[0]):
            second.reverse()
        points += second
    else:
        points = _spiral(first, vertices)

    if not points:
        # A sliver narrower than the lattice spacing: stand at its centroid if that is inside.
        centre = _centroid(vertices)
        if not point_in_polygon(centre, vertices):
            raise ScanPlanError("area_too_small", "no sampling point fits inside the area")
        points = [centre]
    if len(points) > max_waypoints:
        raise _too_many(pattern, len(points), max_waypoints, approximate=False)
    return ScanPlan(
        frame=frame,
        polygon=vertices,
        pattern=pattern,
        swath=swath,
        step=step,
        waypoints=_with_headings(points),
    )


def coverage(polygon: Sequence[Point], centres: Sequence[Point], swath: float) -> float:
    """The fraction of ``polygon`` covered by square footprints ``swath`` wide at ``centres``.

    Estimated on a raster over the polygon's bounding box, so it is exact to
    within a cell (a quarter of the swath, or coarser for a large area).
    """
    vertices = tuple(polygon)
    if not centres or swath <= 0:
        return 0.0
    min_x, min_y, max_x, max_y = _bounds(vertices)
    cell = swath / 4.0
    cells_x = math.ceil((max_x - min_x) / cell)
    cells_y = math.ceil((max_y - min_y) / cell)
    if cells_x * cells_y > _MAX_COVERAGE_CELLS:
        cell *= math.sqrt(cells_x * cells_y / _MAX_COVERAGE_CELLS)
        cells_x = math.ceil((max_x - min_x) / cell)
        cells_y = math.ceil((max_y - min_y) / cell)
    inside: set[tuple[int, int]] = set()
    for i in range(cells_x):
        for j in range(cells_y):
            if point_in_polygon((min_x + (i + 0.5) * cell, min_y + (j + 0.5) * cell), vertices):
                inside.add((i, j))
    if not inside:
        return 0.0
    half = swath / 2.0
    covered: set[tuple[int, int]] = set()
    for cx, cy in centres:
        i_lo = max(0, math.floor((cx - half - min_x) / cell))
        i_hi = min(cells_x - 1, math.floor((cx + half - min_x) / cell))
        j_lo = max(0, math.floor((cy - half - min_y) / cell))
        j_hi = min(cells_y - 1, math.floor((cy + half - min_y) / cell))
        for i in range(i_lo, i_hi + 1):
            px = min_x + (i + 0.5) * cell
            if abs(px - cx) > half:
                continue
            for j in range(j_lo, j_hi + 1):
                py = min_y + (j + 0.5) * cell
                if abs(py - cy) <= half and (i, j) in inside:
                    covered.add((i, j))
    return len(covered) / len(inside)


def point_in_polygon(point: Point, polygon: Sequence[Point]) -> bool:
    """True when ``point`` is inside ``polygon`` or on its boundary."""
    x, y = point
    inside = False
    n = len(polygon)
    for k in range(n):
        (x1, y1), (x2, y2) = polygon[k], polygon[(k + 1) % n]
        if _on_segment(point, (x1, y1), (x2, y2)):
            return True
        if (y1 > y) != (y2 > y):
            crossing = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < crossing:
                inside = not inside
    return inside


def polygon_area(polygon: Sequence[Point]) -> float:
    """The polygon's area in square metres (shoelace formula)."""
    n = len(polygon)
    twice = sum(
        polygon[k][0] * polygon[(k + 1) % n][1] - polygon[(k + 1) % n][0] * polygon[k][1] for k in range(n)
    )
    return abs(twice) / 2.0


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _checked_polygon(vertices: tuple[Point, ...], label: str) -> tuple[Point, ...]:
    if len(vertices) < 3:
        raise ScanPlanError("area_invalid", f"{label} needs at least 3 vertices, got {len(vertices)}")
    if polygon_area(vertices) <= 0:
        raise ScanPlanError("area_invalid", f"{label} has no area")
    return vertices


def _bounds(polygon: Sequence[Point]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return min(xs), min(ys), max(xs), max(ys)


def _count(span: float, *, swath: float, step: float) -> int:
    """How many lattice positions ``_positions`` puts across ``span``."""
    if span <= swath:
        return 1
    return math.ceil((span - swath) / step - 1e-9) + 1


def _positions(low: float, high: float, *, swath: float, step: float) -> list[float]:
    """Evenly spread lattice positions between two edges, at most ``step`` apart.

    The first and last sit half a swath in from the edges, so their footprints
    reach them; a span narrower than the swath gets one position in the middle.
    """
    count = _count(high - low, swath=swath, step=step)
    if count == 1:
        return [(low + high) / 2.0]
    first, last = low + swath / 2.0, high - swath / 2.0
    return [first + (last - first) * k / (count - 1) for k in range(count)]


def _too_many(pattern: str, count: int, maximum: int, *, approximate: bool) -> ScanPlanError:
    needs = f"about {count}" if approximate else str(count)
    return ScanPlanError(
        "too_many_waypoints",
        f"the {pattern} pattern needs {needs} waypoints, more than the configured maximum of {maximum}; "
        "widen scan.swath_m to the sensor's real footprint, lower the overlap, raise "
        "scan.max_waypoints, or scan a smaller area",
    )


def _lanes(polygon: tuple[Point, ...], xs: list[float], ys: list[float], *, along_x: bool) -> list[list[Point]]:
    """The lattice as lanes: lanes run along x when ``along_x``, else along y. Points outside are dropped."""
    lanes: list[list[Point]] = []
    if along_x:
        for y in ys:
            lane = [(x, y) for x in xs if point_in_polygon((x, y), polygon)]
            if lane:
                lanes.append(lane)
    else:
        for x in xs:
            lane = [(x, y) for y in ys if point_in_polygon((x, y), polygon)]
            if lane:
                lanes.append(lane)
    return lanes


def _serpentine(lanes: list[list[Point]]) -> list[Point]:
    points: list[Point] = []
    for index, lane in enumerate(lanes):
        points.extend(lane if index % 2 == 0 else reversed(lane))
    return points


def _spiral(lanes: list[list[Point]], polygon: tuple[Point, ...]) -> list[Point]:
    """The lattice points in expanding square rings around the one nearest the area's middle."""
    points = [p for lane in lanes for p in lane]
    if not points:
        return []
    xs = sorted({p[0] for p in points})
    ys = sorted({p[1] for p in points})
    column = {x: i for i, x in enumerate(xs)}
    row = {y: j for j, y in enumerate(ys)}
    centre = _centroid(polygon)
    start = min(points, key=lambda p: (_distance(p, centre), p))
    ci, cj = column[start[0]], row[start[1]]

    def key(p: Point) -> tuple[int, float]:
        di, dj = column[p[0]] - ci, row[p[1]] - cj
        ring = max(abs(di), abs(dj))
        # Counter-clockwise from the east side of each ring.
        angle = math.atan2(dj, di) % (2 * math.pi)
        return ring, angle

    return sorted(points, key=key)


def _with_headings(points: list[Point]) -> tuple[Waypoint, ...]:
    """Face each waypoint toward the next; the last keeps the heading it arrived with."""
    waypoints: list[Waypoint] = []
    yaw = 0.0
    for k, (x, y) in enumerate(points):
        if k + 1 < len(points):
            nx, ny = points[k + 1]
            if (nx, ny) != (x, y):
                yaw = math.atan2(ny - y, nx - x)
        waypoints.append(Waypoint(x=x, y=y, yaw=yaw))
    return tuple(waypoints)


def _centroid(polygon: Sequence[Point]) -> Point:
    n = len(polygon)
    twice = 0.0
    cx = cy = 0.0
    for k in range(n):
        (x1, y1), (x2, y2) = polygon[k], polygon[(k + 1) % n]
        cross = x1 * y2 - x2 * y1
        twice += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    if abs(twice) < _EDGE_EPS:
        return (sum(p[0] for p in polygon) / n, sum(p[1] for p in polygon) / n)
    return (cx / (3 * twice), cy / (3 * twice))


def _distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _on_segment(p: Point, a: Point, b: Point) -> bool:
    (px, py), (ax, ay), (bx, by) = p, a, b
    cross = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
    if abs(cross) > _EDGE_EPS * max(1.0, _distance(a, b)):
        return False
    within_x = min(ax, bx) - _EDGE_EPS <= px <= max(ax, bx) + _EDGE_EPS
    within_y = min(ay, by) - _EDGE_EPS <= py <= max(ay, by) + _EDGE_EPS
    return within_x and within_y
