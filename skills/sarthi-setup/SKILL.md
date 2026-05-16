---
name: sarthi-setup
description: One-time setup for Sarthi. Automatically configures the SessionStart hook, PostToolUse graphify hook, and codeburn menubar. Run once after installing Sarthi.
---

# Sarthi Setup

Run this skill once after installing Sarthi. It configures everything automatically so you never need to touch a config file manually.

## What this does

1. Adds the Sarthi SessionStart hook to `~/.claude/settings.json`
2. Adds the graphify PostToolUse hook to `~/.claude/settings.json`
3. Installs codeburn menubar (if codeburn is installed)
4. Optionally sets `ANTHROPIC_API_KEY` in your shell profile (needed for graphify; skippable)
5. Optionally configures the Morph MCP server in `~/.claude.json` (enables fast bulk edits; skippable)
6. Optionally enables the prompt optimizer, session monitor, and model advisor (opt-in advisors)
7. Optionally installs a global pre-commit hook that scans staged files for hardcoded secrets before every git commit

## Steps

### Step 0 — Detect tool gaps and show install table

Before configuring anything, check which Sarthi-compatible tools are installed vs. missing. This surfaces what to install to unlock full routing value.

```bash
command -v graphify > /dev/null 2>&1 && echo "graphify:installed" || echo "graphify:missing"
command -v codeburn > /dev/null 2>&1 && echo "codeburn:installed" || echo "codeburn:missing"
jq -e '.mcpServers["morph-mcp"]' ~/.claude.json > /dev/null 2>&1 && echo "morph:configured" || echo "morph:missing"
[ -d ~/.claude/skills/firecrawl ] && echo "firecrawl:installed" || echo "firecrawl:missing"
[ -d ~/.claude/skills/compound-engineering ] && echo "compound:installed" || echo "compound:missing"
[ -d ~/.claude/skills/codex ] && echo "codex:installed" || echo "codex:missing"
[ -d ~/.claude/skills/superpowers ] && echo "superpowers:installed" || echo "superpowers:missing"
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
| graphify | `npm install -g graphify-cli` (see github.com/janwilmake/graphify) |
| codeburn | see getcodeburn.com |
| morph | get API key at morphllm.com — Step 5 below will configure it |
| firecrawl | install the Firecrawl skill plugin |
| compound-engineering | install the compound-engineering skill plugin |
| codex | install the codex skill plugin |
| superpowers | install the superpowers skill plugin |

If all tools are already installed, show: "All Sarthi tools detected — no gaps found." and skip to Step 1.

### Step 0b — Interactive installation of missing tools

If any tools are missing, offer to install them now. Load `AskUserQuestion` via `ToolSearch` with `select:AskUserQuestion`, then present only the missing tools as multi-select options:

> "Which missing tools would you like to set up now? (I'll handle what I can automatically — select all that apply)"

Wait for the user's selection. If nothing selected or skipped — continue to Step 1.

For each selected tool, attempt setup in this order:

**graphify:**
```bash
npm install -g graphify-cli 2>&1
```
Confirm success or surface the error. If npm is unavailable: "npm required — install Node.js from nodejs.org first, then re-run /sarthi-setup."

**codeburn:**
Show: "Visit **getcodeburn.com** for install instructions. Once `codeburn` is on your PATH, re-run `/sarthi-setup` to confirm detection."

**morph (MCP):**
Show: "Morph needs an API key — skipping to Step 5 which handles this interactively." (Step 5 of this setup already covers the full Morph MCP configuration flow.)

**firecrawl / compound-engineering / codex / superpowers (skill plugins):**
For each selected skill plugin, show:
```
[tool] is a Claude Code skill plugin.
To install:
  1. Find the plugin's GitHub repo (search: "claude-code [tool] skill")
  2. Copy its skills/[tool]/ directory to ~/.claude/skills/[tool]/
  3. Re-run /sarthi-setup to confirm detection.
```
(Install paths vary per plugin — this step cannot automate them without known repo URLs.)

After attempting all selected installs, re-run the Step 0 detection checks and show an updated gap table so the user sees what is now ready.

Continue to Step 1 regardless of outcomes.

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

### Step 4 — Set up ANTHROPIC_API_KEY for graphify (optional)

If graphify is installed, check whether `ANTHROPIC_API_KEY` is already exported:
```bash
grep -r "ANTHROPIC_API_KEY" ~/.zshrc ~/.zprofile ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null | grep -v "^$"
```

If it is already set, skip this step silently.

If it is NOT set, ask the user:

```
Graphify needs its own ANTHROPIC_API_KEY to build the knowledge graph.
(Claude Code uses OAuth — that key doesn't carry over to the graphify CLI.)

Would you like to add it to your shell profile now?
  [y] Yes — paste your key and I'll add it to ~/.zprofile (or your active profile)
  [s] Skip — I'll set it up manually later

Your choice (y/s):
```

If the user chooses **y**:
- Ask: "Paste your ANTHROPIC_API_KEY (starts with sk-ant-):"
- Detect the active shell profile in this order: `~/.zprofile`, `~/.zshrc`, `~/.bash_profile`, `~/.bashrc`, `~/.profile` — use the first one that exists
- Append to that file:
  ```bash
  export ANTHROPIC_API_KEY=<key they pasted>
  ```
- Confirm: "Added to <profile path>. Run `source <profile path>` or open a new terminal for it to take effect."

If the user chooses **s**:
- Show: "Skipped. You can add it manually later: `export ANTHROPIC_API_KEY=sk-ant-...` in your shell profile."
- Continue to next step.

### Step 5 — Set up Morph MCP server (optional)

Check if Morph is already configured in `~/.claude.json`:
```bash
jq -e '.mcpServers["morph-mcp"]' ~/.claude.json > /dev/null 2>&1 && echo "configured" || echo "missing"
```

If already configured, skip this step silently.

If NOT configured, ask the user:

```
Morph enables fast bulk code edits via MCP — useful for refactors and renames across many files.

Would you like to set it up now?
  [y] Yes — paste your Morph API key and I'll configure it
  [s] Skip — I'll set it up manually later (see morphllm.com)

Your choice (y/s):
```

If the user chooses **y**:
- Ask: "Paste your Morph API key (get one at morphllm.com):"
- Ensure `~/.claude.json` exists before writing:
```bash
[ -f ~/.claude.json ] || echo '{"mcpServers":{}}' > ~/.claude.json
```
- Add the MCP server entry to `~/.claude.json` using jq:
```bash
jq '.mcpServers["morph-mcp"] = {
  "type": "stdio",
  "command": "npx",
  "args": ["--prefer-offline", "-y", "@morphllm/morphmcp@latest", "--api-key", "<key they pasted>"],
  "env": {
    "MORPH_API_KEY": "<key they pasted>",
    "DISABLED_TOOLS": ""
  }
}' ~/.claude.json > /tmp/sarthi-claude-tmp.json && mv /tmp/sarthi-claude-tmp.json ~/.claude.json
```
- Confirm: "Morph MCP configured in ~/.claude.json. It will be active after you restart Claude Code."

If the user chooses **s**:
- Show: "Skipped. Get a Morph API key at morphllm.com and re-run /sarthi-setup to add it."
- Continue to next step.

### Step 6 — Enable Sarthi advisors (opt-in)

Check which are already enabled:
```bash
[ -f ~/.claude/.sarthi-prompt-optimizer-enabled ] && echo "optimizer:on" || echo "optimizer:off"
[ -f ~/.claude/.sarthi-session-monitor-enabled ] && echo "monitor:on" || echo "monitor:off"
[ -f ~/.claude/.sarthi-model-advisor-enabled ] && echo "advisor:on" || echo "advisor:off"
```

If all three are already enabled, skip this step silently.

If any are not enabled, ask:

```
Sarthi includes three optional advisors — each is non-blocking and can be turned off individually:

  Prompt optimizer  — detects vague asks, missing deliverables, scope creep; suggests a tighter reword
  Session monitor   — warns at ~90% and ~100% context fill (twice per session, never more)
  Model advisor     — suggests Haiku / Sonnet / Opus based on task complexity

  [y] Enable all three
  [n] Skip all
  [c] Choose individually

Your choice (y/n/c):
```

**If [y] — enable all:**
```bash
touch ~/.claude/.sarthi-prompt-optimizer-enabled
touch ~/.claude/.sarthi-session-monitor-enabled
touch ~/.claude/.sarthi-model-advisor-enabled
```
Confirm: "All three advisors enabled."

**If [n] — skip all:**
Show: "Skipped. Enable individually any time:
  `touch ~/.claude/.sarthi-prompt-optimizer-enabled`
  `touch ~/.claude/.sarthi-session-monitor-enabled`
  `touch ~/.claude/.sarthi-model-advisor-enabled`"

**If [c] — choose individually:**
For each advisor that is not already enabled, ask in sequence:

*Prompt optimizer:*
```
Prompt optimizer — assesses prompts for inefficiency signals and suggests rewording.
Learns from accept/reject decisions. Fires only when 2+ signals are present.
  [y] Enable  [s] Skip
```
If y: `touch ~/.claude/.sarthi-prompt-optimizer-enabled`

*Session monitor:*
```
Session monitor — warns at ~90% context (suggests /compact) and ~100% (recommends fresh session).
Fires at most twice per session.
  [y] Enable  [s] Skip
```
If y: `touch ~/.claude/.sarthi-session-monitor-enabled`

*Model advisor:*
```
Model advisor — before each task, suggests Haiku / Sonnet / Opus based on complexity.
Learns from your choices. Rejects twice → silent for the session.
  [y] Enable  [s] Skip
```
If y: `touch ~/.claude/.sarthi-model-advisor-enabled`

### Step 7 — Install pre-commit secrets scan (opt-in)

Check if already configured:
```bash
[ -f ~/.claude/.sarthi-hooks/pre-commit ] && echo "configured" || echo "missing"
```

If already configured, skip this step silently.

If NOT configured, ask:

```
Pre-commit secrets scan — scans staged files for hardcoded API keys, tokens,
and private keys before every git commit. Blocks the commit if matches are found.
Applies globally to all git repos on this machine.

  [y] Yes — install global pre-commit hook
  [s] Skip — I'll handle secrets scanning another way

Your choice (y/s):
```

If the user chooses **y**:

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

Confirm: "Pre-commit secrets scan installed globally. Staged files will be checked before every git commit. To disable: `git config --global --unset core.hooksPath`"

If the user chooses **s**:
- Show: "Skipped. Install any time by re-running `/sarthi-setup`."

### Step 8 — Install codeburn menubar

If codeburn is installed and menubar is not already running:
```bash
codeburn menubar &
```

### Step 9 — Confirm to the user

After completing the above, report clearly what was done and what was skipped (already configured). Use this format:

```
Sarthi setup complete.

✓ SessionStart hook          — added to ~/.claude/settings.json
✓ PostToolUse hook (graphify) — added to ~/.claude/settings.json
✓ PostToolUse hook (intent)  — added to ~/.claude/settings.json
✓ UserPromptSubmit hook      — added to ~/.claude/settings.json
✓ ANTHROPIC_API_KEY          — added to ~/.zprofile
✓ Morph MCP                  — configured in ~/.claude.json
✓ Prompt optimizer           — enabled
✓ Session monitor            — enabled
✓ Model advisor              — enabled
✓ Pre-commit scan            — installed (~/.claude/.sarthi-hooks/pre-commit)
✓ codeburn menubar           — launched

Restart Claude Code (or open a new session) for the hooks to take effect.
```

If something was already configured, show `— already configured` instead of `— added`.
If codeburn is not installed, show `— codeburn not installed, skipped`.
If the user skipped the API key step, show `— skipped (set manually later)`.
If ANTHROPIC_API_KEY was already in their profile, show `— already configured`.
If the user skipped Morph, show `— skipped (morphllm.com to set up later)`.
If Morph was already configured, show `— already configured`.
For each advisor (prompt optimizer, session monitor, model advisor):
- If enabled in this run, show `— enabled`
- If already enabled before setup, show `— already enabled`
- If skipped, show `— skipped (touch ~/.claude/.<flag-file> to enable)`
If the user skipped pre-commit scan, show `— skipped (re-run /sarthi-setup to install)`.
If pre-commit scan was already installed, show `— already installed`.

### Important

- Never overwrite existing hooks — always merge using jq so existing configuration is preserved
- If `~/.claude/settings.json` has invalid JSON, stop and tell the user: "~/.claude/settings.json has invalid JSON. Fix it first, then re-run /sarthi-setup."
- Do not proceed with any step if a previous step failed
