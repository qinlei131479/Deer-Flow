"""阶段 5 实验：与 deerflow-learning 技能配套的问候工具。"""

from langchain.tools import tool


@tool("learning_greeting", parse_docstring=True)
def greeting_tool(name: str, language: str = "zh") -> str:
    """Generate a personalized greeting for learning-path demos.

    Args:
        name: The person's name to greet.
        language: Language code, ``zh`` for Chinese or ``en`` for English.
    """
    if language == "en":
        return f"Hello, {name}! Welcome to DeerFlow learning path."
    return f"你好，{name}！欢迎学习 DeerFlow 二次开发。"
