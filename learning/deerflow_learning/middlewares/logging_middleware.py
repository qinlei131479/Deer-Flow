"""阶段 2 实验：自定义 AgentMiddleware，在 before_model 阶段记录消息数量。"""

from __future__ import annotations

import logging
from typing import override

from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import BaseMessage

from deerflow.agents.features import Next
from deerflow.agents.middlewares.dangling_tool_call_middleware import DanglingToolCallMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddlewareState(AgentState):
    """与 ThreadState 兼容的最小 state schema。"""

    pass


@Next(DanglingToolCallMiddleware)
class LoggingMiddleware(AgentMiddleware[LoggingMiddlewareState]):
    """在每次调用模型前记录当前消息数量，演示 @Next 插桩定位。"""

    state_schema = LoggingMiddlewareState

    @override
    def before_model(self, state: LoggingMiddlewareState, runtime) -> dict | None:
        messages: list[BaseMessage] = state.get("messages", [])
        logger.info("LoggingMiddleware: before_model, message_count=%d", len(messages))
        return None
