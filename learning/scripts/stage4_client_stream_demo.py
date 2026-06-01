#!/usr/bin/env python3
"""阶段 4 实验：DeerFlowClient 多轮对话与流式 delta 演示。

用法::

    cd backend && PYTHONPATH=.:../learning uv run python ../learning/scripts/stage4_client_stream_demo.py

需要 config.yaml 中至少配置一个可用模型与 API Key。
"""

from __future__ import annotations

import argparse
import sys
import uuid

from langgraph.checkpoint.memory import MemorySaver

from deerflow.client import DeerFlowClient


def run_chat_demo(client: DeerFlowClient, thread_id: str) -> None:
    print("\n=== chat() multi-turn demo ===")
    r1 = client.chat("Reply with exactly: TURN-1", thread_id=thread_id)
    print(f"Turn 1: {r1!r}")
    r2 = client.chat("Reply with exactly: TURN-2", thread_id=thread_id)
    print(f"Turn 2: {r2!r}")


def run_stream_demo(client: DeerFlowClient, thread_id: str) -> None:
    print("\n=== stream() delta demo ===")
    chunks: dict[str, list[str]] = {}
    for event in client.stream("Say hello in one short sentence.", thread_id=thread_id):
        if event.type == "messages-tuple" and event.data.get("type") == "ai":
            msg_id = event.data.get("id") or ""
            delta = event.data.get("content", "")
            if delta:
                chunks.setdefault(msg_id, []).append(delta)
                print(f"  delta[{msg_id[:8]}...]: {delta!r}")
        elif event.type == "end":
            print(f"  end usage: {event.data.get('usage')}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-chat", action="store_true", help="Skip multi-turn chat (saves tokens)")
    args = parser.parse_args()

    thread_id = str(uuid.uuid4())
    checkpointer = MemorySaver()
    client = DeerFlowClient(checkpointer=checkpointer)

    models = client.list_models()
    if not models.get("models"):
        print("No models in config.yaml", file=sys.stderr)
        return 1

    print(f"Models: {[m['name'] for m in models['models']]}")
    print(f"Thread: {thread_id}")

    try:
        if not args.skip_chat:
            run_chat_demo(client, thread_id)
        run_stream_demo(client, thread_id)
    except Exception as exc:
        print(f"Demo failed (check API key / model config): {exc}", file=sys.stderr)
        return 1

    print("\nOK: DeerFlowClient demo completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
