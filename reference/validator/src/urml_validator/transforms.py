"""SE(3) rigid-body transform math + a frame-graph resolver (RFC-0288).

Pure Python (no numpy) so the validator keeps minimal dependencies. A rigid
transform is a ``(R, t)`` pair: a 3x3 rotation matrix and a 3-vector translation.
A point ``p`` maps as ``R @ p + t``.

The resolver walks a manifest's frame graph (the ``Frame.parent`` chain, now
carrying a ``Frame.transform`` per RFC-0288) to express a point declared in one
frame in terms of another. Frames that are not connected, or a chain with a
missing transform, resolve to ``None`` — the caller then abstains, preserving the
pre-RFC-0288 behavior (frames were compared only by string-equal name).
"""

from __future__ import annotations

import math
from collections.abc import Mapping

from urml_validator.schemas.common import Transform
from urml_validator.schemas.manifest import Frame

Mat = tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]
Vec = tuple[float, float, float]
Rigid = tuple[Mat, Vec]

IDENTITY: Rigid = (((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), (0.0, 0.0, 0.0))


def rpy_to_matrix(roll: float, pitch: float, yaw: float) -> Mat:
    """Roll/pitch/yaw (radians) -> rotation matrix, ZYX: R = Rz(yaw)·Ry(pitch)·Rx(roll)."""
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )


def _matmul(a: Mat, b: Mat) -> Mat:
    return tuple(  # type: ignore[return-value]
        tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3)
    )


def _matvec(a: Mat, v: Vec) -> Vec:
    return tuple(sum(a[i][k] * v[k] for k in range(3)) for i in range(3))  # type: ignore[return-value]


def _transpose(a: Mat) -> Mat:
    return tuple(tuple(a[j][i] for j in range(3)) for i in range(3))  # type: ignore[return-value]


def _vadd(u: Vec, v: Vec) -> Vec:
    return (u[0] + v[0], u[1] + v[1], u[2] + v[2])


def _vneg(v: Vec) -> Vec:
    return (-v[0], -v[1], -v[2])


def rigid_of(transform: Transform) -> Rigid:
    """A `Transform` schema model -> a `(R, t)` rigid transform."""
    r = rpy_to_matrix(transform.rotation.roll, transform.rotation.pitch, transform.rotation.yaw)
    t = (transform.translation.x, transform.translation.y, transform.translation.z)
    return (r, t)


def compose(a: Rigid, b: Rigid) -> Rigid:
    """``a ∘ b`` — apply ``b`` then ``a``: ``(Ra·Rb, Ra·tb + ta)``."""
    ra, ta = a
    rb, tb = b
    return (_matmul(ra, rb), _vadd(_matvec(ra, tb), ta))


def invert(a: Rigid) -> Rigid:
    """The inverse rigid transform: ``(Rᵀ, -Rᵀ·t)``."""
    r, t = a
    rt = _transpose(r)
    return (rt, _vneg(_matvec(rt, t)))


def apply(a: Rigid, p: Vec) -> Vec:
    """Map point ``p`` by the transform: ``R·p + t``."""
    r, t = a
    return _vadd(_matvec(r, p), t)


def frame_to_root(frame_name: str, frames: Mapping[str, Frame]) -> tuple[Rigid, str] | None:
    """The transform mapping a point in ``frame_name`` to its root frame, and the
    root's name. ``None`` if a frame is unknown, a needed `transform` is missing,
    a declared `parent` is absent, or the chain contains a cycle."""
    current = frames.get(frame_name)
    if current is None:
        return None
    result: Rigid = IDENTITY
    seen: set[str] = set()
    while current.parent is not None:
        if current.name in seen:
            return None  # cycle
        seen.add(current.name)
        if current.transform is None:
            return None  # parent declared but no numeric transform — cannot compose
        result = compose(rigid_of(current.transform), result)
        parent = frames.get(current.parent)
        if parent is None:
            return None  # undeclared parent
        current = parent
    return (result, current.name)


def transform_point_between(
    point: Vec, src: str, dst: str, frames: Mapping[str, Frame]
) -> Vec | None:
    """Express ``point`` (declared in frame ``src``) in frame ``dst``.

    ``None`` when the two frames are not connected in one tree, or a transform on
    the path is missing. Same frame -> the point unchanged.
    """
    if src == dst:
        return point
    s = frame_to_root(src, frames)
    d = frame_to_root(dst, frames)
    if s is None or d is None:
        return None
    (t_src_root, root_src), (t_dst_root, root_dst) = s, d
    if root_src != root_dst:
        return None  # different trees — no common reference
    # src -> dst  =  invert(dst -> root) ∘ (src -> root)
    return apply(compose(invert(t_dst_root), t_src_root), point)
