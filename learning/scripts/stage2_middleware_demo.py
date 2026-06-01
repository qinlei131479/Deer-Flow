#!/usr/bin/env python3
"""阶段 2 实验：用 create_deerflow_agent + extra_middleware 注入 LoggingMiddleware。

用法::

    cd backend && PYTHONPATH=.:../learning uv run python ../learning/scripts/stage2_middleware_demo.py
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

from deerflow.agents.factory import create_deerflow_agent
from deerflow.agents.features import RuntimeFeatures
from deerflow.agents.middlewares.dangling_tool_call_middleware import DanglingToolCallMiddleware

from deerflow_learning.middlewares.logging_middleware import LoggingMiddleware

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")


def main() -> None:
    model = MagicMock(name="mock_model")
    middleware = LoggingMiddleware()

    with patch("deerflow.agents.factory.create_agent") as mock_create:
        mock_create.return_value = MagicMock(name="graph")
        create_deerflow_agent(
            model,
            features=RuntimeFeatures(sandbox=False),
            extra_middleware=[middleware],
        )
        chain = mock_create.call_args.kwargs["middleware"]
        types = [type(m).__name__ for m in chain]
        dangling_idx = types.index("DanglingToolCallMiddleware")
        logging_idx = types.index("LoggingMiddleware")
        assert logging_idx == dangling_idx + 1, f"Expected LoggingMiddleware after DanglingToolCall, got {types}"

    print("OK: LoggingMiddleware inserted via @Next(DanglingToolCallMiddleware)")
    print("Chain snippet:", " -> ".join(types[:5]), "...", types[-1])


if __name__ == "__main__":
    main()
