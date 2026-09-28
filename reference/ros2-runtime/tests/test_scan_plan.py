"""The scan planner: which waypoints a pattern visits over an area, and what they cover.

Pure geometry, no ROS. The adapter tests (test_rclpy_adapter.py) cover driving
the plan; these pin the plan itself: every waypoint inside the area, spacing no
wider than the swath and overlap allow, and each pattern's visiting order.
"""

from __future__ import annotations

import math
import time

import pytest

from urml_ros2_runtime.scan_plan import (
    Region,
    ScanPlanError,
    coverage,
    plan_scan,
    point_in_polygon,
    polygon_area,
    resolve_area,
)

SQUARE = ((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))
# An L: a 4 x 1 bar along x and a 1 x 4 bar along y, sharing the corner at the origin.
L_SHAPE = ((0.0, 0.0), (4.0, 0.0), (4.0, 1.0), (1.0, 1.0), (1.0, 4.0), (0.0, 4.0))


def _plan(polygon: tuple[tuple[float, float], ...] = SQUARE, **overrides: object):  # type: ignore[no-untyped-def]
    call: dict[str, object] = {
        "frame": "map",
        "pattern": "serpentine",
        "overlap": 0.3,
        "swath": 1.0,
        "max_waypoints": 500,
    }
    call.update(overrides)
    return plan_scan(polygon, **call)  # type: ignore[arg-type]


def _xy(plan) -> list[tuple[float, float]]:  # type: ignore[no-untyped-def]
    return [(round(w.x, 3), round(w.y, 3)) for w in plan.waypoints]


def test_serpentine_is_a_lawnmower_over_the_area() -> None:
    assert _xy(_plan()) == [
        (0.5, 0.5), (1.0, 0.5), (1.5, 0.5),
        (1.5, 1.0), (1.0, 1.0), (0.5, 1.0),
        (0.5, 1.5), (1.0, 1.5), (1.5, 1.5),
    ]  # fmt: skip


def test_lanes_run_along_the_longer_side() -> None:
    tall = ((0.0, 0.0), (1.0, 0.0), (1.0, 3.0), (0.0, 3.0))
    xs = {x for x, _ in _xy(_plan(tall, overlap=0.0))}
    assert xs == {0.5}  # one lane up the middle, along y


def test_grid_crosses_the_serpentine_at_right_angles() -> None:
    serpentine = _xy(_plan(overlap=0.0))
    grid = _xy(_plan(overlap=0.0, pattern="grid"))
    assert len(grid) == 2 * len(serpentine)
    assert grid[: len(serpentine)] == serpentine
    # The second pass sees the same points, in lanes along y.
    assert sorted(grid[len(serpentine) :]) == sorted(serpentine)
    assert grid[len(serpentine)][0] == grid[len(serpentine) + 1][0]


def test_spiral_expands_from_the_middle() -> None:
    points = _xy(_plan(pattern="spiral"))
    assert points[0] == (1.0, 1.0)
    rings = [max(abs(x - 1.0), abs(y - 1.0)) for x, y in points]
    assert rings == sorted(rings)
    assert sorted(points) == sorted(_xy(_plan()))


@pytest.mark.parametrize("pattern", ["serpentine", "grid", "spiral"])
def test_every_waypoint_is_inside_a_concave_area(pattern: str) -> None:
    plan = _plan(L_SHAPE, pattern=pattern, overlap=0.0, swath=0.5)
    assert plan.waypoints
    assert all(point_in_polygon((w.x, w.y), L_SHAPE) for w in plan.waypoints)
    # The notch (x, y > 1) holds no waypoint.
    assert not any(w.x > 1.0 and w.y > 1.0 for w in plan.waypoints)


@pytest.mark.parametrize("overlap", [0.0, 0.3, 0.6])
def test_neighbours_are_never_further_apart_than_the_step(overlap: float) -> None:
    plan = _plan(((0.0, 0.0), (7.3, 0.0), (7.3, 2.9), (0.0, 2.9)), overlap=overlap)
    step = 1.0 * (1 - overlap)
    xs = sorted({w.x for w in plan.waypoints})
    ys = sorted({w.y for w in plan.waypoints})
    for axis in (xs, ys):
        gaps = [b - a for a, b in zip(axis, axis[1:], strict=False)]
        assert all(gap <= step + 1e-9 for gap in gaps)
    # The outermost footprints reach the edges.
    assert xs[0] - 0.5 == pytest.approx(0.0) and xs[-1] + 0.5 == pytest.approx(7.3)
    assert plan.step == pytest.approx(step)


def test_each_waypoint_faces_the_next() -> None:
    plan = _plan(overlap=0.0)
    headings = [round(math.degrees(w.yaw)) for w in plan.waypoints]
    # (0.5,0.5) -> (1.5,0.5) -> (1.5,1.5) -> (0.5,1.5); the last keeps the heading it arrived with.
    assert headings == [0, 90, 180, 180]


def test_a_full_plan_covers_the_area_and_a_missing_sample_shows() -> None:
    plan = _plan(overlap=0.0)
    centres = [(w.x, w.y) for w in plan.waypoints]
    assert coverage(SQUARE, centres, 1.0) == 1.0
    assert coverage(SQUARE, centres[:3], 1.0) == 0.75
    assert coverage(SQUARE, [], 1.0) == 0.0


def test_a_sliver_gets_one_waypoint_at_its_middle() -> None:
    sliver = ((0.0, 0.0), (0.4, 0.0), (0.4, 0.3), (0.0, 0.3))
    assert _xy(_plan(sliver)) == [(0.2, 0.15)]


@pytest.mark.parametrize(
    ("overrides", "code"),
    [
        ({"pattern": "adaptive"}, "pattern_not_supported"),
        ({"pattern": "zigzag"}, "pattern_not_supported"),
        ({"overlap": 1.0}, "overlap_invalid"),
        ({"overlap": -0.1}, "overlap_invalid"),
        ({"swath": 0.0}, "swath_invalid"),
        ({"max_waypoints": 8}, "too_many_waypoints"),
    ],
)
def test_unplannable_requests_are_refused(overrides: dict[str, object], code: str) -> None:
    with pytest.raises(ScanPlanError) as caught:
        _plan(**overrides)
    assert caught.value.code == code
    assert str(caught.value).startswith(f"{code}: ")


def test_a_near_total_overlap_is_refused_without_building_the_lattice() -> None:
    """An overlap of 0.9999 over a 1 km field would be ~10^14 points; the estimate refuses it at once."""
    field = ((0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0), (0.0, 1000.0))
    started = time.perf_counter()
    with pytest.raises(ScanPlanError) as caught:
        _plan(field, overlap=0.9999)
    assert caught.value.code == "too_many_waypoints"
    assert "about" in str(caught.value)
    assert time.perf_counter() - started < 1.0


def test_resolve_area_reads_each_form() -> None:
    box = {"bounding_box": {"min_x": 1, "max_x": 3, "min_y": 0, "max_y": 2}}
    assert resolve_area(box, regions={}, default_frame="map") == (
        "map",
        ((1.0, 0.0), (3.0, 0.0), (3.0, 2.0), (1.0, 2.0)),
    )
    polygon = {"polygon": [{"x": 0, "y": 0}, {"x": 2, "y": 0}, {"x": 0, "y": 2}]}
    frame, vertices = resolve_area(polygon, regions={}, default_frame="site")
    assert frame == "site" and polygon_area(vertices) == 2.0
    region = {"named_region": "bed_a"}
    regions = {"bed_a": Region(frame="garden", polygon=SQUARE)}
    assert resolve_area(region, regions=regions, default_frame="map") == ("garden", SQUARE)


@pytest.mark.parametrize(
    ("area", "code"),
    [
        ({"named_region": "nowhere"}, "region_not_configured"),
        ({"bounding_box": {"min_x": 2, "max_x": 1, "min_y": 0, "max_y": 1}}, "area_invalid"),
        ({"bounding_box": {"min_x": 0, "max_x": 1}}, "area_invalid"),
        ({"polygon": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}, "area_invalid"),
        ({"polygon": [{"x": 0, "y": 0}, {"x": 1, "y": 1}, {"x": 2, "y": 2}]}, "area_invalid"),
        ({}, "area_invalid"),
    ],
)
def test_resolve_area_refuses_what_it_cannot_plan(area: dict[str, object], code: str) -> None:
    with pytest.raises(ScanPlanError) as caught:
        resolve_area(area, regions={}, default_frame="map")
    assert caught.value.code == code
