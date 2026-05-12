"""urml_ros2_runtime — ROS 2 reference runtime for URML.

Public API:

  URMLRuntime(adapter)
    .execute(program, manifest, envelope=None, profiles=()) -> RuntimeResult

  MockROSAdapter()
    Hermetic substrate for tests and development without ROS.

  ROSAdapter
    Protocol every substrate adapter implements.

The real ``RclpyAdapter`` lands in a follow-up; this skeleton ships the
mock so the runtime can be exercised on any host, with no ROS 2 install.
"""

from __future__ import annotations

from urml_ros2_runtime._version import __version__
from urml_ros2_runtime.conditions import evaluate as evaluate_condition
from urml_ros2_runtime.errors import (
    ConditionEvalError,
    PrimitiveExecutionError,
    RuntimeError,
    UnsupportedCompositionError,
    ValidationRejectedError,
)
from urml_ros2_runtime.primitives import PrimitiveOutcome
from urml_ros2_runtime.runtime import RuntimeResult, URMLRuntime
from urml_ros2_runtime.substrate import (
    CaptureResult,
    DetectionResult,
    MeasurementResult,
    MockROSAdapter,
    NavigationResult,
    ROSAdapter,
    SubstrateResult,
    WaitResult,
)

__all__ = [
    "CaptureResult",
    "ConditionEvalError",
    "DetectionResult",
    "MeasurementResult",
    "MockROSAdapter",
    "NavigationResult",
    "PrimitiveExecutionError",
    "PrimitiveOutcome",
    "ROSAdapter",
    "RuntimeError",
    "RuntimeResult",
    "SubstrateResult",
    "URMLRuntime",
    "UnsupportedCompositionError",
    "ValidationRejectedError",
    "WaitResult",
    "__version__",
    "evaluate_condition",
]
