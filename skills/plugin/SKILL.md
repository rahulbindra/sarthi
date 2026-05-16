---
name: plugin
description: Plugin manager for Claude Code. Handles /plugin marketplace add <url> and /plugin install <name> commands. Clones plugin repos, copies skills to ~/.claude/skills/, and registers them in ~/.claude/CLAUDE.md. Bootstrap skill — install once, then use to install everything else.
argument-hint: "marketplace add <github-url> | install <plugin-name>"
---

# Plugin Manager

You are the Claude Code plugin manager. You handle two commands:

- `/plugin marketplace add <url>` — install a plugin from a GitHub URL
- `/plugin install <name>` — install a named plugin (looks up from its `.claude-plugin/marketplace.json`)

---

## /plugin marketplace add <url>

When the user runs `/plugin marketplace add <url>`:

### Step 1 — Clone the repo to a temp directory

```bash
REPO_URL="<url>"
PLUGIN_TMP=$(mktemp -d)
git clone --depth 1 "$REPO_URL" "$PLUGIN_TMP/plugin-src" 2>&1
```

If the clone fails, report the git error and stop.

### Step 2 — Read the marketplace manifest

Look for `.claude-plugin/marketplace.json` in the cloned repo.

```bash
cat "$PLUGIN_TMP/plugin-src/.claude-plugin/marketplace.json"
```

If the file doesn't exist: tell the user "This repo does not appear to be a Claude Code plugin — no `.claude-plugin/marketplace.json` found." and stop.

Parse the manifest to get:
- `name` — the plugin name (e.g. `sarthi`)
- `metadata.description` — what it does
- `metadata.version` — version string
- `plugins[].source` — source directory relative to repo root (usually `./`)

### Step 3 — Copy skills

```bash
PLUGIN_NAME="<name from manifest>"
SOURCE_DIR="$PLUGIN_TMP/plugin-src"  # adjust if plugins[].source is a subdir

# Copy all skills
if [ -d "$SOURCE_DIR/skills" ]; then
  mkdir -p ~/.claude/skills
  cp -r "$SOURCE_DIR/skills/"* ~/.claude/skills/
  echo "Copied skills: $(ls $SOURCE_DIR/skills/)"
fi

# Copy hooks if present
if [ -d "$SOURCE_DIR/hooks" ]; then
  mkdir -p ~/.claude/hooks
  cp -r "$SOURCE_DIR/hooks/"* ~/.claude/hooks/
  echo "Copied hooks: $(ls $SOURCE_DIR/hooks/)"
fi
```

### Step 4 — Register skills in ~/.claude/CLAUDE.md

For each skill directory copied (each subdirectory under `skills/`), check if it's already registered in `~/.claude/CLAUDE.md`. If not, add a registration line.

Read `~/.claude/CLAUDE.md` and look for a line containing the skill name. If absent, append:

```
- **<skill-name>** (`~/.claude/skills/<skill-name>/SKILL.md`) - <description from SKILL.md frontmatter>. Trigger: `/<skill-name>`
```

Read the `description` field from each `SKILL.md` frontmatter for the description text.

Do this for every skill that was copied.

### Step 5 — Confirm to user

Show a summary:

```
✅ Plugin installed: <plugin-name> v<version>

Skills added:
  - /<skill-1>
  - /<skill-2>
  ...

Run /<primary-skill>-setup to complete configuration (if a setup skill exists).
```

If a `<plugin-name>-setup` skill was installed, prompt the user to run it now.

---

## /plugin install <name>

When the user runs `/plugin install <name>`:

This is a shorthand that resolves the plugin by name from the plugin's own repo, if the user has previously added it via `marketplace add`, or from a well-known registry.

### Resolution order

1. **Already added** — check if `~/.claude/skills/<name>/SKILL.md` exists. If so, re-run the copy step to update it.
2. **Known plugin** — check the hardcoded registry below.
3. **Not found** — tell the user to use `/plugin marketplace add <github-url>` instead.

### Known plugin registry

| Name | GitHub URL |
|------|-----------|
| `sarthi` | `https://github.com/rahulbindra/sarthi` |
| `compound-engineering` | `https://github.com/EveryInc/compound-engineering-plugin` |
| `graphify` | `https://github.com/safishamsi/graphify` |
| `superpowers` | `https://github.com/obra/superpowers` |
| `codex` | `https://github.com/openai/codex-plugin-cc` |
| `firecrawl` | `https://github.com/mendableai/firecrawl` |
| `morph` | `https://github.com/morphllm/morph-claude-code-plugin` |

Once resolved to a URL, follow the same steps as `/plugin marketplace add <url>`.

---

## /plugin list

List all installed plugins by reading `~/.claude/skills/` directory names.

```bash
ls ~/.claude/skills/
```

Show each with its description from its SKILL.md frontmatter.

---

## /plugin remove <name>

Remove a plugin:

```bash
rm -rf ~/.claude/skills/<name>
```

Then remove its registration line from `~/.claude/CLAUDE.md`.

Confirm: "Removed plugin: `<name>`"

---

## Error handling

- **git not found:** "git is required to install plugins. Install it with `brew install git`."
- **Network error during clone:** Show the git error. Suggest checking the URL and network.
- **CLAUDE.md not found:** Create it at `~/.claude/CLAUDE.md` before appending.
- **Skill already installed:** "Skill `<name>` is already installed. Re-copying to update it." Then proceed.
- **Manifest parse error:** Show the raw JSON and the parse error. Stop.
