# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DeerFlow** (Deep Exploration and Efficient Research Flow) is an open-source AI super agent harness by ByteDance. It orchestrates sub-agents, memory, sandboxes, and tools in a full-stack architecture with a Python backend (LangGraph + FastAPI) and Next.js frontend.

**Key characteristics**:
- Full-stack monorepo with strict backend/frontend separation
- Backend split into publishable harness (`deerflow`) and application layer (`app`)
- Multi-service architecture unified behind nginx on port 2026
- Per-thread isolated execution environments with virtual path system
- Extensive middleware chain (18 middlewares) for agent orchestration

## Quick Start

```bash
# Check prerequisites (Node 22+, Python 3.12+, pnpm 10.26.2+, uv, nginx)
make check

# Install all dependencies (uses Tsinghua PyPI mirror by default)
make install

# Generate config files (first time only)
make config

# Start all services (Gateway + Frontend + Nginx)
make dev

# Access the application
open http://localhost:2026
```

## Common Commands

### Root Directory (Full Application)

| Command | Purpose |
|---------|---------|
| `make check` | Verify system requirements |
| `make install` | Install all dependencies (backend + frontend + pre-commit) |
| `make config` | Generate config files (aborts if exists) |
| `make config-upgrade` | Merge new fields from config.example.yaml |
| `make dev` | Start all services in dev mode (hot-reload) |
| `make stop` | Stop all services |
| `make docker-start` | Start Docker dev services |
| `make up` | Start production Docker services |

### Backend Directory

```bash
cd backend

make install    # Install backend dependencies only
make dev        # Run Gateway API with reload (port 8001)
make test       # Run all tests (277 tests)
make lint       # Lint with ruff
make format     # Format code with ruff
```

**Run a single test**:
```bash
cd backend
PYTHONPATH=. uv run pytest tests/test_<feature>.py -v
```

### Frontend Directory

```bash
cd frontend

pnpm dev              # Dev server (port 3000)
pnpm build            # Production build (requires BETTER_AUTH_SECRET)
pnpm lint             # ESLint
pnpm typecheck        # TypeScript check
pnpm test             # Unit tests (Vitest)
pnpm test:e2e         # E2E tests (Playwright)
```

**Important**: `pnpm build` requires `BETTER_AUTH_SECRET` environment variable:
```bash
BETTER_AUTH_SECRET=local-dev-secret pnpm build
```

## Architecture

### Service Topology

```
Browser → Nginx (2026) ─┬─ /api/langgraph/* → Gateway (8001) [LangGraph Runtime]
                        ├─ /api/*           → Gateway (8001) [REST APIs]
                        └─ /*               → Frontend (3000) [Next.js]
```

### Backend Two-Layer Architecture

**Strict dependency rule**: `app` imports `deerflow`; `deerflow` NEVER imports `app` (enforced by `tests/test_harness_boundary.py`)

1. **Harness** (`backend/packages/harness/deerflow/`)
   - Publishable package: `deerflow-harness`
   - Import prefix: `deerflow.*`
   - Contains: agents, tools, sandbox, models, MCP, skills, config, runtime

2. **App** (`backend/app/`)
   - Unpublishable application code
   - Import prefix: `app.*`
   - Contains: FastAPI Gateway, IM channel integrations

### Agent System

**Entry point**: `deerflow.agents:make_lead_agent` (registered in `langgraph.json`)

**Middleware chain** (18 middlewares in strict order):
1. ThreadDataMiddleware - Per-thread directories
2. UploadsMiddleware - File injection
3. SandboxMiddleware - Sandbox acquisition
4. DanglingToolCallMiddleware - Interrupted tool call handling
5. LLMErrorHandlingMiddleware - Provider failure normalization
6. GuardrailMiddleware - Pre-tool authorization
7. SandboxAuditMiddleware - Security logging
8. ToolErrorHandlingMiddleware - Tool exception conversion
9. SummarizationMiddleware - Context reduction (optional)
10. TodoListMiddleware - Task tracking (optional, plan_mode)
11. TokenUsageMiddleware - Token metrics (optional)
12. TitleMiddleware - Auto thread title
13. MemoryMiddleware - Async memory update
14. ViewImageMiddleware - Image injection (vision models)
15. DeferredToolFilterMiddleware - Tool schema hiding (optional)
16. SubagentLimitMiddleware - Concurrent subagent limit (optional)
17. LoopDetectionMiddleware - Repeated tool-call detection
18. ClarificationMiddleware - Interrupts for clarification (must be last)

### Frontend Architecture

- **Stack**: Next.js 16, React 19, TypeScript 5.8, Tailwind CSS 4
- **Key route**: `/workspace/chats/[thread_id]` (main chat interface)
- **API client**: LangGraph SDK singleton via `getAPIClient()`
- **State management**: TanStack Query (server state) + localStorage (user settings)
- **Streaming**: SSE via `useThreadStream` hook with optimistic updates
- **i18n**: en-US, zh-CN

## Configuration

### Main Config (`config.yaml`)

**Location**: Project root (recommended) or `backend/`

**Priority**:
1. Explicit `config_path` argument
2. `DEER_FLOW_CONFIG_PATH` environment variable
3. `config.yaml` in current directory
4. `config.yaml` in parent directory

**Key sections**:
- `models[]` - LLM configurations with provider-specific settings
- `tools[]` - Tool configurations with reflection-based loading
- `sandbox.use` - Sandbox provider (LocalSandboxProvider or AioSandboxProvider)
- `memory` - Memory system configuration
- `subagents.enabled` - Subagent delegation toggle

**Config versioning**: Run `make config-upgrade` to auto-merge new fields when `config_version` changes.

### Extensions Config (`extensions_config.json`)

**Location**: Project root (recommended) or `backend/`

**Contents**:
- `mcpServers` - MCP server configurations (stdio, SSE, HTTP with OAuth)
- `skills` - Skill enabled/disabled state

## Key Systems

### Sandbox System

**Virtual paths** (agent view):
- `/mnt/user-data/{workspace,uploads,outputs}` - Per-thread user data
- `/mnt/skills` - Skills directory
- `/mnt/acp-workspace` - ACP agent workspace (read-only)

**Physical paths**:
- `backend/.deer-flow/users/{user_id}/threads/{thread_id}/user-data/...`
- `skills/`

**Providers**:
- `LocalSandboxProvider` - Local filesystem with per-thread isolation
- `AioSandboxProvider` - Docker-based isolation

### Memory System

**Storage**: Per-user JSON files at `{base_dir}/users/{user_id}/memory.json`

**Features**:
- LLM-based fact extraction with confidence scores
- Debounced updates (30s default)
- Per-agent per-user isolation
- Automatic injection into system prompt (top 15 facts)

**Migration**: Run `python scripts/migrate_user_isolation.py` to migrate legacy data.

### MCP Integration

- Multi-server support via `langchain-mcp-adapters`
- Lazy initialization with mtime-based cache invalidation
- OAuth support for HTTP/SSE transports
- Runtime updates via Gateway API

### Skills System

**Location**: `skills/{public,custom}/`

**Format**: Directory with `SKILL.md` (YAML frontmatter + markdown content)

**Installation**: `POST /api/skills/install` with .skill ZIP archive

## Development Workflow

### Pre-Commit Validation

**Backend**:
```bash
cd backend
make lint    # ruff check + format check
make test    # 277 tests
```

**Frontend**:
```bash
cd frontend
pnpm lint              # ESLint
pnpm typecheck         # TypeScript
BETTER_AUTH_SECRET=local-dev-secret pnpm build
```

### Test-Driven Development

**Every feature/bugfix MUST include tests**. No exceptions.

- Backend tests: `backend/tests/test_<feature>.py`
- Frontend unit tests: `frontend/tests/unit/`
- Frontend E2E tests: `frontend/tests/e2e/`

### Running Services

**Local development** (recommended):
```bash
make dev              # Foreground with logs
make dev-daemon       # Background
make stop             # Stop all services
```

**Docker development**:
```bash
make docker-start     # Start Docker dev services
make docker-stop      # Stop Docker dev services
make docker-logs      # View logs
```

**Production**:
```bash
make up               # Start production containers
make down             # Stop production containers
```

## Code Style

### Backend (Python)

- **Linter/Formatter**: ruff
- **Line length**: 240 characters
- **Target**: Python 3.12+
- **Quotes**: Double quotes
- **Imports**: First-party: `deerflow`, `app`

### Frontend (TypeScript)

- **Linter**: ESLint (Next.js config)
- **Formatter**: Prettier with Tailwind plugin
- **Path alias**: `@/*` → `src/*`
- **Import ordering**: builtin → external → internal → parent → sibling
- **Unused vars**: Prefix with `_`

## Important Gotchas

1. **PyPI access in China**: Makefile now uses Tsinghua mirror by default. Override with `UV_INDEX_URL=https://pypi.org/simple make install` if needed.

2. **Frontend build**: Requires `BETTER_AUTH_SECRET` environment variable. Use `BETTER_AUTH_SECRET=local-dev-secret` for local builds.

3. **Config location**: `config.yaml` belongs in project root, not `backend/`.

4. **`make config` is non-idempotent**: Aborts if config already exists. Use `make config-upgrade` to merge new fields.

5. **Harness boundary**: `deerflow` package must never import from `app`. Enforced by CI test.

6. **Proxy env vars**: Can break frontend `pnpm install`. Unset if needed.

7. **`pnpm check` is broken**: Use `pnpm lint` + `pnpm typecheck` separately.

## Documentation

### Backend Documentation

See `backend/CLAUDE.md` for detailed backend architecture, and `backend/docs/`:
- `ARCHITECTURE.md` - Detailed architecture
- `API.md` - API reference
- `CONFIGURATION.md` - Configuration options
- `FILE_UPLOAD.md` - File upload system
- `GUARDRAILS.md` - Pre-tool authorization
- `STREAMING.md` - Streaming design
- `summarization.md` - Context summarization
- `plan_mode_usage.md` - TodoList middleware

### Frontend Documentation

See `frontend/CLAUDE.md` for frontend-specific guidance.

### Other Documentation

- `README.md` - User-facing overview and quickstart
- `CONTRIBUTING.md` - Development setup and workflow
- `.github/copilot-instructions.md` - Validated command sequences and gotchas
- `Install.md` - Agent bootstrap instructions

## CI/CD

**Workflows** (`.github/workflows/`):
- `backend-unit-tests.yml` - Backend tests on push/PR
- `frontend-unit-tests.yml` - Frontend tests on push/PR
- `e2e-tests.yml` - E2E tests on frontend changes
- `lint-check.yml` - Lint checks on all PRs
- `container.yaml` - Docker image publishing on tags

**Pre-commit hooks**:
- Backend: `ruff check --fix` + `ruff format`
- Frontend: `eslint --fix` + `prettier --write`

## Troubleshooting

### Network Issues (China)

If you encounter PyPI timeouts:

1. **Makefile already configured**: Uses Tsinghua mirror by default
2. **Manual override**: `UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ make install`
3. **uv config**: Edit `~/.config/uv/uv.toml`:
   ```toml
   [pip]
   index-url = "https://pypi.tuna.tsinghua.edu.cn/simple"
   ```

### Service Won't Start

1. Check if ports are in use: `lsof -i :2026,8001,3000`
2. Stop existing services: `make stop`
3. Check logs: `logs/gateway.log`, `logs/frontend.log`, `logs/nginx.log`
4. Verify config: `make doctor`

### Tests Failing

1. **Backend**: Ensure `config.yaml` exists in project root
2. **Frontend**: Set `SKIP_ENV_VALIDATION=1` or provide required env vars
3. **E2E**: Set `DEER_FLOW_AUTH_DISABLED=true` for test mode

## Related Projects

- **LangGraph**: Agent orchestration framework
- **LangChain**: LLM abstraction layer
- **FastAPI**: Backend web framework
- **Next.js**: Frontend framework
- **Agent Sandbox**: Docker-based isolation (optional)
