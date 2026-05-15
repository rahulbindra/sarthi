---
name: sarthi-session-monitor
description: Opt-in session length monitor. Warns once at ~90% context fill (suggests /compact) and once at ~100% (recommends fresh session). Fires at most twice per session. Only active if ~/.claude/.sarthi-session-monitor-enabled exists.
---

# Sarthi Session Monitor

Estimates context fill from conversation depth and nudges the user before Claude's reasoning quality degrades. Fires at most twice per session — never more.

**Guard:** Only runs if `~/.claude/.sarthi-session-monitor-enabled` exists. If not, skip entirely.

**Note:** codeburn tracks daily/monthly spend totals — it does not expose per-session token counts and is not used here. Context fill is estimated from conversation signals only.

---

## Context window reference

All current Claude models share a 200k token context window.

| Threshold | Tokens | Action |
|-----------|--------|--------|
| 90% mark | ~180k | Suggest `/compact` or new session |
| 100% mark | ~200k | Recommend fresh session with handoff checklist |

---

## Step 1 — Check if enabled and load history

```bash
[ -f ~/.claude/.sarthi-session-monitor-enabled ] && echo "enabled" || echo "disabled"
```

If disabled, exit immediately.

Load monitor history to understand the user's past response patterns:
```bash
cat ~/.claude/.sarthi-monitor-log.jsonl 2>/dev/null | tail -20
```

From the last 10 entries, compute:
- `compact_rate` — fraction of `warned_90` entries where a subsequent `compact_ran: true` entry appears within the same session date
- `ignored_rate` — fraction of warnings with no follow-up action logged

Use these to adapt the warning tone (see Step 3).

---

## Step 2 — Estimate context fill from conversation signals

Claude has direct awareness of its own context state. Self-assess fill using these signals in combination:

**Conversation depth proxies:**
- Count of message exchanges in this session (each exchange ≈ 800–2,000 tokens with tool calls)
- Number of large tool outputs (file reads, bash output, grep results) — each adds 1k–10k tokens
- Number of file edits made this session — each Write/Edit cycle adds context
- Whether `/compact` has already been run this session (resets the baseline)

**Rough token estimates:**
| Session shape | Estimated tokens |
|--------------|-----------------|
| < 20 short exchanges, few tool calls | < 50k — low |
| 20–40 exchanges, moderate tool use | 50k–120k — medium |
| 40–60 exchanges, heavy tool use | 120k–170k — approaching limit |
| 60+ exchanges or very large tool outputs | 170k+ — near/at limit |

Use Claude's own sense of context saturation as the primary signal. If the conversation feels long and deep — it is. Do not over-engineer the estimate; a directional read is sufficient.

Output: `low`, `approaching` (~90%), or `full` (~100%).

---

## Step 3 — Check thresholds and session marks

Track two marks in session memory (not persisted to disk — resets when session ends):
- `warned_90` — 90% nudge already fired this session
- `warned_100` — 100% nudge already fired this session

**If both marks already fired** — exit silently. Never fire a third time.

**At `approaching` (~90%)** and `warned_90` is false:

Set `warned_90 = true`. Log the warning:
```bash
python3 -c "
import json, os
from datetime import datetime, timezone
entry = json.dumps({'ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'event': 'warned_90', 'compact_ran': False})
open(os.path.expanduser('~/.claude/.sarthi-monitor-log.jsonl'), 'a').write(entry + '\n')
" 2>/dev/null || true
```

Show (adapt tone based on history — if `ignored_rate > 0.7`, lead with stronger urgency; if `compact_rate > 0.7`, lead with `/compact` as the obvious choice):
```
⚠️  Session approaching context limit (~90% full).

Claude's reasoning quality degrades as context fills.
Options:
  /compact    — compress conversation history in place (free, continues this session)
  New session — fresh start with full context (best for complex remaining work)

Your current task will proceed — this is just a heads-up.
```

If the user runs `/compact` after this warning, update the log entry to `compact_ran: true`:
```bash
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/.sarthi-monitor-log.jsonl')
lines = open(path).readlines()
for i in range(len(lines)-1, -1, -1):
    e = json.loads(lines[i])
    if e.get('event') == 'warned_90' and not e.get('compact_ran'):
        e['compact_ran'] = True
        lines[i] = json.dumps(e) + '\n'
        break
open(path, 'w').writelines(lines)
" 2>/dev/null || true
```

**At `full` (~100%)** and `warned_100` is false:

Set `warned_100 = true`. Log the warning:
```bash
python3 -c "
import json, os
from datetime import datetime, timezone
entry = json.dumps({'ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'event': 'warned_100'})
open(os.path.expanduser('~/.claude/.sarthi-monitor-log.jsonl'), 'a').write(entry + '\n')
" 2>/dev/null || true
```

Show:
```
🔴  Session at context capacity (~100% full).

Response quality is likely degraded. A fresh session is strongly recommended.

To hand off cleanly:
  1. Run /revise-claude-md (if installed) to save key decisions to CLAUDE.md
  2. Note your current task so you can resume it
  3. Open a new Claude Code session and paste your task

Your current task will still proceed — but consider the above first.
```

**At `low`** — exit silently, no nudge.

---

## Notes

- Both nudges are non-blocking. The current task always proceeds regardless.
- Marks are per-session only — a new Claude Code session resets them naturally.
- If `/compact` has been run this session, reset the fill estimate to `low` and reset `warned_90` (the 90% mark can fire again after compaction, since the context has genuinely reset).
