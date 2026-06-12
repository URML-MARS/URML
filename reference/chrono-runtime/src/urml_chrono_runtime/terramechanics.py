"""TerramechanicsScene — a rig on Chrono SCM deformable terrain.

The bundled Chrono::Vehicle terramechanics scene the runtime's status note
flagged as a follow-up, and the richer evidence Project Chrono lead Dan Negrut
pointed at on `projectchrono/chrono` issue #746: contact forces, sinkage, and a
tip-stability margin, exercised over a *deformable* terrain model rather than a
bare rigid `ChSystem`.

The role is unchanged from the rest of the runtime (RFC-0328): URML validates a
program statically against the capability manifest and the safety envelope
*first*, then drives the same validated intent through this scene so the
high-fidelity dynamics come back as evidence. The scene is selected by the
manifest's `validation.terrain_fidelity: deformable` hint (RFC-0381), mirrored
into `ChronoConfig.terrain_fidelity`; URML never models the soil itself, it only
declares the fidelity it expects and reads back what Chrono computed.

## What is verified where

The URML-side wiring — selecting the deformable scene from the config, driving
the rig with the resolved driver segment, and shaping sinkage / contact force /
tip margin into the validation-evidence payload — is exercised hermetically by
the committed unit suite against a fake `pychrono` (the technique the rest of the
runtime uses). The live SCM construction against a real PyChrono build is the
documented **calibration step** (the px4 / mujoco / opcua convention): the exact
SCM getter surface is version-sensitive, so each physics read is wrapped and
degrades to an honest ``unavailable`` note rather than crashing, and the pinned
scene is verified in ``chrono-integration.yml``'s ``chrono-sitl-e2e`` job.
"""

from __future__ import annotations

import math
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TerramechanicsParams(BaseModel):
    """Soil + rig parameters for the SCM deformable-terrain scene.

    Bekker-Wong pressure-sinkage plus Janosi-Hanamoto shear, the standard SCM
    (Soil Contact Model) parameter set. Defaults approximate a soft sandy loam.
    These are model- and deployment-specific, so they live in adapter config
    (``chrono_adapter.yaml``), never in the URML program, manifest, or envelope.
    """

    model_config = ConfigDict(extra="forbid")

    terrain_length_m: float = Field(default=4.0, gt=0.0)
    terrain_width_m: float = Field(default=2.0, gt=0.0)
    mesh_resolution_m: float = Field(default=0.04, gt=0.0)
    rig_mass_kg: float = Field(default=250.0, gt=0.0)
    tip_threshold_deg: float = Field(
        default=35.0,
        gt=0.0,
        description="Roll/pitch angle past which the rig is treated as unstable (tip margin = threshold - |tilt|).",
    )
    drawbar_gain_n: float = Field(
        default=1500.0,
        ge=0.0,
        description="Forward force per unit of driver[0] (throttle) applied to the rig, N.",
    )
    # Bekker-Wong / Janosi soil parameters (SCM).
    bekker_kphi: float = Field(default=0.2e6, description="Bekker frictional modulus k_phi, Pa/m^n.")
    bekker_kc: float = Field(default=0.0, description="Bekker cohesive modulus k_c, Pa/m^(n-1).")
    bekker_n: float = Field(default=1.1, gt=0.0, description="Bekker sinkage exponent n.")
    mohr_cohesion_pa: float = Field(default=0.0, ge=0.0, description="Mohr-Coulomb cohesion, Pa.")
    mohr_friction_deg: float = Field(default=30.0, description="Mohr-Coulomb internal friction angle, deg.")
    janosi_shear_m: float = Field(default=0.01, gt=0.0, description="Janosi-Hanamoto shear deformation modulus, m.")


def _unavailable(reason: str) -> dict[str, Any]:
    return {"value": None, "note": f"unavailable: {reason}"}


class TerramechanicsScene:
    """A rigid rig resting on an SCM deformable-terrain patch, via ``pychrono``.

    Holds a cached ``ChSystemSMC`` (SCM contact requires the smooth/penalty
    method), an SCM terrain patch, and a rigid rig body. ``advance`` applies the
    driver and steps both; ``evidence`` reads sinkage, the peak contact force,
    and the tip-stability margin. The scene is built lazily by the adapter only
    when ``ChronoConfig.scene == "terramechanics"``.
    """

    TERRAIN_MODEL = "scm_deformable"

    def __init__(self, chrono: Any, params: TerramechanicsParams) -> None:
        self._ch = chrono
        self._p = params
        self._veh = self._import_vehicle()
        self.system: Any = chrono.ChSystemSMC()
        self._terrain: Any = None
        self._rig: Any = None
        self._rig_z0: float = 0.0
        self._notes: list[str] = []
        self._build()

    def _import_vehicle(self) -> Any:
        """Resolve the ``pychrono.vehicle`` module (attribute first, then import)."""
        veh = getattr(self._ch, "vehicle", None)
        if veh is not None:
            return veh
        try:
            import pychrono.vehicle as veh  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:  # pragma: no cover - calibration-only path
            raise RuntimeError(
                "pychrono.vehicle is required for the terramechanics scene.\n"
                "  It ships with PyChrono from conda-forge: conda install -c conda-forge pychrono"
            ) from exc
        return veh

    # ------------------------------------------------------------------
    # Construction (calibration-gated against a real PyChrono build)
    # ------------------------------------------------------------------

    def _build(self) -> None:
        p = self._p
        terrain = self._veh.SCMTerrain(self.system)
        terrain.SetSoilParameters(
            p.bekker_kphi,
            p.bekker_kc,
            p.bekker_n,
            p.mohr_cohesion_pa,
            p.mohr_friction_deg,
            p.janosi_shear_m,
        )
        terrain.Initialize(p.terrain_length_m, p.terrain_width_m, p.mesh_resolution_m)
        self._terrain = terrain

        rig = self._ch.ChBody()
        rig.SetMass(p.rig_mass_kg)
        self.system.AddBody(rig)
        self._rig = rig
        self._rig_z0 = self._body_z(rig)

    # ------------------------------------------------------------------
    # Stepping
    # ------------------------------------------------------------------

    def advance(self, step_size: float, steps: int, driver: list[float] | None = None) -> None:
        if driver:
            self._apply_driver(driver)
        for _ in range(max(1, steps)):
            self._advance_terrain(step_size)
            self.system.DoStepDynamics(step_size)

    def _apply_driver(self, driver: list[float]) -> None:
        """Apply driver[0] (throttle) as a forward drawbar force on the rig."""
        force = float(driver[0]) * self._p.drawbar_gain_n
        try:
            self._rig.EmptyAccumulators()
            self._rig.AccumulateForce(
                self._ch.ChVector3d(force, 0.0, 0.0), self._rig.GetPos(), False
            )
        except Exception as exc:  # pragma: no cover - calibration-only path
            self._note(f"driver_force {type(exc).__name__}")

    def _advance_terrain(self, step_size: float) -> None:
        try:
            self._terrain.Advance(step_size)
        except Exception as exc:  # pragma: no cover - calibration-only path
            self._note(f"terrain_advance {type(exc).__name__}")

    # ------------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------------

    def evidence(self) -> dict[str, Any]:
        """Richer terramechanics evidence for the validation payload."""
        ev: dict[str, Any] = {
            "terrain_model": self.TERRAIN_MODEL,
            "sinkage_m": self._sinkage_m(),
            "max_contact_force_n": self._max_contact_force_n(),
            "tip_margin_deg": self._tip_margin_deg(),
        }
        if self._notes:
            ev["terramechanics_notes"] = list(self._notes)
        return ev

    def _sinkage_m(self) -> float | None:
        try:
            return max(0.0, self._rig_z0 - self._body_z(self._rig))
        except Exception as exc:  # pragma: no cover - calibration-only path
            self._note(f"sinkage {type(exc).__name__}")
            return None

    def _max_contact_force_n(self) -> float | None:
        try:
            f = self._terrain.GetContactForceBody(self._rig)
            return float(f.Length())
        except Exception as exc:  # pragma: no cover - calibration-only path
            self._note(f"contact_force {type(exc).__name__}")
            return None

    def _tip_margin_deg(self) -> float | None:
        try:
            roll, pitch = self._rig_roll_pitch_deg()
            return self._p.tip_threshold_deg - max(abs(roll), abs(pitch))
        except Exception as exc:  # pragma: no cover - calibration-only path
            self._note(f"tip_margin {type(exc).__name__}")
            return None

    # ------------------------------------------------------------------
    # Small physics reads
    # ------------------------------------------------------------------

    def _body_z(self, body: Any) -> float:
        return float(body.GetPos().z)

    def _rig_roll_pitch_deg(self) -> tuple[float, float]:
        """Roll and pitch of the rig from its orientation quaternion, in degrees."""
        q = self._rig.GetRot()
        w, x, y, z = float(q.e0), float(q.e1), float(q.e2), float(q.e3)
        # Standard quaternion -> roll (x) / pitch (y), ZYX convention.
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        sin_pitch = max(-1.0, min(1.0, 2.0 * (w * y - z * x)))
        pitch = math.asin(sin_pitch)
        return math.degrees(roll), math.degrees(pitch)

    def _note(self, msg: str) -> None:
        if msg not in self._notes:
            self._notes.append(msg)
