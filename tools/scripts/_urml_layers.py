"""Layer and profile data shared between docs-asset generators.

Single source of truth for the layer IDs, titles, and bodies used by the
architecture diagram (``gen_architecture_svg.py``). The hero terminal SVG
does not yet consume this; it is here so a second consumer can be added
without refactoring either generator.

The companion guard test (``reference/validator/tests/test_architecture_svg``
``.py``) asserts every title and body substring appears in
``docs/architecture.md``, catching label drift between the diagram and the
canonical layer document. The em-dash in architecture.md's L0 title is
normalised to a comma before comparison, so the diagram label can follow
the no-em-dash style rule without falsely failing the drift check.
"""

from __future__ import annotations

LAYERS: tuple[tuple[str, str, str], ...] = (
    ("L4", "Natural Language Interface",
     "Documented prompt contract, grammar, examples for LLMs"),
    ("L3", "Behavior Composition",
     "Sequence, branch, parallel, retry, error handling"),
    ("L2", "Intent Primitives",
     "move_to, grasp, hover, scan, detect, dock, ..."),
    ("L1", "Hardware Abstraction",
     "Capabilities, joints, frames, sensors, limits"),
    ("L0", "Substrate (existing OSes, not part of URML)",
     "ROS 2 · PX4 / MAVLink · OPC UA · Autoware · ..."),
)

PROFILES: tuple[str, ...] = ("home", "drone", "industrial", "...")
