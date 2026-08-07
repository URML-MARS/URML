"""Speech front-end for the LLM bridge (RFC-0670).

Turns recorded audio into the natural-language text that ``Bridge.translate``
consumes. Mirrors the ``providers/`` layout: a one-method Protocol, per-backend
adapters behind lazy imports, and a hermetic echo provider.

Like the LLM providers, only the Protocol and the hermetic provider are
re-exported here; real adapters are imported from their submodules so the
package imports cleanly without the optional extras.
"""

from urml_llm_bridge.speech.base import SpeechProvider
from urml_llm_bridge.speech.echo import EchoSpeechProvider

__all__ = ["EchoSpeechProvider", "SpeechProvider"]
