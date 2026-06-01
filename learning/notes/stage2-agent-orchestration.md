# 阶段 2：Agent 编排核心

## 精读文件

| 文件 | 要点 |
|------|------|
| `agents/lead_agent/agent.py` | `make_lead_agent` → 解析 runtime config → 装工具/中间件/prompt → `create_agent` |
| `agents/factory.py` | `create_deerflow_agent` + `RuntimeFeatures` + `@Next/@Prev` 插桩 |
| `agents/thread_state.py` | `ThreadState`：sandbox、artifacts、todos、uploaded_files 等 |
| `agents/lead_agent/prompt.py` | skills/memory/subagent 注入系统提示 |
| `agents/memory/` | queue（防抖）→ updater（LLM 抽取）→ storage（按用户隔离） |

## 中间件链顺序（节选）

```
ThreadData → Uploads → Sandbox → DanglingToolCall → ... → Clarification（永远最后）
```

`ClarificationMiddleware` 必须在链尾：拦截 `ask_clarification` 并 `Command(goto=END)`。

## 实验

```bash
cd backend && PYTHONPATH=.:../learning uv run python ../learning/scripts/stage2_middleware_demo.py
```

示例中间件：`learning/deerflow_learning/middlewares/logging_middleware.py`

- 使用 `@Next(DanglingToolCallMiddleware)` 定位插入点
- 通过 `create_deerflow_agent(..., extra_middleware=[LoggingMiddleware()])` 注入

## 二次开发要点

- 改编排逻辑：优先 `_build_middlewares`（应用层）或 `_assemble_from_features`（SDK 层）
- 自定义 state 字段：扩展 `ThreadState` 并配 reducer
- 不要破坏 Clarification 必须在最后的约束
