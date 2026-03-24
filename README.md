# Research Agents Team for Theoretical Physics — Autonomous Research Paper Generation System

An autonomous system that generates academic papers in theoretical physics with minimal human intervention, powered by [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Overview

This system organizes AI agents into a virtual research lab structure: a **PI (Principal Investigator)** coordinates specialized **student agents** (reader, writer, critic, researcher, simulator, etc.), while the **human user** acts as a collaborating researcher who sets direction and reviews progress.

## Commands

| Command | Description |
|---|---|
| `/run [N]` | Drive the research cycle — the PI assigns tasks to student agents, collects results, and advances the project. Default: 5 cycles |
| `/write [N]` | Draft and refine the academic paper from accumulated research artifacts. Default: 5 cycles |
| `/meeting` | Interactive session for progress review, course correction, and strategic decisions |
| `/improve` | Refine agent prompts and behavior based on observed issues |

## Agent Architecture

```
User (Collaborating Researcher)
  │
  ├── /meeting, /improve   ← interactive dialogue
  │
  └── /run, /write         ← autonomous execution (no user input required)
        │
        PI (Main Agent)
        ├── reader         — literature review and paper analysis
        ├── researcher     — investigate tasks, questions, conjectures
        ├── critic         — independent verification of results
        ├── writer         — draft paper sections
        ├── reviewer       — logical consistency checks
        ├── outliner       — design paper structure
        ├── scout          — discover relevant arXiv papers
        ├── simulator      — numerical computation and visualization
        ├── engine-builder — build reusable simulation modules
        ├── finalizer      — assemble the final paper
        ├── reference-auditor — verify citations
        └── self-check     — check self-containedness
```

## Design Principles

- **Fully autonomous execution**: `/run` and `/write` run without requiring user input, so you can step away while the system works
- **File-based communication**: Agents exchange data through files rather than passing large payloads in prompts, keeping context windows efficient
- **Faithful status tracking**: Research item statuses in `project.yaml` reflect actual progress, so the PI and user always have an accurate picture of the project state
- **Honest reporting**: Agents are designed to report results faithfully — unresolved items are never marked as resolved

## Getting Started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and configured
- [Node.js](https://nodejs.org/) (runs `configure.mjs`, which renders prompt templates from config)

### Setup

1. Clone this repository
2. *(Optional)* Edit `.claude/config/config.yaml` if you want to change the response language, simulation language, or default cycle counts

### Usage

1. Start Claude Code in the project directory — configuration is applied automatically via a session-start hook
2. Use `/meeting` to set a research topic and direction
3. Use `/run` to begin autonomous research cycles
4. Use `/write` to generate the paper

## Project Structure

```
.claude/
├── config/
│   └── config.yaml        # Project configuration (edit this)
├── templates/              # Prompt templates (edit these)
│   ├── CLAUDE.md.tmpl
│   ├── common.md.tmpl
│   ├── agents/             # One template per agent
│   │   ├── reader.md.tmpl
│   │   ├── researcher.md.tmpl
│   │   └── ...
│   └── skills/             # One template per skill
│       ├── run/SKILL.md.tmpl
│       ├── write/SKILL.md.tmpl
│       ├── meeting/SKILL.md.tmpl
│       └── improve/SKILL.md.tmpl
├── CLAUDE.md               # ⚙ Generated — do not edit directly
├── common.md               # ⚙ Generated
├── agents/*.md             # ⚙ Generated
├── skills/*/SKILL.md       # ⚙ Generated
├── settings.json           # Claude Code settings (includes session-start hook)
└── settings.local.json     # Local overrides (not committed)

# Project root
configure.mjs               # Template renderer: config.yaml + templates → .md files
```

### Runtime Artifacts

When you run `/run` and `/write`, the system creates research artifacts in the project root. The central file is `project.yaml`, which tracks all research items (tasks, questions, conjectures, etc.) and their statuses. Other artifacts include literature lists, paper drafts, and simulation outputs.

### Configuration System

To customize prompts, edit the `.tmpl` templates and config values — the generated `.md` files are rebuilt automatically on each session start.

A **SessionStart hook** in `settings.json` runs `configure.mjs` every time Claude Code starts, so users never need to run it manually. To change configuration, update `.claude/config/config.yaml` — changes take effect on the next session.

- **Config values**: `.claude/config/config.yaml`
- **Prompt content**: `.claude/templates/**/*.tmpl`

You can also run it manually:

```bash
node configure.mjs              # Apply all templates
node configure.mjs --dry-run    # Preview changes without writing
node configure.mjs --check      # Validate config and templates
```

## License

MIT
