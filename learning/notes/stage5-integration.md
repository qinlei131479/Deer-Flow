# 阶段 5：综合实战

## 交付物

| 组件 | 路径 |
|------|------|
| 技能 | `learning/skills/deerflow-learning/SKILL.md` |
| 工具 | `learning_greeting` + `current_time` |
| 中间件 | `LoggingMiddleware`（阶段 2） |
| 测试 | `backend/tests/test_learning_path.py` |

## 启用步骤

```bash
# 1. 工具：合并 config.snippet.yaml 到 config.yaml
# 2. 技能：复制到 skills/custom 并在 extensions_config.json 启用
mkdir -p skills/custom/deerflow-learning
cp -r learning/skills/deerflow-learning/* skills/custom/deerflow-learning/

# 3. 启动（带 learning 包路径）
cd backend && PYTHONPATH=.:../learning make dev

# 4. 跑测试
cd backend && PYTHONPATH=.:../learning uv run pytest tests/test_learning_path.py -v
```

## 验证路径

1. **单元测试**：工具、中间件、技能解析
2. **Gateway**：Web UI 或 `POST /api/threads/{id}/runs/stream`
3. **DeerFlowClient**：`stage4_client_stream_demo.py`

## 前端（按需）

- `frontend/src/core/threads/` — 流式 hooks
- `frontend/src/core/api/` — LangGraph SDK 客户端
- 详见 `frontend/AGENTS.md`

## TDD 约束

参考 `backend/tests/test_client.py::TestGatewayConformance` — Client 返回值需与 Gateway Pydantic schema 一致。
