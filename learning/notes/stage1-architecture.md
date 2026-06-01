# 阶段 1：架构全景与配置系统

## Harness / App 双层

```
backend/packages/harness/deerflow/   → import deerflow.*  （可发布框架）
backend/app/                         → import app.*       （Gateway + IM）
```

**依赖规则**：App → Harness ✅，Harness → App ❌（`test_harness_boundary.py` CI 强制）

## LangGraph 入口

[backend/langgraph.json](../backend/langgraph.json)：

```json
"lead_agent": "deerflow.agents:make_lead_agent"
```

## 配置加载优先级（AppConfig）

1. 显式 `config_path`
2. `DEER_FLOW_CONFIG_PATH`
3. `backend/config.yaml`
4. 项目根 `config.yaml`（推荐）

## 热重载

`get_app_config()` 缓存配置，但当文件 mtime 变化时自动重载。Gateway 读模型列表时会拿到最新值。

## 关键文件

| 文件 | 职责 |
|------|------|
| `config/app_config.py` | AppConfig 主类、mtime 热重载 |
| `config/model_config.py` | ModelConfig schema |
| `config/extensions_config.py` | MCP + Skills 开关 |

## 实验

```bash
# Gateway 运行时
cd backend && uv run python ../learning/scripts/stage1_config_hot_reload.py
```

或 `--dry-run` 仅查看当前 display_name。
