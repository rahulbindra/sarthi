---
name: sarthi-model-advisor
description: Opt-in model advisor. Before routing, assesses task complexity and suggests the most token-efficient Claude model (Haiku / Sonnet / Opus). Learns from accept/reject decisions. Only active if ~/.claude/.sarthi-model-advisor-enabled exists. Never blocks the task.
---

# Sarthi Model Advisor

Assesses task complexity and suggests the most token-efficient Claude model before routing. A suggestion only appears when the current model is sub-optimal for the task. Learns from user responses over time.

**Guard:** Only runs if `~/.claude/.sarthi-model-advisor-enabled` exists. If not, skip entirely.

---

## Model reference

| Model | ID | Best for | Relative cost |
|-------|----|----------|---------------|
| Haiku 4.5 | `claude-haiku-4-5-20251001` | Simple, fast, single-concern tasks | Lowest |
| Sonnet 4.6 | `claude-sonnet-4-6` | Standard development work | Medium |
| Opus 4.7 | `claude-opus-4-7` | Complex reasoning, architecture, multi-system | Highest |

> Model IDs verified against the Claude Code environment at time of writing. Haiku uses a dated suffix; Sonnet and Opus do not — this reflects the actual API identifiers, not a typo. Update these when new model versions release.

---

## Step 1 — Check if enabled and load learnings

```bash
[ -f ~/.claude/.sarthi-model-advisor-enabled ] && echo "enabled" || echo "disabled"
```

If disabled, exit immediately.

Load learnings:
```bash
cat ~/.claude/.sarthi-model-learnings.json 2>/dev/null || echo "{}"
```

After loading, **reset `session_consecutive_rejects` to 0** in-memory — this counter is per-session only and must not carry forward from previous sessions. Transition preferences and totals are persisted; session state is not.

---

## Step 2 — Detect current model

The current model is the one this session was started with. Infer it from session context (Claude knows its own model). Map to: `haiku`, `sonnet`, or `opus`.

---

## Step 2b — Skip conditions

**Skip** (exit silently) only if the message clearly has no task implied:

- **Pure factual or opinion question** — "how would you rate", "what do you think", "explain X", "why did X", "what is X", "is there a downside", "what's the difference", "does X work"
- **Pure acknowledgment with no pending task** — "ok", "got it", "I see", "makes sense", "thanks" — and the last 3 turns contain no proposed task waiting for approval
- **Already assessed this turn** — never suggest twice for the same message

**Never skip** for:

- Any message requesting an edit, fix, audit, creation, or diagram change — regardless of length
- A short reply ("yes", "both", "go ahead", "sure") when the last 2–3 turns contain a pending task proposal — assess the **proposed task's complexity** instead of the reply itself

**Short reply rule:** If the message is under 5 words and is approving a previously proposed task, assess the complexity of that task (from the last 3 turns), not the reply. Only skip if the context also contains no pending task.

---

## Step 3 — Assess task complexity

Score the task against complexity signals to determine the recommended model tier.

### Haiku signals (simple — low complexity)
- Single file edit, single function change
- Typo, formatting, or rename fix
- Simple factual question or lookup
- Grep or file search request
- Copying, moving, or deleting a file
- Generating a short boilerplate snippet
- Single-step task with a clear, unambiguous outcome

### Sonnet signals (medium — standard complexity) — default
- Multi-file feature implementation
- Debugging with moderate context (single service/module)
- Writing or updating tests
- Code review of a focused PR
- Refactoring within a bounded scope
- Codebase navigation with graphify
- Most standard day-to-day development tasks

### Opus signals (complex — high complexity)
- Architecture design or major system decisions
- Debugging across multiple services or systems
- Deep reasoning tasks (root cause of subtle bugs)
- Strategic planning, roadmap, or product decisions (`/sarthi-pm`)
- Security or vulnerability audit with parallel agents
- Cross-repo or large codebase analysis
- Tasks requiring synthesis of many conflicting constraints
- Multi-step plans with significant unknowns

**Scoring rule:** Count the number of matching signals per tier. Assign the task to the tier with the most signals. If tied, prefer Sonnet as the safe default.

---

## Step 4 — Decide whether to suggest

Only suggest if **current model ≠ recommended model AND the mismatch is meaningful:**

| Current | Recommended | Suggest? | Reason |
|---------|-------------|----------|--------|
| Opus | Haiku | Yes | Paying Opus rates for a simple task |
| Opus | Sonnet | Yes | Paying Opus rates for standard work |
| Sonnet | Haiku | Yes | Haiku would handle this faster and cheaper |
| Sonnet | Opus | Yes | Task complexity warrants deeper reasoning |
| Haiku | Sonnet | Yes | Task may exceed Haiku's reasoning depth |
| Haiku | Opus | Yes | Complex task — Haiku likely to struggle |
| Any | Same | No | Already on the right model — skip silently |

Also apply learnings: if the suggested model transition has been rejected 2+ times with a similar task type, suppress the suggestion.

---

## Step 5 — Present suggestion

```
🤖 Model suggestion:

Task complexity: [simple / medium / complex]
Current model:   [current model name]
Suggested model: [recommended model name] — [one-line reason]

To switch before this task:
  /model [model-id]

[y] Note taken — I'll switch  [s] Skip  [r] Skip — tell me why (one line)
```

Wait for response. The task **always proceeds** after the response regardless of choice — Sarthi cannot switch the model itself.

---

## Step 6 — Handle response and save learnings

**If [y] — accepted:**
- Note: "Switching to [model]. Remember to run `/model [id]` now."
- Update learnings: increment `accepted` for the detected signals and transition pair
- Reset `session_consecutive_rejects` to 0

**If [s] — skipped:**
- Route with no comment
- Increment `session_consecutive_rejects` by 1
- If >= 2: suppress for the rest of the session, note once:
  > "Got it — no more model suggestions this session. Run `/sarthi-model-advisor reset` to re-enable."

**If [r] — skipped with reason:**
- Route with no comment
- Save reason alongside the rejected transition pair
- Increment `session_consecutive_rejects` by 1
- Apply session suppression check (same as above)

Write updated learnings to `~/.claude/.sarthi-model-learnings.json`:

```json
{
  "version": 1,
  "last_updated": "<today's date>",
  "session_consecutive_rejects": 0,
  "transitions": {
    "opus_to_haiku":   { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "opus_to_sonnet":  { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "sonnet_to_haiku": { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "sonnet_to_opus":  { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "haiku_to_sonnet": { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "haiku_to_opus":   { "accepted": 0, "rejected": 0, "last_reject_reason": "" }
  },
  "total_accepted": 0,
  "total_rejected": 0,
  "total_skipped": 0
}
```

---

## Slash commands

**`/sarthi-model-advisor status`**
```
Model advisor — status

  Enabled:    yes
  Suggested:  9 times
  Accepted:   6  (67%)
  Rejected:   2  (with reasons)
  Skipped:    1

  Most accepted: opus→sonnet (4/4) — you use Opus by default but often work on standard tasks
  Most rejected: sonnet→haiku (2/3) — "I prefer Sonnet even for simple tasks"

  Session suppression: inactive
```

**`/sarthi-model-advisor reset`**
Clears `session_consecutive_rejects` and re-enables suggestions for this session.

**`/sarthi-model-advisor off`**
```bash
rm ~/.claude/.sarthi-model-advisor-enabled
```

**`/sarthi-model-advisor clear`**
```bash
rm ~/.claude/.sarthi-model-learnings.json
```
