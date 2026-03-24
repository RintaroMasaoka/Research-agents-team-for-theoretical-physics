# Research Agents Team for Theoretical Physics — Autonomous Research Paper Generation System

An autonomous system that generates academic papers in theoretical physics with minimal human intervention, powered by [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Overview

This system organizes AI agents into a virtual research lab structure: a **PI (Principal Investigator)** coordinates specialized **student agents** (reader, writer, critic, researcher, simulator, etc.), while the **human user** acts as a collaborating researcher who sets direction and reviews progress.

## Commands

| Command | Description |
|---|---|
| `/run` | Drive the research cycle — the PI assigns tasks to student agents, collects results, and advances the project |
| `/write` | Draft and refine the academic paper from accumulated research artifacts |
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
- **Structured research tracking**: Research items are managed in `project.yaml` with typed kinds (task, question, conjecture, etc.) and statuses
- **Honest reporting**: Agents are designed to report results faithfully — unresolved items are never marked as resolved

## Getting Started

### Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed and configured

### Usage

1. Clone this repository
2. Open the project directory in your terminal
3. Start Claude Code
4. Use `/meeting` to set a research topic and direction
5. Use `/run` to begin autonomous research cycles
6. Use `/write` to generate the paper

## Project Structure

```
.claude/
├── CLAUDE.md          # Project instructions and roles
├── common.md          # Shared rules for all agents
├── settings.json      # Claude Code configuration
├── agents/            # Agent definitions (one per .md file)
│   ├── reader.md
│   ├── researcher.md
│   ├── critic.md
│   ├── writer.md
│   ├── reviewer.md
│   ├── outliner.md
│   ├── scout.md
│   ├── simulator.md
│   ├── engine-builder.md
│   ├── finalizer.md
│   ├── reference_auditor.md
│   └── self-check.md
└── skills/            # Slash command definitions
    ├── run/
    ├── write/
    ├── meeting/
    └── improve/
```

## License

MIT
