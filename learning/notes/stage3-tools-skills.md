# 阶段 3：工具 / 技能 / MCP / 子代理 / 沙箱

## 工具装配

入口：`deerflow/tools/tools.py` → `get_available_tools()`

组装顺序：

1. `config.yaml` 中 `tools[]`（`use: module:var` 经 `resolve_variable` 加载）
2. MCP 工具（懒加载 + mtime 缓存失效）
3. Builtins：`present_files`、`ask_clarification`、`view_image`（条件）、`task`（subagent 开启时）
4. 社区工具：Tavily、Jina、Firecrawl、DDG 等

## 标准工具定义

```python
from langchain.tools import tool

@tool("tool_name", parse_docstring=True)
def my_tool(arg: str) -> str:
    """Docstring becomes tool description."""
    return result
```

## 沙箱

- 抽象：`sandbox/sandbox.py`
- 工具：`sandbox/tools.py` — bash/ls/read_file/write_file/str_replace
- 虚拟路径：`/mnt/user-data/{workspace,uploads,outputs}`

## 子代理

- `subagents/executor.py` — `task()` 后台线程池执行
- `subagents/registry.py` — 内置 general-purpose、bash
- 并发：`SubagentLimitMiddleware` 截断超额 `task` 调用

## 技能

- 格式：`skills/{public,custom}/<name>/SKILL.md`（YAML frontmatter）
- 解析：`skills/parser.py`；存储/安装：`skills/storage/skill_storage.py`

## 实验

1. 合并 [config.snippet.yaml](../config.snippet.yaml) 到 `config.yaml`
2. 启动时 `PYTHONPATH=.:../learning make dev`
3. 对话中问「现在几点」触发 `current_time` 工具

单元测试：`pytest tests/test_learning_path.py -k current_time`
