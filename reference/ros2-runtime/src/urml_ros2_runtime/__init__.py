"""urml_ros2_runtime — ROS 2 reference runtime for URML.

Public API:

  URMLRuntime(adapter)
    .execute(program, manifest, envelope=None, profiles=()) -> RuntimeResult

  MockROSAdapter()
    Hermetic substrate for tests and development without ROS.

  RclpyAdapter(config=None)
    Real ROS 2 adapter via rclpy. Requires a ROS 2 environment;
    rclpy is imported lazily so this module loads on every host.

  AdapterConfig / load_adapter_config(path)
    Deployment-side config for RclpyAdapter (action-server names,
    perception topics, speech topics, location-to-pose map).

  ROSAdapter
    Protocol every substrate adapter implements.
"""

from __future__ import annotations

from urml_ros2_runtime._version import __version__
from urml_ros2_runtime.bindings import resolve as resolve_reference
from urml_ros2_runtime.bindings import resolve_all as resolve_references
from urml_ros2_runtime.conditions import evaluate as evaluate_condition
from urml_ros2_runtime.errors import (
    ConditionEvalError,
    PrimitiveExecutionError,
    RuntimeError,
    UnresolvedReferenceError,
    UnsupportedCompositionError,
    ValidationRejectedError,
)
from urml_ros2_runtime.primitives import PrimitiveOutcome
from urml_ros2_runtime.runtime import RuntimeResult, URMLRuntime
from urml_ros2_runtime.substrate import (
    AdapterConfig,
    CaptureResult,
    DetectionResult,
    MeasurementResult,
    MockROSAdapter,
    NavigationResult,
    RclpyAdapter,
    ROSAdapter,
    SubstrateResult,
    WaitResult,
    load_adapter_config,
)

__all__ = [
    "AdapterConfig",
    "CaptureResult",
    "ConditionEvalError",
    "DetectionResult",
    "MeasurementResult",
    "MockROSAdapter",
    "NavigationResult",
    "PrimitiveExecutionError",
    "PrimitiveOutcome",
    "ROSAdapter",
    "RclpyAdapter",
    "RuntimeError",
    "RuntimeResult",
    "SubstrateResult",
    "URMLRuntime",
    "UnresolvedReferenceError",
    "UnsupportedCompositionError",
    "ValidationRejectedError",
    "WaitResult",
    "__version__",
    "evaluate_condition",
    "load_adapter_config",
    "resolve_reference",
    "resolve_references",
]
