"""Provider adapters.

Each adapter wraps a single LLM provider behind the LLMProvider Protocol
defined in `base.py`. Adapters are imported lazily — the bridge package
has no hard runtime dependency on any provider SDK. Install the optional
dependency for the provider you want:

    pip install urml-llm-bridge[anthropic]
    pip install urml-llm-bridge[openai]
"""
