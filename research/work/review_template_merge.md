# Template Merge Review: simulator.md.tmpl / engine-builder.md.tmpl / run/SKILL.md.tmpl

## Verdict: FAIL

## Review Summary

The merge is largely well-executed, with consistent archive directory structures and coherent new sections (Results Directory Management, Note Curation, Refinement pass). However, there are two major issues: (1) a naming conflict between `README.md` and `REPORT.md` within the simulator template, and (2) a contradiction between the simulator's Design step (which encourages extending existing scripts) and its Implementation step (which says to write a single new script). There is also a notable cross-file inconsistency where the run SKILL uses a new status system (`stable`/`closed`) that conflicts with `common.md.tmpl` and several agent templates still using the old system (`resolved`/`partial`/`reframed`/`dropped`), though this extends beyond the three target files.

## Detailed Findings

### A. simulator.md.tmpl

#### [MAJOR-1] README.md vs REPORT.md naming conflict

The Results Directory Management section (line 41) introduces:

> `**README.md**: Every results directory contains a README listing all files with one-line descriptions, the physical setup that produced the data, and the command(s) to reproduce the results`

But section 6 "Results README" (line 108) instructs:

> `Write results/{slug}/REPORT.md — a self-contained explanation of this simulation...`

~~**`README.md`**~~: Every results directory contains a README... [* Should be `REPORT.md` to match section 6, or section 6 should be changed to `README.md`. Choose one name and use it consistently. The origin/main version used `REPORT.md` in the directory structure comment, suggesting `REPORT.md` is the intended name.]

Additionally, the functional overlap is problematic: the `README.md` description in Results Directory Management (file listing, physical setup, reproduction commands) substantially overlaps with the REPORT.md content specification in section 6 (overview, figures, data reliability, reproduction). These appear to be the same file described under two names with partially overlapping scope.

**Fix**: Unify to a single filename (likely `REPORT.md` for continuity with origin/main). Merge the Results Directory Management's content expectations into section 6, or explicitly differentiate their roles if two separate files are intended.

#### [MAJOR-2] Contradiction between Design (extend existing) and Implementation (write single new)

Section 1 Design (line 51) says:

> Extend an existing script rather than creating a new file when possible

Section 2 Implementation (line 58) says:

> Write a single script `src/{slug}.{ext}`, verifying and improving it with Edit.

The origin/main version of section 2 handled this correctly: "Write or extend a script in `src/`. If extending an existing script (per section 1), use Edit; if creating a new one, write `src/{slug}.{ext}`." The experiment branch simplified this and lost the "extend" path.

**Fix**: Restore the origin/main phrasing for section 2 to maintain consistency with the Design step's "extend existing" instruction. Something like: "Write or extend a script in `src/` (per the decision made in section 1). The script loads modules from `lib/` and implements only the measurement logic."

#### [MINOR-1] Plot script extension changed to template variable without constraint update

Origin/main had `src/{slug}_plot.py` (always Python/matplotlib) with a constraint "Do not add dependencies beyond matplotlib and numpy to plot scripts." The experiment version changed to `src/{slug}_plot.{ext}` using `{{ simulation.visualization }}`, which is a good generalization, but the corresponding constraint about matplotlib/numpy was removed (line 149 area) without replacing it with an equivalent constraint for the configured visualization backend.

This is minor because the constraint removal may be intentional (the backend is now configurable, so hard-coding matplotlib/numpy restrictions would be wrong). But consider whether a generic constraint like "Minimize plot script dependencies; rely on the configured visualization backend" is warranted.

#### [MINOR-2] Deliverable structure changed without backward-compatible mapping

The origin/main had a 9-item numbered deliverable structure (Task, Modules Used, Measurement Logic, etc.). The experiment version replaced this with a narrative-oriented 6-item structure (Setup, Method, Verification, Results, Conclusions, Appendix) plus writing principles. This is an improvement in quality but a breaking change for any existing deliverables or tooling that expected the old structure.

This is minor for the template review itself but worth noting for migration awareness.

### B. engine-builder.md.tmpl

The engine-builder merge is **identical** to the origin/main version -- the diff shows zero changes. All improvements listed in the merge summary (Role update, Startup Reading expansion, "Evolve, don't duplicate" principle, Refinement pass, etc.) are already present on origin/main. This means:

#### [INFO] No actual merge occurred for engine-builder.md.tmpl

The experiment branch version is identical to origin/main. This is not an issue per se -- it means the origin/main version was adopted as-is, which is valid if the experiment branch had no independent changes to this file.

### C. run/SKILL.md.tmpl

#### [MAJOR-3] Status system mismatch with common.md.tmpl and agent templates

The run SKILL uses a new status system:

| New (run SKILL) | Old (common.md.tmpl, researcher, critic, writer, meeting) |
|---|---|
| `stable` | `resolved` / `partial` |
| `closed` | `reframed` / `dropped` |

`common.md.tmpl` line 5 still says: `status (open, active, partial, resolved, reframed, dropped)`

Agent templates that reference the old system:
- `researcher.md.tmpl` line 118: "Status assessment for the item: resolved / partial / open / reframed / dropped"
- `critic.md.tmpl` line 76: "Does the claimed status (resolved / partial, etc.) match the actual argumentation?"
- `writer.md.tmpl` lines 25-31: All `(resolved)` references for item kinds
- `meeting/SKILL.md.tmpl` lines 83-84: "resolved: {N} items", "partial: {N} items"

While updating these files is outside the scope of the three target files, this creates operational inconsistency: the PI (run SKILL) will set items to `stable`/`closed`, but worker agents reading `common.md.tmpl` will expect `resolved`/`partial`/`reframed`/`dropped`. The researcher will propose status as "resolved" when PI expects "stable." The critic will check whether "resolved" is warranted when the status should be "stable."

**Fix**: Update `common.md.tmpl` and all agent templates that reference the status system to use the new terminology. This is a required follow-up to make the merge operational.

#### [MINOR-3] "step 3" reference in TodoWrite guidance

Line 221: "always update TodoWrite in step 3 (insert new tasks, delete unnecessary tasks, reprioritize)"

With the new Note Curation phase inserted as step 4, the cycle steps are now: 1 (Research Judgment), 2 (Task Execution), 3 (Result Collection), 4 (Note Curation), 5 (Next Cycle). The TodoWrite update instruction in step 3 is correct (it's in Result Collection), so the reference is valid. No issue.

#### [MINOR-4] "skip to section 5" reference could be confusing

Line 374: "skip to §5" -- this refers to step 5 (Next Cycle), which is correct.

#### [MINOR-5] Critic mode added to prompt template but not to origin/main's critic data

Line 301 adds `mode: blind` or `mode: contextual` to the critic prompt data. The Critic verification mode section (lines 337-342) is newly added and well-explained. However, the `critic.md.tmpl` template itself may need updating to accept and act on this mode parameter. This is outside the three target files but is a dependency of the merge.

### D. Cross-File Consistency (Among the Three Target Files)

#### Directory structure alignment

| Path | run/SKILL | simulator | engine-builder |
|---|---|---|---|
| `simulations/lib/` | Yes | Yes (read-only) | Yes (primary) |
| `simulations/src/` | Yes | Yes (primary) | Yes (read for API consumption) |
| `simulations/src/archive/` | Yes | Not listed | Not listed |
| `simulations/results/{slug}/` | Yes | Yes | Not listed |
| `simulations/results/archive/` | Yes | Yes | Not listed |
| `simulations/test/` | Yes | Yes (read-only) | Yes (primary) |

`src/archive/` appearing only in run/SKILL is **correct** -- script archiving is PI's session-end responsibility (run/SKILL Session End section), not the simulator's or engine-builder's.

#### Role boundaries

The three files maintain clear role separation:
- simulator: writes to `src/`, `results/` (read-only for `lib/`)
- engine-builder: writes to `lib/`, `test/` (exception: updating `src/` call sites during API refactoring)
- run/SKILL (PI): coordinates both, handles session-end cleanup of `src/archive/`

No contradictions found in role boundaries.

#### Template variable consistency

| Variable | Used in |
|---|---|
| `{{ simulation.language }}` | simulator (line 58), engine-builder (line 14) |
| `{{ simulation.visualization }}` | simulator (line 93) |
| `{{ language }}` | simulator (lines 108, 110) |
| `{{ cycles.run }}` | run/SKILL (lines 3, 22) |

All template variables are used correctly and consistently.

### E. Redundancy Check

#### [MINOR-6] Partial content overlap between Results Directory Management and section 6

As noted in MAJOR-1, the Results Directory Management section and section 6 (Results README / REPORT.md) both specify what information should be in the results directory. Specifically:
- Results Directory Management: "file descriptions, physical setup, commands to reproduce"
- Section 6 REPORT.md: "overview (physical setup, observables, motivation), figures, data reliability, reproduction commands"

If unified under one filename, the content specifications should also be consolidated to avoid the simulator receiving partially overlapping instructions.

## Verification Results Summary

| Category | Result |
|---|---|
| 1. Internal consistency | FAIL -- MAJOR-1 (README/REPORT naming), MAJOR-2 (extend vs write contradiction) in simulator.md.tmpl |
| 2. Cross-file consistency (3 files) | PASS -- directory structures, role boundaries, and template variables are aligned |
| 3. Cross-file consistency (broader) | FAIL -- MAJOR-3 (status system mismatch with common.md.tmpl and agent templates) |
| 4. Missing references | PASS -- all section cross-references (§1, §2, §3, §4, §5) are valid |
| 5. Redundancy | MINOR -- README.md and REPORT.md content overlap (related to MAJOR-1) |
| 6. Template variables | PASS -- all `{{ }}` variables used correctly |

## Issue Count Summary

Critical: 0 / Major: 3 / Minor: 6

## Suggested Fixes

### For MAJOR-1 (README.md vs REPORT.md)
1. In simulator.md.tmpl Results Directory Management (line 41), change `README.md` to `REPORT.md`
2. Consolidate the content expectations: Results Directory Management specifies file naming, data format, and the existence of REPORT.md. Section 6 specifies the detailed content and structure of REPORT.md. Ensure no overlap in instructions

### For MAJOR-2 (extend vs write contradiction)
In simulator.md.tmpl section 2 (line 58), restore the origin/main phrasing:
> Write or extend a script in `src/` (per the decision made in §1). If extending, use Edit on the existing file; if creating new, write `src/{slug}.{ext}`. The script loads modules from `lib/` and implements only the measurement logic. Language: **{{ simulation.language }}** (matches the modules).

### For MAJOR-3 (status system mismatch)
Update the following files to use the new status system (`open`, `active`, `stable`, `closed`):
1. `templates/common.md.tmpl` -- line 5 status list, lines 7 and 13 `resolved` references
2. `templates/agents/researcher.md.tmpl` -- line 118 status list, lines 119-120 partial/reframed descriptions, line 124 resolved reference
3. `templates/agents/critic.md.tmpl` -- lines 76-77 resolved/partial references
4. `templates/agents/writer.md.tmpl` -- lines 25-31 all `(resolved)` and `(partial)` references
5. `templates/skills/meeting/SKILL.md.tmpl` -- lines 83-84 resolved/partial status counts
6. `templates/skills/write/SKILL.md.tmpl` -- line 75 open/partial check
