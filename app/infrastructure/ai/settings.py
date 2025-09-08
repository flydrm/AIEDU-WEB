import os
import json
from typing import Any


def load_providers() -> list[dict[str, Any]]:
    env = os.environ.get("AI_PROVIDERS")
    if env:
        try:
            providers = json.loads(env)
            assert isinstance(providers, list)
            return providers
        except Exception:
            pass
    # Fallback single provider via base/url+key
    base_url = os.environ.get("AI_BASE_URL")
    api_key = os.environ.get("AI_API_KEY")
    if base_url and api_key:
        return [{"name": "default", "base_url": base_url, "api_key": api_key, "timeout": 30}]
    return []

