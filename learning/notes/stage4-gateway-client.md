# 阶段 4：Gateway API、运行时与内嵌 Client

## Gateway 请求流

```
HTTP POST /api/threads/{id}/runs/stream
  → thread_runs.py
  → RunManager.create_run()
  → worker.run_agent() → agent.astream()
  → StreamBridge → SSE 客户端
```

## 关键文件

| 文件 | 职责 |
|------|------|
| `app/gateway/app.py` | FastAPI 入口、路由挂载 |
| `app/gateway/routers/thread_runs.py` | run 生命周期（stream/wait/cancel/join） |
| `runtime/runs/manager.py` | RunManager |
| `runtime/runs/worker.py` | `run_agent()` 驱动 LangGraph |
| `runtime/stream_bridge/` | SSE 解耦、重放、fan-out |
| `client.py` | `DeerFlowClient` 同步内嵌路径 |

## DeerFlowClient vs Gateway

| | Gateway | DeerFlowClient |
|---|---------|----------------|
| 调用方式 | HTTP SSE | 进程内 `agent.stream()` |
| 异步 | async | sync generator |
| 配置 | 同 config.yaml | 同 config.yaml |
| 流式模式 | `values` + `messages` + `custom` | 相同语义 |

## 实验

```bash
# 需有效 API Key
cd backend && PYTHONPATH=.:../learning uv run python ../learning/scripts/stage4_client_stream_demo.py --skip-chat
```

多轮对话需传入 `checkpointer=MemorySaver()`（或 SQLite checkpointer）。

## Checkpoint / 用户隔离

- `runtime/checkpointer/provider.py` — checkpoint 后端
- `runtime/user_context.py` — `get_effective_user_id()`，无鉴权时默认 `"default"`
