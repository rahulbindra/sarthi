---
name: sarthi-setup
description: One-time setup for Sarthi. Automatically configures the SessionStart hook, PostToolUse graphify hook, and codeburn menubar. Run once after installing Sarthi.
---

# Sarthi Setup

Run this skill once after installing Sarthi. It configures everything automatically so you never need to touch a config file manually.

> **Run in a fresh Claude Code session** — this skill does significant work and can hit context limits if the session already has history. Open a new session, then run `/sarthi-setup`.

## What this does

1. Detects missing Sarthi-compatible tools and installs what it can automatically
2. Adds all Sarthi hooks to `~/.claude/settings.json` (SessionStart, PostToolUse, UserPromptSubmit)
3. Auto-enables all three advisors (prompt optimizer, session monitor, model advisor)
4. Auto-installs a global pre-commit hook that scans staged files for hardcoded secrets
5. Installs codeburn menubar (if codeburn is installed)

> **Configure later (no setup required):**
> - Morph MCP — get a free key at morphllm.com, then re-run `/sarthi-setup`
> - ANTHROPIC_API_KEY for graphify — `export ANTHROPIC_API_KEY=sk-ant-... >> ~/.zprofile`

## Steps

### Step 0 — Detect tool gaps and show install table

Before configuring anything, check which Sarthi-compatible tools are installed vs. missing. This surfaces what to install to unlock full routing value.

```bash
command -v graphify > /dev/null 2>&1 && echo "graphify:installed" || echo "graphify:missing"
command -v codeburn > /dev/null 2>&1 && echo "codeburn:installed" || echo "codeburn:missing"
jq -e '.mcpServers["morph-mcp"]' ~/.claude.json > /dev/null 2>&1 && echo "morph:configured" || echo "morph:missing"
(jq -e '.enabledPlugins["firecrawl@claude-plugins-official"] == true' ~/.claude/settings.json > /dev/null 2>&1 || [ -d ~/.claude/skills/firecrawl-agent ] || [ -d ~/.claude/plugins/cache/claude-plugins-official/firecrawl ]) && echo "firecrawl:installed" || echo "firecrawl:missing"
(jq -e '.enabledPlugins["compound-engineering@compound-engineering-plugin"] == true' ~/.claude/settings.json > /dev/null 2>&1 || [ -d ~/.claude/skills/ce-work ] || [ -d ~/.claude/plugins/cache/compound-engineering-plugin/compound-engineering ]) && echo "compound:installed" || echo "compound:missing"
(jq -e '.enabledPlugins["codex@openai-codex"] == true' ~/.claude/settings.json > /dev/null 2>&1 || [ -d ~/.claude/skills/codex-cli-runtime ] || [ -d ~/.claude/plugins/cache/openai-codex/codex ]) && echo "codex:installed" || echo "codex:missing"
(jq -e '.enabledPlugins["superpowers@claude-plugins-official"] == true' ~/.claude/settings.json > /dev/null 2>&1 || [ -d ~/.claude/skills/dispatching-parallel-agents ] || [ -d ~/.claude/plugins/cache/claude-plugins-official/superpowers ]) && echo "superpowers:installed" || echo "superpowers:missing"
```

Show this table — mark each row ✓ (installed) or ✗ (missing):

```
Sarthi tool gap report:
──────────────────────────────────────────────────────────────────────
  graphify              [✓/✗]   codebase knowledge graph
  codeburn              [✓/✗]   token spend analytics
  morph (MCP)           [✓/✗]   fast bulk code edits
  firecrawl             [✓/✗]   web research and scraping
  compound-engineering  [✓/✗]   build, debug, review, ship, strategy
  codex                 [✓/✗]   parallel code review and investigation
  superpowers           [✓/✗]   parallel agents, TDD, debugging
──────────────────────────────────────────────────────────────────────
[N] tools ready · [M] not installed
```

For each missing tool, show a one-line install hint below the table:

| Tool | Install hint |
|------|-------------|
| graphify | `pip install graphifyy` (note: two y's — PyPI package) |
| codeburn | `npm install -g codeburn` |
| morph | free API key required — get one at morphllm.com, Step 5 configures it |
| firecrawl | `/plugin install firecrawl@claude-plugins-official` |
| compound-engineering | `/plugin install compound-engineering@compound-engineering-plugin` |
| codex | `/plugin install codex@openai-codex` |
| superpowers | `/plugin install superpowers@claude-plugins-official` |

If all tools are already installed, show: "All Sarthi tools detected — no gaps found." and skip to Step 1.

### Step 0b — Interactive installation of missing tools

If any tools are missing, offer to install them now. Load `AskUserQuestion` via `ToolSearch` with `select:AskUserQuestion`, then present only the missing tools as multi-select options:

> "Which missing tools would you like to set up now? (I'll handle what I can automatically — select all that apply)"

Wait for the user's selection. If nothing selected or skipped — continue to Step 0c.

For each selected tool, attempt setup in this order:

**graphify:**
```bash
pip install graphifyy 2>&1
```
Note: two y's — this is the PyPI package (`graphifyy`), not an npm package. Confirm success or surface the error. If pip is unavailable: "pip required — install Python 3 from python.org first, then re-run /sarthi-setup."

**codeburn:**
```bash
npm install -g codeburn 2>&1
```
Confirm success or surface the error. If npm is unavailable: "npm required — install Node.js from nodejs.org first, then re-run /sarthi-setup."

**morph (MCP):**
Show: "Morph MCP will be auto-configured in Step 5 — no API key needed for the free plan."

**compound-engineering:**
```bash
CACHE="$HOME/.claude/plugins/cache/compound-engineering-plugin/compound-engineering"
if [ -d "$CACHE" ]; then
  LATEST=$(ls -t "$CACHE" | head -1)
  cp -r "$CACHE/$LATEST/skills/." "$HOME/.claude/skills/"
  echo "✓ compound-engineering installed from cache (v$LATEST)"
else
  echo "not-cached"
fi
```
If `not-cached`: show `Run: /plugin install compound-engineering@compound-engineering-plugin — then type "done" to continue.` Wait for "done", then re-run the cache check above.

**firecrawl:**
```bash
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official/firecrawl"
if [ -d "$CACHE" ]; then
  LATEST=$(ls -t "$CACHE" | head -1)
  cp -r "$CACHE/$LATEST/skills/." "$HOME/.claude/skills/"
  echo "✓ firecrawl installed from cache (v$LATEST)"
else
  echo "not-cached"
fi
```
If `not-cached`: auto-install directly from GitHub — do not ask the user:
```bash
PLUGIN_TMP=$(mktemp -d)
git clone --depth 1 https://github.com/mendableai/firecrawl "$PLUGIN_TMP/firecrawl-src" 2>&1
if [ -d "$PLUGIN_TMP/firecrawl-src/skills" ]; then
  cp -r "$PLUGIN_TMP/firecrawl-src/skills/." "$HOME/.claude/skills/"
  echo "✓ firecrawl installed from GitHub"
elif [ -f "$PLUGIN_TMP/firecrawl-src/.claude-plugin/marketplace.json" ]; then
  SOURCE=$(jq -r '.plugins[0].source // "./"' "$PLUGIN_TMP/firecrawl-src/.claude-plugin/marketplace.json")
  cp -r "$PLUGIN_TMP/firecrawl-src/$SOURCE/skills/." "$HOME/.claude/skills/" 2>/dev/null || \
  cp -r "$PLUGIN_TMP/firecrawl-src/skills/." "$HOME/.claude/skills/" 2>/dev/null
  echo "✓ firecrawl installed from GitHub"
else
  echo "firecrawl:install-failed"
fi
```
If `firecrawl:install-failed`: show this prominently — do not let it get lost in surrounding output:

```
⚠️  firecrawl auto-install failed (network or repo issue).
    Manual install required — run this after setup completes:

    /plugin marketplace add https://github.com/mendableai/firecrawl

    Continuing setup without firecrawl.
```

**codex:**
```bash
CACHE="$HOME/.claude/plugins/cache/openai-codex/codex"
if [ -d "$CACHE" ]; then
  LATEST=$(ls -t "$CACHE" | head -1)
  cp -r "$CACHE/$LATEST/skills/." "$HOME/.claude/skills/"
  echo "✓ codex installed from cache (v$LATEST)"
else
  echo "not-cached"
fi
```
If `not-cached`: show `Run: /plugin install codex@openai-codex — then type "done" to continue.` Wait for "done", then re-run the cache check above.

**superpowers:**
```bash
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official/superpowers"
if [ -d "$CACHE" ]; then
  LATEST=$(ls -t "$CACHE" | head -1)
  cp -r "$CACHE/$LATEST/skills/." "$HOME/.claude/skills/"
  echo "✓ superpowers installed from cache (v$LATEST)"
else
  echo "not-cached"
fi
```
If `not-cached`: show `Run: /plugin install superpowers@claude-plugins-official — then type "done" to continue.` Wait for "done", then re-run the cache check above.

After all selected installs complete, re-run the Step 0 detection checks and show an updated gap table so the user sees what is now ready.

Continue to Step 0c regardless of outcomes.

### Step 0c — Check ANTHROPIC_API_KEY for graphify

Check if graphify is present and if the key is already configured:
```bash
command -v graphify > /dev/null 2>&1 && echo "graphify:present" || echo "graphify:absent"
grep -r "ANTHROPIC_API_KEY" ~/.zshrc ~/.zprofile ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null | grep -v "^Binary" | grep -q . && echo "key:present" || echo "key:absent"
```

Store the result as `api_key_status` (`present` or `absent`).

If `graphify:present` AND `key:absent`, show this warning immediately before proceeding — do not defer to the summary:

```
⚠️  graphify is installed but ANTHROPIC_API_KEY is not set.
    Graph builds will fail silently until you add it:

    echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.zprofile && source ~/.zprofile

    Get a key at console.anthropic.com/keys
    Note: Claude Code uses OAuth — a separate API key is required for graphify.

    Continuing setup. You can add the key later and re-run /sarthi-setup.
```

Continue to Step 1.

---

### Step 1 — Read current settings

Read `~/.claude/settings.json`. If it doesn't exist, start with `{}`.

### Step 2 — Check what's already configured

Check if the Sarthi SessionStart hook is already present:
```bash
jq '.hooks.SessionStart[]?.hooks[]?.command | select(. != null) | select(contains("sarthi"))' ~/.claude/settings.json 2>/dev/null
```

Check if the graphify PostToolUse hook is already present:
```bash
jq '.hooks.PostToolUse[]? | select(.matcher == "Write|Edit") | .hooks[]?.command | select(contains("graphify"))' ~/.claude/settings.json 2>/dev/null
```

Check if codeburn is installed:
```bash
command -v codeburn > /dev/null && echo "yes" || echo "no"
```

### Step 3 — Merge hooks into settings.json

For each hook that is NOT already present, merge it into `~/.claude/settings.json` using `jq`.

**SessionStart hook** (if missing):
```bash
jq '.hooks.SessionStart = (.hooks.SessionStart // []) + [{
  "hooks": [{
    "type": "command",
    "statusMessage": "Sarthi loading...",
    "command": "python3 -c \"import json; print(json.dumps({'\''hookSpecificOutput'\'': {'\''hookEventName'\'': '\''SessionStart'\'', '\''additionalContext'\'': '\''Act as Sarthi. Load ~/.claude/skills/sarthi/SKILL.md and follow it exactly, including the Session Onboarding block: detect tools silently, auto-setup graphify if needed, then present the welcome prompt listing active tools and asking the user if they want to skip any before routing.'\''}}))\" "
  }]
}]' ~/.claude/settings.json > /tmp/sarthi-settings-tmp.json && mv /tmp/sarthi-settings-tmp.json ~/.claude/settings.json
```

**PostToolUse hook** (if missing):
```bash
jq '.hooks.PostToolUse = (.hooks.PostToolUse // []) + [{
  "matcher": "Write|Edit",
  "hooks": [{
    "type": "command",
    "command": "[ -f graphify-out/graph.json ] && python3 -c \"import os,time; exit(0 if time.time()-os.path.getmtime('\''graphify-out/graph.json'\'')>30 else 1)\" 2>/dev/null && graphify update . > /dev/null 2>&1 || true"
  }]
}]' ~/.claude/settings.json > /tmp/sarthi-settings-tmp.json && mv /tmp/sarthi-settings-tmp.json ~/.claude/settings.json
```

**PostToolUse hook — intent logging** (if not already present):
```bash
jq '.hooks.PostToolUse = (.hooks.PostToolUse // []) + [{
  "matcher": "Skill",
  "hooks": [{
    "type": "command",
    "command": "python3 -c \"import sys,json,os; from datetime import datetime,timezone; data=json.load(sys.stdin); skill=data.get(\\\"tool_input\\\",{}).get(\\\"skill\\\",\\\"unknown\\\"); entry=json.dumps({\\\"ts\\\":datetime.now(timezone.utc).strftime(\\\"%Y-%m-%dT%H:%M:%SZ\\\"),\\\"routed_to\\\":skill}); open(os.path.expanduser(\\\"~/.claude/.sarthi-intent-log.jsonl\\\"),\\\"a\\\").write(entry+\\\"\\\\n\\\")\" 2>/dev/null || true"
  }]
}]' ~/.claude/settings.json > /tmp/sarthi-settings-tmp.json && mv /tmp/sarthi-settings-tmp.json ~/.claude/settings.json
```

**Install the UserPromptSubmit hook script** (runs inline session monitor + model advisor — no longer asks Claude to invoke the skill, does the assessment itself):
```bash
mkdir -p ~/.claude/.sarthi-hooks
cp "$(dirname "$0")/../../hooks/user-prompt-submit.py" ~/.claude/.sarthi-hooks/user-prompt-submit.py
```

**UserPromptSubmit hook — wire the script** (if not already present):
```bash
jq '.hooks.UserPromptSubmit = (.hooks.UserPromptSubmit // []) + [{
  "hooks": [{
    "type": "command",
    "command": "python3 ~/.claude/.sarthi-hooks/user-prompt-submit.py 2>/dev/null || true"
  }]
}]' ~/.claude/settings.json > /tmp/sarthi-settings-tmp.json && mv /tmp/sarthi-settings-tmp.json ~/.claude/settings.json
```

**SessionStart hook — reset session counters** (add counter reset to existing SessionStart command, if not already present — prepend to the existing command string):
The SessionStart hook command should begin with:
`rm -f ~/.claude/.sarthi-session-counter ~/.claude/.sarthi-session-warned 2>/dev/null; `

### Step 4 — (skipped — ANTHROPIC_API_KEY is configured later by the user)

Continue to Step 5.

### Step 5 — Install Morph MCP (optional)

**First: check for an existing Morph API key across all locations:**
```bash
# 1. From environment
printenv MORPH_API_KEY 2>/dev/null

# 2. From shell profiles (fixed sed — use double-quote string to handle single-quote stripping)
grep -h "MORPH_API_KEY" ~/.zshrc ~/.zprofile ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null \
  | grep -v "^#" | head -1 \
  | sed "s/.*MORPH_API_KEY[=:][\"'[:space:]]*//" | tr -d "\"'"

# 3. From ~/.claude/morph/.env (Morph's own config directory)
grep "MORPH_API_KEY" ~/.claude/morph/.env 2>/dev/null | cut -d'=' -f2 | tr -d '[:space:]'

# 4. From existing ~/.claude.json env field
jq -r '.mcpServers["morph-mcp"].env.MORPH_API_KEY // empty' ~/.claude.json 2>/dev/null

# 5. From existing ~/.claude.json args array (Morph stores key as --api-key <value>)
jq -r '
  .mcpServers["morph-mcp"].args
  | if . then
      . as $args
      | indices("--api-key")
      | if length > 0 then $args[.[0]+1] else empty end
    else empty end
' ~/.claude.json 2>/dev/null
```
Use the first non-empty value found as `found_key`.

If Morph is already configured in `~/.claude.json`:
- If `found_key` is set: set `morph_status = configured_with_key`. **Do not rewrite the entry** — preserve it as-is.
- If `found_key` is empty: set `morph_status = configured_no_key`. **Do not rewrite** — preserve it as-is.
- Skip to Step 6 in both cases.

If NOT configured, ask the user using `AskUserQuestion`:

> "Morph MCP enables fast bulk code edits. Set it up now?"
> [y] Yes — set it up
> [s] Skip — I'll do it later

If **[s]**: set `morph_status = skipped`. Continue to Step 6.

**2. Configure `~/.claude.json`:**
```bash
[ -f ~/.claude.json ] || echo '{"mcpServers":{}}' > ~/.claude.json
```

If `found_key` is set:
```bash
jq --arg key "$found_key" '.mcpServers["morph-mcp"] = {
  "type": "stdio",
  "command": "npx",
  "args": ["--prefer-offline", "-y", "@morphllm/morphmcp@latest", "--api-key", $key],
  "env": { "MORPH_API_KEY": $key, "DISABLED_TOOLS": "" }
}' ~/.claude.json > /tmp/sarthi-claude-tmp.json && mv /tmp/sarthi-claude-tmp.json ~/.claude.json
```
Set `morph_status = configured_with_key`.

If `found_key` is empty:
```bash
jq '.mcpServers["morph-mcp"] = {
  "type": "stdio",
  "command": "npx",
  "args": ["--prefer-offline", "-y", "@morphllm/morphmcp@latest"],
  "env": { "DISABLED_TOOLS": "" }
}' ~/.claude.json > /tmp/sarthi-claude-tmp.json && mv /tmp/sarthi-claude-tmp.json ~/.claude.json
```
Set `morph_status = configured_no_key`.

### Step 6 — Auto-enable Sarthi advisors

Enable all three advisors automatically — they are non-blocking and reversible at any time:

```bash
touch ~/.claude/.sarthi-prompt-optimizer-enabled
touch ~/.claude/.sarthi-session-monitor-enabled
touch ~/.claude/.sarthi-model-advisor-enabled
```

(Skip any that are already enabled — `touch` is idempotent but note in summary if they were already on.)

To disable any advisor later:
- `rm ~/.claude/.sarthi-prompt-optimizer-enabled`
- `rm ~/.claude/.sarthi-session-monitor-enabled`
- `rm ~/.claude/.sarthi-model-advisor-enabled`

### Step 7 — Auto-install pre-commit secrets scan

Check if already configured:
```bash
[ -f ~/.claude/.sarthi-hooks/pre-commit ] && echo "configured" || echo "missing"
```

If already configured, skip this step silently.

If NOT configured, install it automatically:

1. Create the hooks directory:
```bash
mkdir -p ~/.claude/.sarthi-hooks
```

2. Write the hook script:
```bash
cat > ~/.claude/.sarthi-hooks/pre-commit << 'HOOK'
#!/bin/bash
# Sarthi pre-commit hook — scans staged files for hardcoded secrets
# Installed by /sarthi-setup
# To disable: git config --global --unset core.hooksPath

STAGED_FILES=$(git diff --cached --name-only 2>/dev/null)
[ -z "$STAGED_FILES" ] && exit 0

FOUND=0

while IFS= read -r file; do
  [ -f "$file" ] || continue
  # Skip documentation files — patterns in docs/comments are not real secrets
  case "$file" in
    *.md|*.txt|*.rst|*.adoc) continue ;;
  esac
  result=$(grep -n \
    -e "sk-ant-" \
    -e "AKIA[0-9A-Z]\{16\}" \
    -e "ghp_[a-zA-Z0-9]\{36\}" \
    -e "gho_[a-zA-Z0-9]\{36\}" \
    -e "xoxb-\|xoxp-" \
    -e "AIza[0-9A-Za-z_-]\{35\}" \
    -e "-----BEGIN.*PRIVATE KEY-----" \
    -e "password\s*=\s*['\"][^'\"]\{4,\}['\"]" \
    -e "secret\s*=\s*['\"][^'\"]\{4,\}['\"]" \
    -e "api_key\s*=\s*['\"][^'\"]\{4,\}['\"]" \
    "$file" 2>/dev/null)
  if [ -n "$result" ]; then
    if [ $FOUND -eq 0 ]; then
      echo ""
      echo "🔴  Sarthi pre-commit: possible secrets detected in staged files"
      echo ""
    fi
    FOUND=1
    echo "  $file"
    echo "$result" | sed 's/^/    /'
    echo ""
  fi
done <<< "$STAGED_FILES"

if [ $FOUND -eq 1 ]; then
  echo "Review the above before committing."
  echo "To bypass (only if intentional): git commit --no-verify"
  echo ""
  exit 1
fi
exit 0
HOOK
chmod +x ~/.claude/.sarthi-hooks/pre-commit
```

3. Configure git to use this hooks directory globally:
```bash
git config --global core.hooksPath ~/.claude/.sarthi-hooks
```

### Step 8 — Install codeburn menubar

If codeburn is installed and menubar is not already running:
```bash
codeburn menubar &
```

### Step 8b — Verify configuration

Run self-checks and surface any failures clearly before showing the summary:

```bash
jq -e '.hooks.SessionStart[]?.hooks[]?.command | select(. != null) | select(contains("sarthi"))' ~/.claude/settings.json > /dev/null 2>&1 && echo "hook:sessionstart:ok" || echo "hook:sessionstart:MISSING"
jq -e '.hooks.PostToolUse[]? | select(.matcher == "Write|Edit") | .hooks[]?.command | select(contains("graphify"))' ~/.claude/settings.json > /dev/null 2>&1 && echo "hook:posttooluse:ok" || echo "hook:posttooluse:MISSING"
jq -e '.hooks.UserPromptSubmit[]?.hooks[]?.command | select(contains("sarthi-hooks"))' ~/.claude/settings.json > /dev/null 2>&1 && echo "hook:userpromptsubmit:ok" || echo "hook:userpromptsubmit:MISSING"
[ -f ~/.claude/.sarthi-prompt-optimizer-enabled ] && echo "advisor:ok" || echo "advisor:MISSING"
[ -f ~/.claude/.sarthi-hooks/pre-commit ] && echo "precommit:ok" || echo "precommit:MISSING"
```

If any check returns `MISSING`, show it as `✗` in the summary and tell the user to re-run `/sarthi-setup`.

### Step 9 — Confirm to the user

After completing the above, report clearly what was done and what was skipped. Use this format:

```
Sarthi setup complete.

✓ SessionStart hook           — added to ~/.claude/settings.json
✓ PostToolUse hook (graphify) — added to ~/.claude/settings.json
✓ PostToolUse hook (intent)   — added to ~/.claude/settings.json
✓ UserPromptSubmit hook       — added to ~/.claude/settings.json
✓ Morph MCP                   — configured (key found automatically)
✓ Prompt optimizer            — enabled
✓ Session monitor             — enabled
✓ Model advisor               — enabled
✓ Pre-commit scan             — installed (~/.claude/.sarthi-hooks/pre-commit)
✓ codeburn menubar            — launched

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠️  RESTART CLAUDE CODE NOW for hooks to activate.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Morph MCP line variants:
- `morph_status = configured_with_key` → `✓ Morph MCP — configured (key found automatically)`
- `morph_status = configured_no_key` → `✓ Morph MCP — configured (no key — get one free at morphllm.com, then re-run /sarthi-setup)`
- `morph_status = skipped` → `  Morph MCP — skipped (re-run /sarthi-setup to add)`
- `morph_status = already configured` → `✓ Morph MCP — already configured`

If `api_key_status` is `absent` and graphify is present, add this line above the restart banner:
```
⚠️  graphify: ANTHROPIC_API_KEY not set — graph builds will fail.
    Fix: echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.zprofile && source ~/.zprofile
```

Other status variants:
- Already configured before setup → `— already configured`
- codeburn not installed → `— codeburn not installed, skipped`
- Advisor already enabled before setup → `— already enabled`
- Pre-commit scan already installed → `— already installed`

### Important

- Never overwrite existing hooks — always merge using jq so existing configuration is preserved
- If `~/.claude/settings.json` has invalid JSON, stop and tell the user: "~/.claude/settings.json has invalid JSON. Fix it first, then re-run /sarthi-setup."
- Do not proceed with any step if a previous step failed
