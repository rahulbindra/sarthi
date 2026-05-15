---
name: sarthi-session-monitor
description: Opt-in session length monitor. Warns once at 90% context fill (suggests /compact) and once at 100% (recommends fresh session). Fires at most twice per session, never more. Only active if ~/.claude/.sarthi-session-monitor-enabled exists.
---

# Sarthi Session Monitor

Tracks estimated context fill and nudges the user before Claude performance degrades. Fires at most twice per session — at the 90% and 100% marks. Never repeats a mark already warned.

**Guard:** Only runs if `~/.claude/.sarthi-session-monitor-enabled` exists. If not, skip entirely.

---

## Context window reference

| Model | Context limit | 90% mark | 100% mark |
|-------|--------------|----------|-----------|
| claude-haiku-4-5 | 200k tokens | ~180k | 200k |
| claude-sonnet-4-6 | 200k tokens | ~180k | 200k |
| claude-opus-4-7 | 200k tokens | ~180k | 200k |

All current Claude models share a 200k token context window.

---

## Step 1 — Check if enabled

```bash
[ -f ~/.claude/.sarthi-session-monitor-enabled ] && echo "enabled" || echo "disabled"
```

If disabled, exit immediately.

---

## Step 2 — Estimate context fill

**If codeburn is installed:**
```bash
codeburn status --json 2>/dev/null | python3 -c "
import sys, json
d = json.load(sys.stdin)
tokens = d.get('current_session', {}).get('total_tokens', 0)
pct = round((tokens / 200000) * 100, 1)
print(f'tokens:{tokens} pct:{pct}')
" 2>/dev/null || echo "codeburn:unavailable"
```

**If codeburn is unavailable**, self-assess using conversation signals:
- Count approximate message exchanges in this session
- Estimate average tokens per exchange (~800 tokens for a typical back-and-forth with tool calls)
- Multiply to get rough total
- Flag as estimate: prefix result with `estimated:`

If the fill cannot be determined at all, skip this check silently.

---

## Step 3 — Check thresholds and session marks

Read session marks from in-memory state (tracked as variables within this session only — not persisted to disk since they reset naturally when a new session starts):

- `warned_90` — whether the 90% nudge has already fired this session
- `warned_100` — whether the 100% nudge has already fired this session

**At 90–99% fill** (and `warned_90` is false):

Set `warned_90 = true`. Show:

```
⚠️  Session at ~90% context capacity.

Claude's reasoning quality degrades as the context window fills.
Options:
  /compact     — compress conversation history in place (continues this session)
  New session  — fresh start with full context (most effective for complex remaining work)

Your current task will proceed — this is just a heads-up.
```

Then proceed with routing the current task normally.

**At 100%+ fill** (and `warned_100` is false):

Set `warned_100 = true`. Show:

```
🔴  Session at full context capacity.

Response quality is likely degraded. Starting a new session is strongly recommended.

To hand off cleanly:
  1. Run /revise-claude-md (if installed) to save any key decisions
  2. Note your current task: "[current task description]"
  3. Open a new Claude Code session
  4. Paste your task and any relevant context

Your current task will still proceed — but consider the above before continuing.
```

Then proceed with routing the current task normally.

**Below 90%** — no nudge, exit silently.

**After both marks have fired** — exit silently for the remainder of the session. Never fire a third time.

---

## Notes

- Both nudges are **non-blocking** — they appear as warnings, not gates. The current task always proceeds.
- The marks are per-session only. A new Claude Code session resets both to false automatically.
- If context fill is estimated (no codeburn), use slightly conservative thresholds: warn at 80% for the first nudge, 95% for the second, to account for estimation error.
