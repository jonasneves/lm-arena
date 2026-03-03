#!/usr/bin/env python3
"""
Get tunnel token for a model from tunnels.json or TUNNELS_JSON env var.

Usage:
    python scripts/get_tunnel_token.py <model>
    TUNNELS_JSON='{"qwen": "token..."}' python scripts/get_tunnel_token.py qwen
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def load(s: str) -> dict:
    try:
        return json.loads(s)
    except Exception:
        return {}


def get_token(data: dict, model: str) -> str | None:
    entry = data.get(model)
    if isinstance(entry, str):
        return entry or None
    if isinstance(entry, dict):  # backward compat with nested format
        token = entry.get("tunnel_token", "")
        return token or None
    return None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: get_tunnel_token.py <model> [--silent]", file=sys.stderr)
        sys.exit(1)

    model = sys.argv[1]
    silent = "--silent" in sys.argv

    data: dict = {}
    env_json = os.environ.get("TUNNELS_JSON", "")
    if env_json:
        data = load(env_json)
    else:
        for path in [Path("tunnels.json"), Path(__file__).parent.parent / "tunnels.json"]:
            if path.exists():
                data = load(path.read_text())
                break

    token = get_token(data, model)
    if token:
        print(token)
    else:
        if not silent:
            print(f"Error: No tunnel token for '{model}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
