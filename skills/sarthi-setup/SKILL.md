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
    "command": "[ -f graphify-out/graph.json ] && graphify update . > /dev/null 2>&1 || true"
  }]
}]' ~/.claude/settings.json > /tmp/sarthi-settings-tmp.json && mv /tmp/sarthi-settings-tmp.json ~/.claude/settings.json
```

### Step 4 — Install codeburn menubar

If codeburn is installed and menubar is not already running:
```bash
codeburn menubar &
```

### Step 5 — Confirm to the user

After completing the above, report clearly what was done and what was skipped (already configured). Use this format:

```
Sarthi setup complete.

✓ SessionStart hook     — added to ~/.claude/settings.json
✓ PostToolUse hook      — added to ~/.claude/settings.json
✓ codeburn menubar      — launched

Restart Claude Code (or open a new session) for the hooks to take effect.
```

If something was already configured, show `— already configured` instead of `— added`.
If codeburn is not installed, show `— codeburn not installed, skipped`.

### Important

- Never overwrite existing hooks — always merge using jq so existing configuration is preserved
- If `~/.claude/settings.json` has invalid JSON, stop and tell the user: "~/.claude/settings.json has invalid JSON. Fix it first, then re-run /sarthi-setup."
- Do not proceed with any step if a previous step failed
