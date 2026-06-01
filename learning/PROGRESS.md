# 学习路径执行进度

> 最后更新：自动化验证已完成；Web UI 体验与 LLM 联调需本地手动完成。

## 自动化验证（已通过）

| 项目 | 命令 / 结果 |
|------|-------------|
| 单元测试 7/7 | `cd backend && PYTHONPATH=.:../learning uv run pytest tests/test_learning_path.py -v` |
| 阶段 2 中间件 | `stage2_middleware_demo.py` — LoggingMiddleware 插入链正确 |
| 阶段 5 综合 | `stage5_integration_check.py` — config + skill + pytest |
| 工具挂载 | `get_available_tools()` 含 `current_time`、`learning_greeting`（共 13 个工具） |
| 技能发现 | `deerflow-learning` 在 `skills/custom/` 且 extensions 已启用 |
| Gateway 健康 | `curl http://localhost:8001/health` → 200 |
| DeerFlowClient 流式 | `stage4_client_stream_demo.py --skip-chat` — 管道正常（LLM 连接失败时走错误恢复） |

## 已写入的运行时配置

- `config.yaml`：新增 `utility` 工具组 + 两个学习工具
- `extensions_config.json`：`deerflow-learning` enabled
- `skills/custom/deerflow-learning/SKILL.md`：已安装
- `scripts/serve.sh`：检测到 `learning/deerflow_learning` 时自动 `PYTHONPATH=.:learning`

## 需你本地手动完成

1. **首次 Gateway 鉴权**：访问 http://localhost:8001/setup 创建管理员（API 返回 401 时）
2. **Web UI 全栈**：`make dev` → http://localhost:2026，体验对话 / Plan Mode / 工具 / Artifacts
3. **阶段 1 热重载**：Gateway 运行后执行 `stage1_config_hot_reload.py`
4. **阶段 4 真实 LLM**：修复 `config.yaml` 中模型 API（当前 openai-hk 连接 SSL 错误），再跑完整 `stage4_client_stream_demo.py`

## 建议下一步（按学习计划精读）

1. [notes/stage2-agent-orchestration.md](notes/stage2-agent-orchestration.md) — `make_lead_agent` + 中间件链
2. [notes/stage3-tools-skills.md](notes/stage3-tools-skills.md) — 在 Web UI 问「现在几点」触发 `current_time`
3. [backend/CLAUDE.md](../backend/CLAUDE.md) — 随时查阅的架构索引
