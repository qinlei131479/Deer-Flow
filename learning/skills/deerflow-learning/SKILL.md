---
name: deerflow-learning
description: Learning-path demo skill for DeerFlow secondary development. Use when practicing custom skills, tools, and middleware integration. Demonstrates SKILL.md frontmatter and allowed-tools policy.
allowed-tools:
  - learning_greeting
  - current_time
---

# DeerFlow Learning Skill

## Overview

This skill is part of the DeerFlow 2.0 learning path. It demonstrates how a Markdown skill is discovered, parsed, and injected into the agent system prompt.

## When to Use

- User asks to demo the learning path or custom skill integration
- Practicing secondary development on DeerFlow skills/tools/middleware

## Workflow

1. Load this skill when the user wants a greeting demo
2. Call `learning_greeting` with the user's name
3. Optionally call `current_time` to show tool + skill working together

## Tools

| Tool | Purpose |
|------|---------|
| `learning_greeting` | Personalized greeting in zh/en |
| `current_time` | Return current UTC timestamp |
