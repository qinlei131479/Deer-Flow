# DeerFlow 2.0 源码学习路径 — 动手实验与笔记

本目录对应学习计划各阶段的可运行交付物，**不修改**框架核心代码。

## 目录结构

```
learning/
├── README.md                          # 本文件
├── config.snippet.yaml                # 挂载自定义工具的 config 片段
├── deerflow_learning/                 # 可 import 的示例包（PYTHONPATH=learning）
│   ├── middlewares/logging_middleware.py
│   └── tools/{current_time,greeting}_tool.py
├── skills/deerflow-learning/SKILL.md  # 阶段 5 示例技能
├── scripts/                           # 各阶段实验脚本
└── notes/                             # 各阶段精读笔记
```

## 快速开始

```bash
# 阶段 0：环境检查 + 测试基线
make check
cd backend && make test

# 阶段 1：配置热重载（需 Gateway 运行: make dev）
cd backend && uv run python ../learning/scripts/stage1_config_hot_reload.py --dry-run

# 阶段 2：中间件注入
cd backend && PYTHONPATH=.:../learning uv run python ../learning/scripts/stage2_middleware_demo.py

# 阶段 3/5：学习路径单元测试
cd backend && PYTHONPATH=.:../learning uv run pytest tests/test_learning_path.py -v

# 阶段 4：DeerFlowClient 流式演示（需有效模型 API Key）
cd backend && PYTHONPATH=.:../learning uv run python ../learning/scripts/stage4_client_stream_demo.py --skip-chat
```

## 挂载自定义工具到 Agent

将 [config.snippet.yaml](config.snippet.yaml) 中的 `tools` 条目合并到项目根 `config.yaml`，
并确保 `tool_groups` 含 `utility` 组（或改用已有组名）。

## 启用示例技能

```bash
mkdir -p skills/custom/deerflow-learning
cp -r learning/skills/deerflow-learning/* skills/custom/deerflow-learning/

# 在 extensions_config.json 中启用
# "skills": { "deerflow-learning": { "enabled": true } }
```

## 核心心智模型

DeerFlow Agent = `create_agent(model, tools, middleware, system_prompt, state_schema)`

| 能力 | 入口文件 |
|------|----------|
| 应用工厂 | `backend/packages/harness/deerflow/agents/lead_agent/agent.py` → `make_lead_agent` |
| SDK 工厂 | `backend/packages/harness/deerflow/agents/factory.py` → `create_deerflow_agent` |
| 工具装配 | `backend/packages/harness/deerflow/tools/tools.py` → `get_available_tools` |
| 内嵌 Client | `backend/packages/harness/deerflow/client.py` → `DeerFlowClient` |
| Gateway | `backend/app/gateway/app.py` + `routers/thread_runs.py` |

## 架构约束

- **Harness** (`deerflow.*`) 永不 import **App** (`app.*`)
- 框架能力放 harness，API/渠道放 app
- 每个功能改动需配 `backend/tests/test_*.py`（TDD）

详细笔记见 [notes/](notes/) 目录。执行进度见 [PROGRESS.md](PROGRESS.md)。

## 注意事项

- Gateway 首次启动需访问 `/setup` 创建管理员，否则 `/api/*` 返回 401
- `make dev` 已自动将 `learning/` 加入 Gateway 的 PYTHONPATH（见 `scripts/serve.sh`）
- 阶段 4 演示需 `config.yaml` 中配置可用的模型 API Key
