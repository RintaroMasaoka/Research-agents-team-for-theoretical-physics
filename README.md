# Research Agents Team for Theoretical Physics

Autonomous research and paper-writing system for theoretical physics projects.

The system is organized like a small research lab: a PI agent drives the project, specialized worker agents handle bounded tasks, and the human user steers direction through meetings. The repository is tool-agnostic at the instruction level, with shared rules in `AGENTS.md`, and currently includes Claude Code-specific configuration under `.claude/`.

## Current Status

This project is useful now, but the validation level is different for `/run` and `/write`.

- As of 2026-03-25, `/run` is the more battle-tested path. In test research sessions, it has been exercised repeatedly at substantial scale, on the order of roughly 200 cycles in total.
- As of 2026-03-25, `/write` is still much less validated. It has not yet been used in a real end-to-end project, so the writing workflow should be treated as experimental and expected to need further iteration.

If you want the most reliable part of the system today, use `/meeting` and `/run` first, and treat `/write` as an early-stage workflow that still needs practical feedback.

## What This Repository Does

- `/meeting` sets or revises the research direction with the user
- `/run [N]` advances the research autonomously for up to `N` cycles
- `/write [N]` turns accumulated research artifacts into paper drafts
- `/improve` is used to refine prompts, workflows, and agent behavior

Core operating model:

- The PI agent owns direction, prioritization, verification, and integration
- Worker agents perform bounded tasks such as reading, research, critique, outlining, reviewing, or simulation
- During `/run` and `/write`, the system is designed to continue without asking the user for clarification

## Quick Start

### Prerequisites

- A compatible coding-agent environment
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) if you want to use the included `.claude/` configuration directly
- [Node.js](https://nodejs.org/) for `configure.mjs`

### Setup

1. Clone the repository
2. Optionally edit `.claude/config/config.yaml`
3. Start your agent session in the project root

If you are using Claude Code, `.claude/settings.json` runs `node configure.mjs` automatically on session start, so generated prompt files stay in sync with the templates and config.

### Minimal Workflow

1. Run `/meeting` to define the topic and direction
2. Run `/run 2` to test a short autonomous research session
3. Inspect generated artifacts such as `project.yaml`, `research/plan.md`, and `logs/last_session.md`
4. Use larger `/run N` sessions once the direction is stable
5. Try `/write 2` only with the understanding that it is currently much less validated than `/run`

## Validation and Expectations

This repository aims to be honest about maturity rather than claiming that all workflows are equally production-ready.

### More validated today

- `/meeting`
- `/run`
- The project-state and research-artifact workflow around `project.yaml`, `research/`, and `logs/`

### Less validated today

- `/write`
- The end-to-end paper assembly loop
- Review and refinement behavior driven by real paper-writing use rather than template design alone

That means the main current value of the repository is autonomous research progression, not yet fully validated autonomous paper production.

## Command Summary

| Command | Purpose | Maturity |
|---|---|---|
| `/meeting` | Interactive progress review and course correction | Usable |
| `/run [N]` | Autonomous research cycles led by the PI | Most validated |
| `/write [N]` | Draft and refine the paper from accumulated artifacts | Experimental |
| `/improve` | Improve prompts, workflows, and behavior | Usable |

## Repository Layout

```text
AGENTS.md                 # Canonical shared instructions for agent behavior
CLAUDE.md                 # Thin wrapper that imports AGENTS.md for Claude Code
README.md                 # Project overview and operational expectations
configure.mjs             # Renders generated prompt files from config + templates

.agents/
└── skills/               # Local skill definitions used by the current environment

.claude/
├── config/config.yaml    # Main editable config
├── templates/            # Prompt templates
├── agents/*.md           # Generated agent instructions
├── skills/*/SKILL.md     # Generated skills
└── settings.json         # Claude Code settings, including SessionStart hook
```

## Runtime Artifacts

During actual research and writing sessions, the project creates working files in the repository root. Typical artifacts include:

- `project.yaml`: central state file for topic, items, and statuses
- `research/plan.md`: current research plan and story arc
- `research/notes/`: PI-owned research notes and contribution assessments
- `research/work/`: worker deliverables produced during `/run`
- `paper/`: outlines, section drafts, and integrated drafts produced during `/write`
- `simulations/`: code, data, and figures for numerical work
- `logs/last_session.md`: handoff summary for the next `/run`
- `logs/last_write_session.md`: handoff summary for the next `/write`

## Configuration

The main editable config is `.claude/config/config.yaml`.

By default, the repository is configured for Japanese user-facing responses.

Current supported top-level values include:

| Key | Meaning |
|---|---|
| `language` | User-facing response language |
| `simulation.language` | Preferred language for simulation code |
| `cycles.run` | Default cycle count for `/run` |
| `cycles.write` | Default cycle count for `/write` |

Prompt content lives in `.claude/templates/`, and generated files are rebuilt from those templates.

Manual commands:

```bash
node configure.mjs
node configure.mjs --dry-run
node configure.mjs --check
```

## Design Constraints

The system is intentionally opinionated.

- During `/run` and `/write`, do not block on user questions
- Keep all writes inside the project directory
- Avoid global installs and other machine-level side effects
- Prefer file-based state and handoff over large prompt-only context
- Track progress honestly; unresolved work should not be marked resolved

These rules are defined canonically in `AGENTS.md`.

## License

MIT
