"""Top-level URMLProgram schema.

A URML program is what an LLM emits and what the validator consumes. It
declares the profile(s) it targets, a single root behavior, and an optional
URML version pin for tooling.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from urml_validator.schemas.common import Identifier
from urml_validator.schemas.composition import BehaviorOrStep


class URMLProgram(BaseModel):
    """A complete URML program.

    YAML surface (canonical):

        urml: "0.1"
        profile: home
        behavior:
          type: sequence
          steps:
            - move_to: { location: kitchen }
            - ...

    The `urml` field is optional in the surface YAML but recommended for
    forward compatibility once the spec moves to 1.0.
    """

    model_config = ConfigDict(extra="forbid")

    urml: str = Field("0.1", description="URML spec version this program targets.")
    profile: Identifier | list[Identifier] = Field(
        ..., description="Profile name, or a list when the program straddles multiple profiles."
    )
    behavior: BehaviorOrStep
    description: str | None = None

    @property
    def profiles(self) -> list[Identifier]:
        """Return the program's declared profiles as a list, regardless of YAML form."""
        if isinstance(self.profile, str):
            return [self.profile]
        return list(self.profile)
