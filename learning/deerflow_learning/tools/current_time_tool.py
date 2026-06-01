"""阶段 3 实验：自定义工具 — 返回当前 UTC 时间。"""

from datetime import UTC, datetime

from langchain.tools import tool


@tool("current_time", parse_docstring=True)
def current_time_tool() -> str:
    """Return the current UTC date and time in ISO 8601 format.

    Use when the user asks for the current time, date, or timestamp.
    """
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
