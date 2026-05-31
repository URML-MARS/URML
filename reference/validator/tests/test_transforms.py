"""RFC-0288 — SE(3) transform math + frame-graph validation."""

from __future__ import annotations

import math

from urml_validator import ErrorCode, validate
from urml_validator.schemas.common import Rotation, Transform, Translation
from urml_validator.schemas.manifest import Frame
from urml_validator.transforms import (
    apply,
    compose,
    frame_to_root,
    invert,
    rigid_of,
    rpy_to_matrix,
    transform_point_between,
)


def _close(a, b, tol=1e-9):
    return all(abs(x - y) < tol for x, y in zip(a, b))


# ---------------------------------------------------------------------------
# Rotation + rigid-transform math
# ---------------------------------------------------------------------------


def test_identity_rotation():
    r = rpy_to_matrix(0.0, 0.0, 0.0)
    assert _close(r[0], (1.0, 0.0, 0.0))
    assert _close(r[1], (0.0, 1.0, 0.0))
    assert _close(r[2], (0.0, 0.0, 1.0))


def test_yaw_90_rotates_x_to_y():
    t = Transform(rotation=Rotation(yaw=math.pi / 2))
    assert _close(apply(rigid_of(t), (1.0, 0.0, 0.0)), (0.0, 1.0, 0.0))


def test_translation_only():
    t = Transform(translation=Translation(x=2.0, y=-3.0, z=1.0))
    assert _close(apply(rigid_of(t), (1.0, 1.0, 1.0)), (3.0, -2.0, 2.0))


def test_invert_round_trips():
    t = rigid_of(Transform(translation=Translation(x=5.0, y=2.0, z=-1.0), rotation=Rotation(roll=0.3, pitch=-0.7, yaw=1.1)))
    p = (1.5, -2.5, 0.5)
    assert _close(apply(invert(t), apply(t, p)), p)


def test_compose_is_apply_b_then_a():
    a = rigid_of(Transform(translation=Translation(x=1.0)))
    b = rigid_of(Transform(rotation=Rotation(yaw=math.pi / 2)))
    # compose(a, b): rotate then translate. (1,0,0) --yaw90--> (0,1,0) --+x1--> (1,1,0)
    assert _close(apply(compose(a, b), (1.0, 0.0, 0.0)), (1.0, 1.0, 0.0))


# ---------------------------------------------------------------------------
# Frame-graph resolution
# ---------------------------------------------------------------------------


def _frames(*frames):
    return {f.name: f for f in frames}


def test_transform_point_between_same_frame_is_identity():
    frames = _frames(Frame(name="site"))
    assert transform_point_between((1.0, 2.0, 3.0), "site", "site", frames) == (1.0, 2.0, 3.0)


def test_transform_point_child_to_parent():
    # base_link is at (10, 0, 0) in site, yawed 90 degrees.
    frames = _frames(
        Frame(name="site"),
        Frame(
            name="base_link",
            parent="site",
            transform=Transform(translation=Translation(x=10.0), rotation=Rotation(yaw=math.pi / 2)),
        ),
    )
    # A point 1m ahead of base_link (its +x) is at site (10, 1, 0).
    got = transform_point_between((1.0, 0.0, 0.0), "base_link", "site", frames)
    assert got is not None and _close(got, (10.0, 1.0, 0.0))
    # And back the other way.
    back = transform_point_between((10.0, 1.0, 0.0), "site", "base_link", frames)
    assert back is not None and _close(back, (1.0, 0.0, 0.0))


def test_disconnected_frames_resolve_to_none():
    frames = _frames(Frame(name="site"), Frame(name="water"))  # two roots, no link
    assert transform_point_between((0.0, 0.0, 0.0), "site", "water", frames) is None


def test_missing_transform_on_chain_is_none():
    # base_link has a parent but no transform -> not numerically related.
    frames = _frames(Frame(name="site"), Frame(name="base_link", parent="site"))
    assert transform_point_between((0.0, 0.0, 0.0), "base_link", "site", frames) is None


def test_frame_to_root_reports_root():
    frames = _frames(
        Frame(name="site"),
        Frame(name="base_link", parent="site", transform=Transform()),
        Frame(name="sensor", parent="base_link", transform=Transform(translation=Translation(z=0.5))),
    )
    result = frame_to_root("sensor", frames)
    assert result is not None
    _, root = result
    assert root == "site"


# ---------------------------------------------------------------------------
# Frame-graph validation (via validate)
# ---------------------------------------------------------------------------

_MINIMAL_PROGRAM = {
    "profile": "home",
    "behavior": {"report": {"to": "user", "facts": {"ok": True}}},
}


def _manifest_with_frames(frames):
    return {"robot_id": "r", "frames": frames}


def test_valid_frame_tree_accepted():
    manifest = _manifest_with_frames([
        {"name": "site"},
        {"name": "base_link", "parent": "site", "transform": {"translation": {"x": 1.0}}},
    ])
    result = validate(_MINIMAL_PROGRAM, manifest, policy=None)
    assert not result.has(ErrorCode.CAPABILITY_FRAME_PARENT_UNDECLARED)
    assert not result.has(ErrorCode.CAPABILITY_FRAME_CYCLE)


def test_undeclared_parent_rejected():
    manifest = _manifest_with_frames([{"name": "base_link", "parent": "ghost_frame"}])
    result = validate(_MINIMAL_PROGRAM, manifest, policy=None)
    assert result.has(ErrorCode.CAPABILITY_FRAME_PARENT_UNDECLARED)


def test_frame_cycle_rejected():
    manifest = _manifest_with_frames([
        {"name": "a", "parent": "b", "transform": {}},
        {"name": "b", "parent": "a", "transform": {}},
    ])
    result = validate(_MINIMAL_PROGRAM, manifest, policy=None)
    assert result.has(ErrorCode.CAPABILITY_FRAME_CYCLE)


# ---------------------------------------------------------------------------
# Single-robot geofence cross-frame resolution (RFC-0288)
# ---------------------------------------------------------------------------

# base_link sits at site (10, 0, 0); a 0..20 box geofence is declared in `site`.
_CROSS_FRAME_MANIFEST = {
    "robot_id": "rover",
    "frames": [
        {"name": "site"},
        {"name": "base_link", "parent": "site", "transform": {"translation": {"x": 10.0}}},
    ],
    "mobility": {"drive_type": "differential", "max_velocity": 1.0},
}
_BOX_ENVELOPE = {
    "geofences": [
        {"name": "box", "frame": "site", "vertices": [[0.0, -5.0], [20.0, -5.0], [20.0, 5.0], [0.0, 5.0]]}
    ]
}


def _move_to_pose(x):
    return {
        "profile": "home",
        "behavior": {"move_to": {"pose": {"x": x, "y": 0.0}, "frame": "base_link"}},
    }


def test_geofence_cross_frame_inside_accepted():
    # base_link (1,0) -> site (11,0), inside the box.
    result = validate(_move_to_pose(1.0), _CROSS_FRAME_MANIFEST, _BOX_ENVELOPE, policy=None)
    assert not result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)


def test_geofence_cross_frame_outside_rejected():
    # base_link (15,0) -> site (25,0), outside the box.
    result = validate(_move_to_pose(15.0), _CROSS_FRAME_MANIFEST, _BOX_ENVELOPE, policy=None)
    assert result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)


def test_geofence_no_transform_abstains():
    # Same setup but base_link has no transform -> not resolvable -> geofence
    # abstains -> no violation (backward-compatible with pre-RFC-0288).
    manifest = {
        "robot_id": "rover",
        "frames": [{"name": "site"}, {"name": "base_link", "parent": "site"}],
        "mobility": {"drive_type": "differential", "max_velocity": 1.0},
    }
    result = validate(_move_to_pose(15.0), manifest, _BOX_ENVELOPE, policy=None)
    assert not result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)
