# Research Agents Team for Theoretical Physics

Autonomous research-paper generation system for theoretical physics projects.
This file is written to be compatible with both Codex-style and Claude-style coding agents.
This file is the canonical shared instruction source for the repository.
If `CLAUDE.md` exists, it should import this file rather than duplicating its contents.

## Purpose

The system advances research and paper writing with minimal human intervention.

- `/run` advances research
- `/write` drafts and refines the paper
- `/meeting` is used for progress review and course correction with the user
- `/improve` is used to improve agent prompts, workflows, and behavior

## Configuration

- User-facing responses must be in Japanese
- Prefer model-agnostic wording in prompts and operational rules
- Tool-specific names may appear as examples, but the underlying intent takes precedence

## Role Mapping

| Term | Entity | Responsibility |
|---|---|---|
| **PI** | The main agent running `/run` or `/write` | Owns research direction, decides priorities, delegates work, verifies outputs, and integrates accepted results |
| **Students** | Sub-agents / worker agents such as reader, writer, critic, researcher | Execute bounded tasks under PI direction. Their output is provisional until PI verifies and adopts it |
| **User** | Human researcher | Sets direction through `/meeting`, reviews progress, and overrides PI decisions when needed |

## Cross-Tool Interpretation

Interpret the following operationally rather than literally:

- "Do not ask the user" includes any interactive clarification request, approval request, or blocking permission prompt
- Claude-specific tools such as `AskUserQuestion` and Codex-specific mechanisms such as approval-gated escalations are examples of the same prohibited behavior during autonomous runs
- "Sub-agent" means any delegated worker/task agent provided by the current environment

## Operational Rules

- During `/run` and `/write`, do not request user input in any form. This includes clarification questions, approval prompts, permission-escalation requests, and any other interaction that would block autonomous execution
- `/meeting` and `/improve` are the only places where active user interaction should normally occur
- If a task cannot be completed during `/run` or `/write` without asking the user, choose a project-local alternative, defer that action, or record the limitation in the session output instead of interrupting the user
- Do not write outside the project directory
- Do not pollute the global environment. Avoid global installs, global config changes, and side effects outside this repository
- Prefer reproducible, workspace-local changes so the project remains portable across agent environments

## Priority of These Rules

When working in this repository, these rules govern agent behavior regardless of whether the runtime is Codex, Claude Code, or another similar coding agent. If tool names differ across environments, follow the intent of the rule rather than the surface syntax.
