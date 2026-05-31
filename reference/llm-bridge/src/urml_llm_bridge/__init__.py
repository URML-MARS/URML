"""urml_llm_bridge — provider-agnostic glue from natural language to validated URML.

Public API:

  Bridge(provider, manifest, envelope=None, profiles=(), max_revisions=3)
    .translate(user_request: str) -> TranslateResult

  EchoProvider(responses: dict[str, str])
    A hermetic provider for testing, with no network.

Bring your own provider by implementing LLMProvider.complete(). Real
adapters for Anthropic and OpenAI live under `urml_llm_bridge.providers`
and are imported lazily so the bridge has no hard dependency on either
SDK.
"""

from __future__ import annotations

from urml_llm_bridge._version import __version__
from urml_llm_bridge.bridge import Bridge, FleetBridge, TranslateResult
from urml_llm_bridge.errors import (
    BridgeError,
    BridgePolicyViolation,
    BridgeRevisionExhausted,
    ProviderError,
)
from urml_llm_bridge.few_shot import (
    FewShot,
    default_few_shots,
    drone_few_shots,
    few_shots_for,
    fleet_few_shots,
    home_few_shots,
    industrial_few_shots,
)
from urml_llm_bridge.prompt import build_fleet_system_prompt, build_system_prompt
from urml_llm_bridge.providers.base import LLMProvider
from urml_llm_bridge.providers.echo import EchoProvider

__all__ = [
    "Bridge",
    "BridgeError",
    "BridgePolicyViolation",
    "BridgeRevisionExhausted",
    "EchoProvider",
    "FewShot",
    "FleetBridge",
    "LLMProvider",
    "ProviderError",
    "TranslateResult",
    "__version__",
    "build_fleet_system_prompt",
    "build_system_prompt",
    "default_few_shots",
    "drone_few_shots",
    "few_shots_for",
    "fleet_few_shots",
    "home_few_shots",
    "industrial_few_shots",
]
