#!/usr/bin/env python3
"""阶段 1 实验：验证 config.yaml 的 mtime 热重载。

用法（Gateway 已启动时）::

    cd backend && uv run python ../learning/scripts/stage1_config_hot_reload.py

脚本会修改 models[0].display_name，调用 GET /api/models 验证变更，然后恢复原值。
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import httpx
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "config.yaml"
GATEWAY_URL = "http://localhost:8001"


def _load_models(config_path: Path) -> list[dict]:
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return data.get("models") or []


def _first_model_name(models: list[dict]) -> str | None:
    for model in models:
        name = model.get("name")
        if name:
            return name
    return None


def _fetch_display_name(client: httpx.Client, model_name: str) -> str | None:
    resp = client.get(f"{GATEWAY_URL}/api/models/{model_name}")
    resp.raise_for_status()
    return resp.json().get("display_name")


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 1: config hot-reload experiment")
    parser.add_argument("--gateway", default=GATEWAY_URL, help="Gateway base URL")
    parser.add_argument("--dry-run", action="store_true", help="Only print current display_name")
    args = parser.parse_args()

    if not CONFIG_PATH.exists():
        print(f"config not found: {CONFIG_PATH}", file=sys.stderr)
        return 1

    models = _load_models(CONFIG_PATH)
    model_name = _first_model_name(models)
    if not model_name:
        print("No models configured in config.yaml", file=sys.stderr)
        return 1

    original_text = CONFIG_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(original_text)
    model_entry = next(m for m in data["models"] if m.get("name") == model_name)
    original_display = model_entry.get("display_name", model_name)
    test_display = f"{original_display} [hot-reload-test]"

    print(f"Model: {model_name}")
    print(f"Original display_name: {original_display}")

    with httpx.Client(base_url=args.gateway, timeout=10.0) as client:
        try:
            before = _fetch_display_name(client, model_name)
            print(f"Gateway before: {before}")
        except httpx.HTTPError as exc:
            print(f"Gateway not reachable ({exc}). Start with: make dev", file=sys.stderr)
            return 1

        if args.dry_run:
            return 0

        model_entry["display_name"] = test_display
        CONFIG_PATH.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        time.sleep(0.5)

        try:
            after = _fetch_display_name(client, model_name)
            print(f"Gateway after edit: {after}")
            if after != test_display:
                print("Hot reload may not have applied yet; retry or check Gateway logs.", file=sys.stderr)
                return 1
            print("OK: display_name hot-reload verified")
        finally:
            CONFIG_PATH.write_text(original_text, encoding="utf-8")
            print("Restored original config.yaml")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
