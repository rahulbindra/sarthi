---
name: sarthi-prompt-optimizer
description: Opt-in prompt assessment layer. Before routing any task, checks for token-inefficiency signals and suggests a tighter reword. Learns from user accept/reject decisions over time. Only active if ~/.claude/.sarthi-prompt-optimizer-enabled exists. Never blocks the task — always skippable.
---

# Sarthi Prompt Optimizer

Assesses the user's prompt for token-inefficiency signals before routing. Suggests a reword if one would meaningfully reduce clarifying round trips or wasted work. Learns from user responses over time.

**Guard:** Only runs if `~/.claude/.sarthi-prompt-optimizer-enabled` exists. If not, skip entirely.

---

## Step 1 — Check if enabled and load learnings

```bash
[ -f ~/.claude/.sarthi-prompt-optimizer-enabled ] && echo "enabled" || echo "disabled"
```

If disabled, exit immediately — do not assess or suggest anything.

If enabled, load learnings:
```bash
cat ~/.claude/.sarthi-prompt-learnings.json 2>/dev/null || echo "{}"
```

After loading, **reset `session_consecutive_rejects` to 0** in-memory — this counter is per-session only and must not carry forward from previous sessions. Pattern preferences (`patterns.*`) and totals are persisted across sessions; session state is not.

---

## Step 2 — Assess prompt for inefficiency signals

Score the prompt against these signals. A suggestion is only warranted if **2 or more** signals are present — never suggest for a single signal alone.

| Signal | Description | Examples |
|--------|-------------|---------|
| `vague_verb` | Action is unclear or generic | "fix this", "make it better", "clean up" |
| `missing_deliverable` | No concrete outcome stated | "look at the auth flow" |
| `multi_concern` | Multiple unrelated tasks in one prompt | "fix X and also update Y and check Z" |
| `repeated_context` | Re-explains something already established this session | Restates the tech stack, re-describes the bug already discussed |
| `scope_creep` | Adds unbounded scope | "while you're at it", "and anything else you notice", "quickly also" |
| `ambiguous_referent` | Unclear what "it", "this", "that" refers to | "fix it", "update this", "make that work" |
| `over_long` | Prompt is 200+ words but the core ask is buried | Wall of context with a one-line ask at the end |

If fewer than 2 signals → skip silently. Proceed to routing.

---

## Step 3 — Generate suggestion

Apply learnings to the suggestion:
- If a pattern has been rejected 2+ times with a reason → avoid that pattern in the suggestion
- If a pattern has been accepted 3+ times → prioritise that pattern

Produce a suggestion that:
- States one clear deliverable per task
- Splits multi-concern prompts into numbered separate asks
- Removes redundant context already in session
- Replaces ambiguous referents with specific names
- Keeps the suggestion ≤ 30 words longer than the original

Present it as:

```
💡 Token suggestion — your prompt may cause extra round trips:

Original:  "[original prompt]"
Suggested: "[reworded prompt]"

Why: [one line — e.g. "splits two unrelated tasks" / "adds missing deliverable" / "removes repeated context"]

[y] Use suggested  [s] Skip  [r] Skip — tell me why (one line)
```

Wait for response.

---

## Step 4 — Handle response and save to learnings

**If [y] — accepted:**
- Use the suggested prompt for routing (not the original)
- Update learnings:
  ```json
  { "signal_accepted": ["<signal1>", "<signal2>"], "count": +1 }
  ```
- Reset `session_consecutive_rejects` to 0

**If [s] — skipped silently:**
- Route with the original prompt
- Increment `session_consecutive_rejects` by 1
- Do not update pattern learnings (no signal — user may have just been in a hurry)

**If [r] — skipped with reason:**
- Route with the original prompt
- Capture the reason
- Update learnings:
  ```json
  {
    "signal_rejected": ["<signal1>", "<signal2>"],
    "reason": "<user's reason>",
    "count": +1
  }
  ```
- Increment `session_consecutive_rejects` by 1
- If `session_consecutive_rejects >= 2`: set `session_suppressed: true` and note:
  > "Got it — I'll hold suggestions for the rest of this session. Run `/sarthi-prompt-optimizer reset` to re-enable."

---

## Step 5 — Write updated learnings

Write back to `~/.claude/.sarthi-prompt-learnings.json`:

```json
{
  "version": 1,
  "last_updated": "<today's date>",
  "session_consecutive_rejects": <count>,
  "patterns": {
    "vague_verb":          { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "missing_deliverable": { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "multi_concern":       { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "repeated_context":    { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "scope_creep":         { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "ambiguous_referent":  { "accepted": 0, "rejected": 0, "last_reject_reason": "" },
    "over_long":           { "accepted": 0, "rejected": 0, "last_reject_reason": "" }
  },
  "total_accepted": 0,
  "total_rejected": 0,
  "total_skipped": 0
}
```

Merge with existing values — never overwrite fields not touched in this run.

---

## Slash commands

**`/sarthi-prompt-optimizer status`**
Show current learnings summary:
```
Prompt optimizer — status

  Enabled:   yes
  Suggested: 12 times this week
  Accepted:  8  (67%)
  Rejected:  3  (with reasons)
  Skipped:   1

  Strongest signal you accept: missing_deliverable (accepted 5/5)
  Signal you reject most:      over_long (rejected 2/3 — "I prefer context-rich prompts")

  Session suppression: inactive
```

**`/sarthi-prompt-optimizer reset`**
Clear `session_consecutive_rejects` and re-enable suggestions for this session.

**`/sarthi-prompt-optimizer off`**
```bash
rm ~/.claude/.sarthi-prompt-optimizer-enabled
```
Confirm: "Prompt optimizer disabled. Re-enable any time: `touch ~/.claude/.sarthi-prompt-optimizer-enabled`"

**`/sarthi-prompt-optimizer clear`**
```bash
rm ~/.claude/.sarthi-prompt-learnings.json
```
Confirm: "Learnings cleared. Optimizer will start fresh."
