"""Query OpenRouter credit / usage info.

Reads the OpenRouter API key from models.toml (first section whose base_url
points at openrouter.ai) and prints account credits and per-key usage limits.

    uv run python -m eval.openrouter_credits
    uv run python -m eval.openrouter_credits --key sk-or-v1-...   # override
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

API = "https://openrouter.ai/api/v1"
CONFIG = Path(__file__).resolve().parent.parent / "models.toml"


def find_key() -> str:
    cfg = tomllib.loads(CONFIG.read_text())
    for section in cfg.values():
        if not isinstance(section, dict):
            continue
        if "openrouter.ai" in section.get("base_url", "") and section.get("api_key"):
            return section["api_key"]
    sys.exit("no OpenRouter section (base_url containing openrouter.ai) found in models.toml")


def get(path: str, key: str) -> dict:
    req = urllib.request.Request(f"{API}{path}", headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp).get("data", {})
    except urllib.error.HTTPError as e:
        return {"_error": f"{e.code} {e.read().decode(errors='replace')[:200]}"}
    except urllib.error.URLError as e:
        return {"_error": str(e.reason)}


def fmt(x) -> str:
    return f"${x:,.4f}" if isinstance(x, (int, float)) else str(x)


def main() -> None:
    ap = argparse.ArgumentParser(description="Show OpenRouter credits/usage.")
    ap.add_argument("--key", help="OpenRouter API key (default: read from models.toml)")
    args = ap.parse_args()

    key = args.key or find_key()
    print(f"key: ...{key[-6:]}\n")

    credits = get("/credits", key)
    if "_error" in credits:
        print(f"credits: ERROR {credits['_error']}")
    else:
        total = credits.get("total_credits")
        used = credits.get("total_usage")
        print("== account credits ==")
        print(f"  total credits : {fmt(total)}")
        print(f"  total usage   : {fmt(used)}")
        if isinstance(total, (int, float)) and isinstance(used, (int, float)):
            print(f"  remaining     : {fmt(total - used)}")

    info = get("/key", key)
    print("\n== key ==")
    if "_error" in info:
        print(f"  ERROR {info['_error']}")
    else:
        limit = info.get("limit")
        print(f"  label          : {info.get('label')}")
        print(f"  usage          : {fmt(info.get('usage'))}")
        print(f"  limit          : {'unlimited' if limit is None else fmt(limit)}")
        print(f"  limit remaining: {fmt(info.get('limit_remaining')) if info.get('limit_remaining') is not None else '—'}")
        print(f"  free tier      : {info.get('is_free_tier')}")


if __name__ == "__main__":
    main()
