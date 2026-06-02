"""Single source of truth for `__version__`.

Kept in its own module so the package's submodules can import the version
string without triggering circular imports through `__init__.py`.
"""

from __future__ import annotations

__version__: str = "0.2.0"
