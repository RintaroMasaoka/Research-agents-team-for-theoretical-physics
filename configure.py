#!/usr/bin/env python3
"""Render .md files from templates + config.yaml.

Usage:
  ./configure.py              Apply all templates (default)
  ./configure.py --dry-run    Show what would change without writing files
  ./configure.py --check      Validate config and templates (no writes)
  ./configure.py --help       Show this help message

Source of truth:
  Config values:  .claude/config/config.yaml
  Prompt content: .claude/templates/**/*.tmpl
Generated (do not edit directly — overwritten on each run):
  .claude/**/*.md  (mirrors templates/ structure, .tmpl extension stripped)

Extending:
  New config key:   Add to config.yaml, use {{ key }} or {{ parent.child }} in templates
  New template:     Create .claude/templates/{path}.md.tmpl (auto-discovered)
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / ".claude" / "config" / "config.yaml"
TMPL_DIR = ROOT / ".claude" / "templates"
OUT_DIR = ROOT / ".claude"

# ── YAML parsing ──────────────────────────────────────────────────────

def parse_config(path: Path) -> dict[str, str]:
    """Parse YAML (arbitrary nesting depth) into flat dot-notation dict.

    Supports:
      key: value          → {"key": "value"}
      parent:
        child: value      → {"parent.child": "value"}
        deep:
          leaf: value     → {"parent.deep.leaf": "value"}
    """
    config: dict[str, str] = {}
    # Stack of (indent_level, key_prefix) for tracking nesting
    stack: list[tuple[int, str]] = []

    with open(path) as f:
        for lineno, line in enumerate(f, 1):
            stripped = line.rstrip("\n")

            # Skip comments and blank lines
            if re.match(r"^\s*#", stripped) or not stripped.strip():
                continue

            # Measure indentation (number of leading spaces)
            indent = len(stripped) - len(stripped.lstrip())

            # Reject tab indentation (YAML forbids tabs)
            if "\t" in stripped[:indent]:
                print(f"Error: tab indentation on line {lineno}: {stripped!r}", file=sys.stderr)
                sys.exit(1)

            # Pop stack entries that are at the same or deeper indent level
            while stack and stack[-1][0] >= indent:
                stack.pop()

            # Build current prefix from stack
            prefix = stack[-1][1] + "." if stack else ""

            # Parent key (key with no value — starts a nested block)
            m = re.match(r"^(\s*)([a-zA-Z_][\w-]*):\s*$", stripped)
            if m:
                key = m.group(2)
                stack.append((indent, prefix + key))
                continue

            # Key with value
            m = re.match(r"^(\s*)([a-zA-Z_][\w-]*):\s+(.+)$", stripped)
            if m:
                key = m.group(2)
                value = m.group(3)
                # Strip trailing inline comments
                value = re.sub(r"\s+#.*$", "", value)
                # Strip surrounding quotes
                if len(value) >= 2 and (
                    (value[0] == '"' and value[-1] == '"') or
                    (value[0] == "'" and value[-1] == "'")
                ):
                    value = value[1:-1]
                config[prefix + key] = value
                continue

            # Warn about unrecognized lines
            print(f"Warning: skipped unrecognized line {lineno}: {stripped!r}", file=sys.stderr)

    return config

# ── Template rendering ────────────────────────────────────────────────

def find_placeholders(template: str) -> set[str]:
    """Extract all {{ key }} placeholder names from a template string.

    Skips placeholders inside backtick-quoted spans (`` `{{ key }}` ``)
    since those are documentation examples, not real placeholders.
    """
    # Remove backtick-quoted spans first to avoid false positives
    cleaned = re.sub(r"`[^`]*`", "", template)
    return {m.group(1).strip() for m in re.finditer(r"\{\{\s*([\w.]+)\s*\}\}", cleaned)}


def render(template: str, config: dict[str, str]) -> str:
    """Replace all {{ key }} placeholders with config values.

    Unknown placeholders are left as-is (and flagged by --check).
    """
    def replacer(m: re.Match) -> str:
        key = m.group(1).strip()
        return config.get(key, m.group(0))
    return re.sub(r"\{\{\s*([\w.]+)\s*\}\}", replacer, template)

# ── Validation ────────────────────────────────────────────────────────

def check_config_and_templates(config: dict[str, str]) -> list[str]:
    """Return a list of warning messages for config/template issues."""
    warnings: list[str] = []

    # Collect all placeholders used across all templates
    used_keys: set[str] = set()
    template_keys: dict[str, set[str]] = {}  # path → set of keys

    for tmpl_path in sorted(TMPL_DIR.rglob("*.tmpl")):
        rel = tmpl_path.relative_to(ROOT)
        content = tmpl_path.read_text()
        keys = find_placeholders(content)
        template_keys[str(rel)] = keys
        used_keys.update(keys)

    # Warn: config keys not used by any template
    for key in sorted(config):
        if key not in used_keys:
            warnings.append(f"Unused config key: '{key}' (not referenced in any template)")

    # Warn: template placeholders with no matching config key
    for path, keys in sorted(template_keys.items()):
        for key in sorted(keys):
            if key not in config:
                warnings.append(f"Unresolved placeholder: '{{{{ {key} }}}}' in {path}")

    return warnings

# ── Main ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render .md files from templates + config.yaml.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Validate config and templates (no file writes)",
    )
    args = parser.parse_args()

    if not CONFIG_PATH.exists():
        print(f"Error: {CONFIG_PATH} not found", file=sys.stderr)
        sys.exit(1)

    config = parse_config(CONFIG_PATH)

    # ── Display config ────────────────────────────────────────────
    print("Config:")
    for key in sorted(config):
        print(f"  {key} = {config[key]}")
    print()

    # ── Check mode ────────────────────────────────────────────────
    if args.check:
        warnings = check_config_and_templates(config)
        if warnings:
            print("Warnings:")
            for w in warnings:
                print(f"  ⚠ {w}")
            sys.exit(1)
        else:
            print("✓ All config keys are used, all placeholders are resolved.")
        return

    # ── Render templates ──────────────────────────────────────────
    label = "Would generate:" if args.dry_run else "Generated:"
    print(label)

    for tmpl_path in sorted(TMPL_DIR.rglob("*.tmpl")):
        rel = tmpl_path.relative_to(TMPL_DIR)
        out_rel = rel.parent / rel.name.removesuffix(".tmpl")
        dst = OUT_DIR / out_rel

        content = tmpl_path.read_text()
        rendered = render(content, config)

        if args.dry_run:
            # Show diff if file exists and content differs
            marker = ""
            if dst.exists():
                existing = dst.read_text()
                if existing != rendered:
                    marker = " (changed)"
                else:
                    marker = " (unchanged)"
            else:
                marker = " (new)"
            print(f"  {dst.relative_to(ROOT)}{marker}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(rendered)
            print(f"  {dst.relative_to(ROOT)}")

    print()
    print("Done." if not args.dry_run else "Dry run complete (no files written).")


if __name__ == "__main__":
    main()
