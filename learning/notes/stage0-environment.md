# 阶段 0：环境跑通

## 检查清单

- [x] `make check` — Node 22+、pnpm、uv、nginx
- [x] `config.yaml` 已存在（项目根）
- [x] 学习工具已写入 config.yaml（current_time、learning_greeting）
- [x] 技能已安装至 skills/custom/deerflow-learning
- [ ] `make dev` → http://localhost:2026（需手动启动体验 Web UI）
- [ ] Web UI：普通对话、Plan Mode、工具调用、Artifacts
- [x] `tests/test_learning_path.py` — 7/7 通过（见 learning/PROGRESS.md）

## 端口

| 服务 | 端口 |
|------|------|
| Nginx 统一入口 | 2026 |
| Gateway | 8001 |
| Frontend | 3000 |

## 常用命令

```bash
make setup      # 交互向导（新环境推荐）
make install    # uv sync + pnpm install
make dev        # 全栈开发
make stop       # 停止服务
cd backend && make test
```

## 实验

运行 `cd backend && make test` 确认测试基线通过。
