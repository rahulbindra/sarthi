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
6. Optionally enables the prompt optimizer (opt-in; suggests token-efficient rewording before routing)
7. Optionally enables the session monitor (opt-in; warns at 90% and 100% context fill, twice per session)
8. Optionally enables the model advisor (opt-in; suggests Haiku/Sonnet/Opus based on task complexity)

## Steps

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

### Step 6 — Enable prompt optimizer (opt-in)

Check if already enabled:
```bash
[ -f ~/.claude/.sarthi-prompt-optimizer-enabled ] && echo "enabled" || echo "disabled"
```

If already enabled, skip this step silently.

If NOT enabled, ask the user:

```
Prompt optimizer — before routing each task, Sarthi can assess your prompt for
token-inefficiency signals (vague asks, missing deliverables, scope creep, etc.)
and suggest a tighter reword. It learns from whether you accept or reject suggestions.

Off by default. Enable it?
  [y] Yes — enable prompt optimizer
  [s] Skip — keep it off (you can enable later with /sarthi-prompt-optimizer)

Your choice (y/s):
```

If the user chooses **y**:
```bash
touch ~/.claude/.sarthi-prompt-optimizer-enabled
```
- Confirm: "Prompt optimizer enabled. It will suggest rewording when it detects 2+ inefficiency signals. Rejects twice in a row → silent for the session."

If the user chooses **s**:
- Show: "Skipped. Enable any time by running `/sarthi-prompt-optimizer` and choosing 'enable'."
- Continue to next step.

### Step 7 — Enable session monitor (opt-in)

Check if already enabled:
```bash
[ -f ~/.claude/.sarthi-session-monitor-enabled ] && echo "enabled" || echo "disabled"
```

If already enabled, skip this step silently.

If NOT enabled, ask the user:

```
Session monitor — warns you when your session is approaching its context limit,
before Claude's reasoning quality degrades.

  At 90%: suggests /compact or a new session (once)
  At 100%: recommends starting fresh (once)
  Never interrupts more than twice per session.

Enable it?
  [y] Yes — enable session monitor
  [s] Skip — keep it off

Your choice (y/s):
```

If the user chooses **y**:
```bash
touch ~/.claude/.sarthi-session-monitor-enabled
```
Confirm: "Session monitor enabled. You'll get one nudge at ~90% and one at 100% context fill."

If the user chooses **s**:
- Show: "Skipped. Enable any time: `touch ~/.claude/.sarthi-session-monitor-enabled`"

### Step 8 — Enable model advisor (opt-in)

Check if already enabled:
```bash
[ -f ~/.claude/.sarthi-model-advisor-enabled ] && echo "enabled" || echo "disabled"
```

If already enabled, skip this step silently.

If NOT enabled, ask the user:

```
Model advisor — before each task, assesses complexity and suggests the most
token-efficient Claude model (Haiku / Sonnet / Opus). Learns from your responses.

  Simple tasks  → suggests Haiku  (fastest, cheapest)
  Standard tasks → suggests Sonnet (default)
  Complex tasks  → suggests Opus   (deepest reasoning)

You can always skip a suggestion. Rejects twice → silent for the session.

Enable it?
  [y] Yes — enable model advisor
  [s] Skip — keep it off

Your choice (y/s):
```

If the user chooses **y**:
```bash
touch ~/.claude/.sarthi-model-advisor-enabled
```
Confirm: "Model advisor enabled. It suggests a model switch when the task complexity warrants it."

If the user chooses **s**:
- Show: "Skipped. Enable any time: `touch ~/.claude/.sarthi-model-advisor-enabled`"

### Step 9 — Install codeburn menubar

If codeburn is installed and menubar is not already running:
```bash
codeburn menubar &
```

### Step 10 — Confirm to the user

After completing the above, report clearly what was done and what was skipped (already configured). Use this format:

```
Sarthi setup complete.

✓ SessionStart hook     — added to ~/.claude/settings.json
✓ PostToolUse hook      — added to ~/.claude/settings.json
✓ ANTHROPIC_API_KEY     — added to ~/.zprofile
✓ Morph MCP             — configured in ~/.claude.json
✓ Prompt optimizer      — enabled
✓ Session monitor       — enabled
✓ Model advisor         — enabled
✓ codeburn menubar      — launched

Restart Claude Code (or open a new session) for the hooks to take effect.
```

If something was already configured, show `— already configured` instead of `— added`.
If codeburn is not installed, show `— codeburn not installed, skipped`.
If the user skipped the API key step, show `— skipped (set manually later)`.
If ANTHROPIC_API_KEY was already in their profile, show `— already configured`.
If the user skipped Morph, show `— skipped (morphllm.com to set up later)`.
If Morph was already configured, show `— already configured`.
If the user skipped prompt optimizer, show `— skipped (run /sarthi-prompt-optimizer to enable later)`.
If prompt optimizer was already enabled, show `— already enabled`.
If the user skipped session monitor, show `— skipped (touch ~/.claude/.sarthi-session-monitor-enabled to enable)`.
If session monitor was already enabled, show `— already enabled`.
If the user skipped model advisor, show `— skipped (touch ~/.claude/.sarthi-model-advisor-enabled to enable)`.
If model advisor was already enabled, show `— already enabled`.

### Important

- Never overwrite existing hooks — always merge using jq so existing configuration is preserved
- If `~/.claude/settings.json` has invalid JSON, stop and tell the user: "~/.claude/settings.json has invalid JSON. Fix it first, then re-run /sarthi-setup."
- Do not proceed with any step if a previous step failed
