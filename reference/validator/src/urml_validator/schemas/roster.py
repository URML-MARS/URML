"""Layer-1 — Fleet roster: binding several robots into one addressable fleet.

Added by RFC-0286. A *roster* is the multi-robot analogue of a single
``CapabilityManifest``: it gives each robot in a fleet a short, English-callable
handle (``courier``, ``arm``) and points at that robot's existing per-robot
manifest. The roster does **not** nest or alter a manifest — it binds N
already-valid manifests by name, exactly the way the single-robot path takes one
loaded manifest. ``CapabilityManifest`` is unchanged.

The handle declared here is what a Layer-3 ``on:`` scope node and a ``barrier:``
node address (see ``composition.OnMember`` / ``composition.Barrier``). A fleet
mission is the two-document YAML form::

    roster_version: "0.1"
    members:
      - { name: courier, manifest: husky_amr }
      - { name: arm,     manifest: kawasaki_rs }
    ---
    profile: industrial
    behavior:
      type: sequence
      steps: [ ... ]

Manifest resolution (a registry name vs. a path) is the caller's job, the same
way single-robot loading resolves a manifest before handing the validator a
model. ``validate_fleet`` takes the resolved ``{name -> CapabilityManifest}``.

Schema version: tracks v0.1 (see RFC-0286).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from urml_validator.schemas.common import Identifier


class RosterMember(BaseModel):
    """One robot in a fleet: a handle plus a reference to its manifest.

    ``name`` is the handle a program's ``on:`` / ``barrier:`` nodes use.
    ``manifest`` is an opaque reference (a registry name or a path) the caller
    resolves to a ``CapabilityManifest`` before validation; the roster itself
    never loads it.
    """

    model_config = ConfigDict(extra="forbid")

    name: Identifier = Field(
        ..., description="Fleet-local handle, e.g. 'courier'. Addressed by `on:` / `barrier:`."
    )
    manifest: str = Field(
        ...,
        min_length=1,
        description="Reference to this member's per-robot manifest (registry name or path).",
    )


class FleetRoster(BaseModel):
    """A fleet: an ordered set of uniquely-named members.

    The roster is optional infrastructure — a single-robot program needs none.
    When present it is the binding a fleet program's ``on:`` handles resolve
    against. Member names must be unique (two robots cannot share a handle).
    """

    model_config = ConfigDict(extra="forbid")

    roster_version: str = Field("0.1", description="Roster schema version this fleet targets.")
    members: list[RosterMember] = Field(..., min_length=1)
    description: str | None = None
    shared_frames: list[Identifier] = Field(
        default_factory=list,
        description=(
            "Frame names that denote ONE common physical coordinate reference across "
            "all members (e.g. 'site', 'water', 'agl') — the fleet's shared geodetic "
            "reference, in UTM terms (RFC-0287). The geometric cross-robot collision "
            "check only compares targets whose frame is in this list; a member's own "
            "local frame (e.g. each robot's private 'floor') is never compared against "
            "another's. Empty (default) means the check abstains across members."
        ),
    )

    @model_validator(mode="after")
    def _unique_names(self) -> FleetRoster:
        names = [m.name for m in self.members]
        if len(names) != len(set(names)):
            dupes = sorted({n for n in names if names.count(n) > 1})
            raise ValueError(f"roster has duplicate member name(s): {dupes}")
        if len(self.shared_frames) != len(set(self.shared_frames)):
            dupes = sorted({f for f in self.shared_frames if self.shared_frames.count(f) > 1})
            raise ValueError(f"roster has duplicate shared_frame(s): {dupes}")
        return self

    @property
    def member_names(self) -> set[str]:
        """The set of declared member handles."""
        return {m.name for m in self.members}

    @property
    def shared_frame_set(self) -> set[str]:
        """The set of frames declared as a common physical reference (RFC-0287)."""
        return set(self.shared_frames)
