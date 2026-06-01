"""DeerFlow 学习路径单元测试（阶段 2/3/5 交付物验证）。"""

from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock, patch

from langchain.tools import BaseTool

from deerflow.agents.factory import create_deerflow_agent
from deerflow.agents.features import RuntimeFeatures
from deerflow.reflection import resolve_variable
from deerflow.skills.parser import parse_skill_file
from deerflow.skills.types import SkillCategory

LEARNING_ROOT = Path(__file__).resolve().parents[2] / "learning"
SKILL_PATH = LEARNING_ROOT / "skills" / "deerflow-learning" / "SKILL.md"


# ---------------------------------------------------------------------------
# Stage 3: custom tools
# ---------------------------------------------------------------------------


def test_current_time_tool_returns_iso_utc():
    from deerflow_learning.tools.current_time_tool import current_time_tool

    result = current_time_tool.invoke({})
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", result)


def test_greeting_tool_chinese():
    from deerflow_learning.tools.greeting_tool import greeting_tool

    result = greeting_tool.invoke({"name": "Alice", "language": "zh"})
    assert "Alice" in result
    assert "你好" in result


def test_greeting_tool_english():
    from deerflow_learning.tools.greeting_tool import greeting_tool

    result = greeting_tool.invoke({"name": "Bob", "language": "en"})
    assert "Bob" in result
    assert "Hello" in result


def test_tools_resolve_via_reflection():
    current = resolve_variable("deerflow_learning.tools.current_time_tool:current_time_tool", BaseTool)
    greeting = resolve_variable("deerflow_learning.tools.greeting_tool:greeting_tool", BaseTool)
    assert current.name == "current_time"
    assert greeting.name == "learning_greeting"


# ---------------------------------------------------------------------------
# Stage 2: custom middleware
# ---------------------------------------------------------------------------


@patch("deerflow.agents.factory.create_agent")
def test_logging_middleware_inserts_after_dangling(mock_create_agent):
    from deerflow_learning.middlewares.logging_middleware import LoggingMiddleware

    mock_create_agent.return_value = MagicMock()
    create_deerflow_agent(
        MagicMock(name="model"),
        features=RuntimeFeatures(sandbox=False),
        extra_middleware=[LoggingMiddleware()],
    )
    chain = mock_create_agent.call_args.kwargs["middleware"]
    types = [type(m).__name__ for m in chain]
    assert types.index("LoggingMiddleware") == types.index("DanglingToolCallMiddleware") + 1
    assert types[-1] == "ClarificationMiddleware"


# ---------------------------------------------------------------------------
# Stage 5: skill parsing
# ---------------------------------------------------------------------------


def test_deerflow_learning_skill_parses():
    assert SKILL_PATH.is_file(), f"Missing skill file: {SKILL_PATH}"
    skill = parse_skill_file(SKILL_PATH, SkillCategory.CUSTOM)
    assert skill is not None
    assert skill.name == "deerflow-learning"
    assert "learning" in skill.description.lower()
    assert skill.allowed_tools is not None
    assert "learning_greeting" in skill.allowed_tools


def test_skill_allowed_tools_policy_names():
    from deerflow_learning.tools.current_time_tool import current_time_tool
    from deerflow_learning.tools.greeting_tool import greeting_tool

    from deerflow.skills.tool_policy import filter_tools_by_skill_allowed_tools

    assert SKILL_PATH.is_file()
    skill = parse_skill_file(SKILL_PATH, SkillCategory.CUSTOM)
    assert skill is not None
    tools = [current_time_tool, greeting_tool]
    filtered = filter_tools_by_skill_allowed_tools(tools, [skill])
    names = {t.name for t in filtered}
    assert names == {"current_time", "learning_greeting"}
