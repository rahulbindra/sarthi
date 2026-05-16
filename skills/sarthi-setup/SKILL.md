---
name: sarthi-setup
description: One-time setup for Sarthi. Automatically configures the SessionStart hook, PostToolUse graphify hook, and codeburn menubar. Run once after installing Sarthi.
---

# Sarthi Setup

Run this skill once after installing Sarthi. It configures everything automatically so you never need to touch a config file manually.

## What this does

1. Detects missing Sarthi-compatible tools and installs what it can automatically
2. Adds all Sarthi hooks to `~/.claude/settings.json` (SessionStart, PostToolUse, UserPromptSubmit)
3. Auto-configures Morph MCP server in `~/.claude.json` (free plan — no API key required)
4. Auto-enables all three advisors (prompt optimizer, session monitor, model advisor)
5. Auto-installs a global pre-commit hook that scans staged files for hardcoded secrets
6. Optionally sets `ANTHROPIC_API_KEY` in your shell profile (needed for graphify graph building)
7. Installs codeburn menubar (if codeburn is installed)

## Steps

### Step 0 — Detect tool gaps and show install table

Before configuring anything, check which Sarthi-compatible tools are installed vs. missing. This surfaces what to install to unlock full routing value.

```bash
command -v graphify > /dev/null 2>&1 && echo "graphify:installed" || echo "graphify:missing"
command -v codeburn > /dev/null 2>&1 && echo "codeburn:installed" || echo "codeburn:missing"
jq -e '.mcpServers["morph-mcp"]' ~/.claude.json > /dev/null 2>&1 && echo "morph:configured" || echo "morph:missing"
([ -d ~/.claude/skills/firecrawl-agent ] || [ -d ~/.claude/plugins/cache/claude-plugins-official/firecrawl ]) && echo "firecrawl:installed" || echo "firecrawl:missing"
([ -d ~/.claude/skills/ce-work ] || [ -d ~/.claude/plugins/cache/compound-engineering-plugin/compound-engineering ]) && echo "compound:installed" || echo "compound:missing"
([ -d ~/.claude/skills/codex-cli-runtime ] || [ -d ~/.claude/plugins/cache/openai-codex/codex ]) && echo "codex:installed" || echo "codex:missing"
([ -d ~/.claude/skills/dispatching-parallel-agents ] || [ -d ~/.claude/plugins/cache/claude-plugins-official/superpowers ]) && echo "superpowers:installed" || echo "superpowers:missing"
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
| morph | Step 5 will auto-configure it — free plan, no API key needed |
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
Copy skills from the local plugin cache (already downloaded when you ran `/plugin install` previously), falling back to a direct GitHub clone:
```bash
CACHE="$HOME/.claude/plugins/cache/compound-engineering-plugin/compound-engineering"
if [ -d "$CACHE" ]; then
  LATEST=$(ls -t "$CACHE" | head -1)
  cp -r "$CACHE/$LATEST/skills/." "$HOME/.claude/skills/"
  echo "✓ compound-engineering installed from cache (v$LATEST)"
else
  TMP=$(mktemp -d)
  git clone --depth=1 https://github.com/EveryInc/compound-engineering-plugin.git "$TMP/ce" 2>&1 | tail -2
  cp -r "$TMP/ce/skills/." "$HOME/.claude/skills/"
  rm -rf "$TMP"
  echo "✓ compound-engineering installed from GitHub"
fi
```

**firecrawl:**
```bash
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official/firecrawl"
if [ -d "$CACHE" ]; then
  LATEST=$(ls -t "$CACHE" | head -1)
  cp -r "$CACHE/$LATEST/skills/." "$HOME/.claude/skills/"
  echo "✓ firecrawl installed from cache (v$LATEST)"
else
  TMP=$(mktemp -d)
  git clone --depth=1 https://github.com/anthropics/claude-plugins-official.git "$TMP/cp" 2>&1 | tail -2
  cp -r "$TMP/cp/firecrawl/skills/." "$HOME/.claude/skills/"
  rm -rf "$TMP"
  echo "✓ firecrawl installed from GitHub"
fi
```

**codex:**
```bash
CACHE="$HOME/.claude/plugins/cache/openai-codex/codex"
if [ -d "$CACHE" ]; then
  LATEST=$(ls -t "$CACHE" | head -1)
  cp -r "$CACHE/$LATEST/skills/." "$HOME/.claude/skills/"
  echo "✓ codex installed from cache (v$LATEST)"
else
  TMP=$(mktemp -d)
  git clone --depth=1 https://github.com/openai/codex-plugin-cc.git "$TMP/codex" 2>&1 | tail -2
  cp -r "$TMP/codex/skills/." "$HOME/.claude/skills/"
  rm -rf "$TMP"
  echo "✓ codex installed from GitHub"
fi
```

**superpowers:**
```bash
CACHE="$HOME/.claude/plugins/cache/claude-plugins-official/superpowers"
if [ -d "$CACHE" ]; then
  LATEST=$(ls -t "$CACHE" | head -1)
  cp -r "$CACHE/$LATEST/skills/." "$HOME/.claude/skills/"
  echo "✓ superpowers installed from cache (v$LATEST)"
else
  TMP=$(mktemp -d)
  git clone --depth=1 https://github.com/anthropics/claude-plugins-official.git "$TMP/cp" 2>&1 | tail -2
  cp -r "$TMP/cp/superpowers/skills/." "$HOME/.claude/skills/"
  rm -rf "$TMP"
  echo "✓ superpowers installed from GitHub"
fi
```

After all selected installs complete, re-run the Step 0 detection checks and show an updated gap table so the user sees what is now ready.

Continue to Step 0c regardless of outcomes.

### Step 0c — Confirm ANTHROPIC_API_KEY (only if graphify is installed or was just installed)

Check if graphify is present and if the key is already in the shell profile:
```bash
command -v graphify > /dev/null 2>&1 && echo "graphify:present" || echo "graphify:absent"
grep -r "ANTHROPIC_API_KEY" ~/.zshrc ~/.zprofile ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null | grep -v "^Binary" | grep -q . && echo "key:present" || echo "key:absent"
```

- If graphify is absent → skip this step silently.
- If graphify is present and key is already set → skip this step silently.
- If graphify is present and key is NOT set → ask once using `AskUserQuestion`:

  > "Graphify needs ANTHROPIC_API_KEY to build the knowledge graph (Claude Code's OAuth key doesn't carry over). Add it to your shell profile now?"
  > [y] Yes — paste my key now
  > [l] Add later — I'll set it up manually (graphify won't build graphs until then)

Store the user's choice as `api_key_choice`. Continue to Step 1.

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

### Step 4 — Set ANTHROPIC_API_KEY (if chosen in Step 0c)

If `api_key_choice` is not "y" or Step 0c was skipped → skip this step silently.

If `api_key_choice` is "y":
- Ask: "Paste your ANTHROPIC_API_KEY (starts with sk-ant-):"
- Detect the active shell profile in this order: `~/.zprofile`, `~/.zshrc`, `~/.bash_profile`, `~/.bashrc`, `~/.profile` — use the first one that exists
- Append to that file:
  ```bash
  export ANTHROPIC_API_KEY=<key they pasted>
  ```
- Confirm: "Added to <profile path>. Run `source <profile path>` or open a new terminal for it to take effect."

### Step 5 — Auto-configure Morph MCP server (free plan)

Check if Morph is already configured in `~/.claude.json`:
```bash
jq -e '.mcpServers["morph-mcp"]' ~/.claude.json > /dev/null 2>&1 && echo "configured" || echo "missing"
```

If already configured, skip this step silently.

If NOT configured, auto-configure it now — no API key required for the free plan:

```bash
[ -f ~/.claude.json ] || echo '{"mcpServers":{}}' > ~/.claude.json
jq '.mcpServers["morph-mcp"] = {
  "type": "stdio",
  "command": "npx",
  "args": ["--prefer-offline", "-y", "@morphllm/morphmcp@latest"],
  "env": {
    "DISABLED_TOOLS": ""
  }
}' ~/.claude.json > /tmp/sarthi-claude-tmp.json && mv /tmp/sarthi-claude-tmp.json ~/.claude.json
```

Confirm: "Morph MCP configured (free plan). Active after you restart Claude Code."

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

### Step 9 — Confirm to the user

After completing the above, report clearly what was done and what was skipped (already configured). Use this format:

```
Sarthi setup complete.

✓ SessionStart hook           — added to ~/.claude/settings.json
✓ PostToolUse hook (graphify)  — added to ~/.claude/settings.json
✓ PostToolUse hook (intent)   — added to ~/.claude/settings.json
✓ UserPromptSubmit hook       — added to ~/.claude/settings.json
✓ Morph MCP (free plan)       — configured in ~/.claude.json
✓ Prompt optimizer            — enabled
✓ Session monitor             — enabled
✓ Model advisor               — enabled
✓ Pre-commit scan             — installed (~/.claude/.sarthi-hooks/pre-commit)
✓ ANTHROPIC_API_KEY           — added to ~/.zprofile
✓ codeburn menubar            — launched

Restart Claude Code (or open a new session) for the hooks to take effect.
```

Status variants:
- Already configured before setup → `— already configured`
- codeburn not installed → `— codeburn not installed, skipped`
- ANTHROPIC_API_KEY skipped by user → `— skipped (add manually: export ANTHROPIC_API_KEY=sk-ant-... in your shell profile)`
- ANTHROPIC_API_KEY already in profile → `— already configured`
- Advisor already enabled before setup → `— already enabled`
- Pre-commit scan already installed → `— already installed`

### Important

- Never overwrite existing hooks — always merge using jq so existing configuration is preserved
- If `~/.claude/settings.json` has invalid JSON, stop and tell the user: "~/.claude/settings.json has invalid JSON. Fix it first, then re-run /sarthi-setup."
- Do not proceed with any step if a previous step failed
