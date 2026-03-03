#!/usr/bin/env python3
"""
Collect Cloudflare tunnel tokens and sync to GitHub secret.

For each model: cloudflared tunnel token serverless-llm-<model>
Saves flat {model: token} JSON to tunnels.json and sets TUNNELS_JSON secret.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config.models import get_inference_models


def get_token(model_name: str) -> str:
    result = subprocess.run(
        ["cloudflared", "tunnel", "token", f"serverless-llm-{model_name}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def main() -> None:
    models = get_inference_models()
    tokens: dict[str, str] = {}

    for m in models:
        print(f"  {m.name}...", end=" ", flush=True)
        tokens[m.name] = get_token(m.name)
        print("ok")

    out = Path(__file__).parent.parent / "tunnels.json"
    out.write_text(json.dumps(tokens, indent=2) + "\n")
    print(f"\nSaved {out}")

    result = subprocess.run(
        ["gh", "secret", "set", "TUNNELS_JSON", "-b", json.dumps(tokens)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("Set TUNNELS_JSON secret")


if __name__ == "__main__":
    main()
