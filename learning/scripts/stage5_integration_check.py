#!/usr/bin/env python3
"""阶段 5 综合验证：工具挂载、技能解析、中间件链、单元测试一键检查。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND = REPO_ROOT / "backend"
LEARNING = REPO_ROOT / "learning"


def _run_pytest() -> int:
    cmd = [
        "uv",
        "run",
        "pytest",
        "tests/test_learning_path.py",
        "-q",
    ]
    env = {"PYTHONPATH": f".:{LEARNING}"}
    print("=== pytest tests/test_learning_path.py ===")
    result = subprocess.run(cmd, cwd=BACKEND, env={**dict(__import__("os").environ), **env})
    return result.returncode


def _check_tools_in_config() -> bool:
    text = (REPO_ROOT / "config.yaml").read_text(encoding="utf-8")
    ok = "deerflow_learning.tools.current_time_tool" in text
    print(f"=== config.yaml learning tools: {'OK' if ok else 'MISSING'} ===")
    return ok


def _check_skill_installed() -> bool:
    skill = REPO_ROOT / "skills" / "custom" / "deerflow-learning" / "SKILL.md"
    ok = skill.is_file()
    print(f"=== skills/custom/deerflow-learning: {'OK' if ok else 'MISSING'} ===")
    return ok


def main() -> int:
    checks = [_check_tools_in_config(), _check_skill_installed()]
    code = _run_pytest()
    if code != 0:
        return code
    if not all(checks):
        print("\nSome manual setup steps missing — see learning/README.md", file=sys.stderr)
        return 1
    print("\nOK: stage 5 integration check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
