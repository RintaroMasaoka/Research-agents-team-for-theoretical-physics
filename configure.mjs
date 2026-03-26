#!/usr/bin/env node
/**
 * Render .md files from templates + config.yaml.
 *
 * Usage:
 *   node configure.mjs              Apply all templates (default)
 *   node configure.mjs --dry-run    Show what would change without writing files
 *   node configure.mjs --check      Validate config and templates (no writes)
 *
 * Source of truth:
 *   Config values:  .claude/config/config.yaml
 *   Prompt content: templates/**\/*.tmpl
 * Generated (do not edit directly — overwritten on each run):
 *   .claude/**\/*.md  (mirrors templates/ structure, .tmpl extension stripped)
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, statSync } from "fs";
import { join, dirname, relative } from "path";
import { fileURLToPath } from "url";

const ROOT = dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH = join(ROOT, ".claude", "config", "config.yaml");
const TMPL_DIR = join(ROOT, "templates");
const OUT_DIR = join(ROOT, ".claude");

// ── YAML parsing ──────────────────────────────────────────────────────

function parseConfig(path) {
  const lines = readFileSync(path, "utf-8").split("\n");
  const config = {};
  const stack = []; // [{indent, key}]

  for (const raw of lines) {
    const stripped = raw.replace(/\n$/, "");
    if (/^\s*#/.test(stripped) || !stripped.trim()) continue;

    const indent = stripped.length - stripped.trimStart().length;

    // Pop stack entries at same or deeper indent
    while (stack.length > 0 && stack[stack.length - 1].indent >= indent) {
      stack.pop();
    }

    const prefix = stack.map((s) => s.key).join(".") + (stack.length ? "." : "");
    const line = stripped.trim();
    const colon = line.indexOf(":");
    if (colon === -1) continue;

    const key = line.slice(0, colon);
    if (!/^[a-zA-Z_][\w-]*$/.test(key)) continue;

    const rest = line.slice(colon + 1).trim();

    if (rest === "") {
      // Parent key
      stack.push({ indent, key });
      continue;
    }

    // Key with value
    let val = rest.replace(/\s+#.*$/, ""); // strip inline comments
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    config[prefix + key] = val;
  }

  return config;
}

// ── Template rendering ────────────────────────────────────────────────

function findPlaceholders(template) {
  const cleaned = template.replace(/`[^`]*`/g, "");
  const keys = new Set();
  for (const m of cleaned.matchAll(/\{\{\s*([\w.]+)\s*\}\}/g)) {
    keys.add(m[1]);
  }
  return keys;
}

function render(template, config) {
  return template.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (match, key) => {
    return key in config ? config[key] : match;
  });
}

// ── Recursive glob for .tmpl files ───────────────────────────────────

function findTemplates(dir) {
  const results = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      results.push(...findTemplates(full));
    } else if (entry.endsWith(".tmpl")) {
      results.push(full);
    }
  }
  return results.sort();
}

// ── Main ──────────────────────────────────────────────────────────────

const mode = process.argv[2] || "apply";

if (mode === "--help") {
  console.log("Usage: node configure.mjs [--dry-run | --check]");
  process.exit(0);
}

if (!existsSync(CONFIG_PATH)) {
  console.error(`Error: ${CONFIG_PATH} not found`);
  process.exit(1);
}

const config = parseConfig(CONFIG_PATH);

// Display config
console.log("Config:");
for (const key of Object.keys(config).sort()) {
  console.log(`  ${key} = ${config[key]}`);
}
console.log();

// ── Check mode ────────────────────────────────────────────────────────
if (mode === "--check") {
  const warnings = [];
  const allPlaceholders = new Set();
  const templateKeys = {};

  for (const tmplPath of findTemplates(TMPL_DIR)) {
    const rel = relative(ROOT, tmplPath);
    const content = readFileSync(tmplPath, "utf-8");
    const keys = findPlaceholders(content);
    templateKeys[rel] = keys;
    for (const k of keys) allPlaceholders.add(k);
  }

  for (const key of Object.keys(config).sort()) {
    if (!allPlaceholders.has(key)) {
      warnings.push(`Unused config key: '${key}' (not referenced in any template)`);
    }
  }

  for (const [path, keys] of Object.entries(templateKeys).sort()) {
    for (const key of [...keys].sort()) {
      if (!(key in config)) {
        warnings.push(`Unresolved placeholder: '{{ ${key} }}' in ${path}`);
      }
    }
  }

  if (warnings.length > 0) {
    console.log("Warnings:");
    for (const w of warnings) console.log(`  ⚠ ${w}`);
    process.exit(1);
  } else {
    console.log("✓ All config keys are used, all placeholders are resolved.");
  }
  process.exit(0);
}

// ── Render templates ──────────────────────────────────────────────────
console.log(mode === "--dry-run" ? "Would generate:" : "Generated:");

for (const tmplPath of findTemplates(TMPL_DIR)) {
  const rel = relative(TMPL_DIR, tmplPath);
  const outRel = rel.replace(/\.tmpl$/, "");
  const dst = join(OUT_DIR, outRel);

  const content = readFileSync(tmplPath, "utf-8");
  const rendered = render(content, config);

  if (mode === "--dry-run") {
    let marker = " (new)";
    if (existsSync(dst)) {
      marker = readFileSync(dst, "utf-8") === rendered ? " (unchanged)" : " (changed)";
    }
    console.log(`  ${relative(ROOT, dst)}${marker}`);
  } else {
    mkdirSync(dirname(dst), { recursive: true });
    writeFileSync(dst, rendered);
    console.log(`  ${relative(ROOT, dst)}`);
  }
}

console.log();
console.log(mode === "--dry-run" ? "Dry run complete (no files written)." : "Done.");
