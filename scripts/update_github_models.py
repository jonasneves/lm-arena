#!/usr/bin/env python3
"""
Update models.json with the latest GitHub Models catalog.
Preserves self-hosted model entries.

Usage: python3 scripts/update_github_models.py
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CATALOG_URL = "https://models.github.ai/catalog/models"
MODELS_JSON = Path("app/chat/frontend/public/models.json")


def fetch_github_models() -> list[dict]:
    with urllib.request.urlopen(CATALOG_URL) as response:
        catalog = json.loads(response.read())

    return [
        {
            "id": m["id"],
            "name": m["name"],
            "type": "api",
            "context_length": m.get("limits", {}).get("max_input_tokens", 128000),
            "publisher": m.get("publisher"),
            "summary": m.get("summary"),
            "capabilities": m.get("capabilities", []),
        }
        for m in catalog
        if "streaming" in m.get("capabilities", [])
        and "text" in m.get("supported_output_modalities", [])
    ]


def main() -> None:
    current = json.loads(MODELS_JSON.read_text())
    self_hosted = [m for m in current["models"] if m.get("type") == "self-hosted"]

    github_models = fetch_github_models()
    print(f"Fetched {len(github_models)} GitHub models")

    MODELS_JSON.write_text(
        json.dumps(
            {
                "models": github_models + self_hosted,
                "fetchedAt": datetime.now(timezone.utc).isoformat(),
                "source": "build-time",
            },
            indent=2,
        )
        + "\n"
    )

    print(f"Updated {MODELS_JSON} ({len(github_models)} GitHub + {len(self_hosted)} self-hosted)")


if __name__ == "__main__":
    main()
