---
name: sarthi-checks
description: Combined pre-task check — runs prompt optimizer and model advisor in a single skill call. Replaces two separate skill invocations with one.
---

# Sarthi Checks

Runs prompt optimizer and model advisor sequentially in one call. Exits silently if neither has anything to surface.

---

## Part 0 — Complexity pre-gate

**Run before Parts 1 and 2. Exit silently if the task is simple.**

Score the prompt against Haiku-tier (simple) signals. If 2+ match → skip Parts 1 and 2 entirely.

| Signal | Examples |
|--------|---------|
| Pure factual/lookup question | "what is X", "where is X", "explain X", "does X work", "when did X" |
| Single targeted search | one grep, one file read, one symbol lookup |
| Trivial one-step fix | typo, rename one variable, add one import |
| Pure acknowledgment | "ok", "thanks", "got it", "sounds good", "yes", "no" |
| Zero-ambiguity, no file edits | clear question with a bounded factual answer |
| Under 10 words, single concern | short question about one specific thing |

Count matching signals. If **2 or more** match → exit immediately, skip Parts 1 and 2.

If **0 or 1** match → the task is medium or high complexity. Proceed to Part 1.

---

## Part 1 — Prompt Optimizer

**Guard:** Only runs if `~/.claude/.sarthi-prompt-optimizer-enabled` exists.

```bash
[ -f ~/.claude/.sarthi-prompt-optimizer-enabled ] && echo "enabled" || echo "disabled"
```

If disabled, skip to Part 2.

If enabled, load learnings:
```bash
cat ~/.claude/.sarthi-prompt-learnings.json 2>/dev/null || echo "{}"
```

Reset `session_consecutive_rejects` to 0 in-memory (per-session only).

### Signal detection

Score the prompt. Threshold: weighted sum ≥ 2.0. Default weight per signal: 1.0. Reduce to 0.5 if rejected 2+ times with reason; 0.0 if rejected 3+ times. Boost to 1.5 if accepted 3+ times.

| Signal | Description |
|--------|-------------|
| `vague_verb` | Action is unclear — "fix this", "make it better", "clean up" |
| `missing_deliverable` | No concrete outcome stated |
| `multi_concern` | Multiple unrelated tasks in one prompt |
| `repeated_context` | Re-explains something already established this session |
| `scope_creep` | Unbounded scope — "while you're at it", "anything else you notice" |
| `ambiguous_referent` | Unclear what "it", "this", "that" refers to |
| `over_long` | 200+ words with the core ask buried |

If weighted sum < 2.0 → skip silently, go to Part 2.

If ≥ 2.0, present:

```
💡 Prompt suggestion — may reduce round trips:

Original:  "[original prompt]"
Suggested: "[reworded prompt]"

Why: [one line]

[y] Use suggested  [s] Skip  [r] Skip — tell me why
```

Wait for response, then save to `~/.claude/.sarthi-prompt-learnings.json`:
- [y]: increment `accepted` for triggered signals, reset `session_consecutive_rejects` to 0
- [s]: increment `session_consecutive_rejects`, no learning update
- [r]: capture reason, increment `rejected` + `session_consecutive_rejects`; if ≥ 2 consecutive rejects: set session-suppressed and note "holding suggestions for this session"

Learnings file structure:
```json
{
  "version": 1,
  "last_updated": "<date>",
  "session_consecutive_rejects": 0,
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

---

## Part 2 — Model Advisor

**Guard:** Only runs if `~/.claude/.sarthi-model-advisor-enabled` exists.

```bash
[ -f ~/.claude/.sarthi-model-advisor-enabled ] && echo "enabled" || echo "disabled"
```

If disabled, exit.

Load learnings:
```bash
cat ~/.claude/.sarthi-model-learnings.json 2>/dev/null || echo "{}"
```

Reset `session_consecutive_rejects` to 0 in-memory (per-session only).

### Skip conditions

Exit silently if:
- Pure factual/opinion question — "what is X", "why did X", "explain X", "what do you think", "does X work"
- Pure acknowledgment with no pending task — "ok", "got it", "thanks" and last 3 turns have no pending task

**Short reply rule:** Under 5 words approving a prior proposal → assess the proposed task's complexity, not the reply.

### Complexity scoring

**Haiku signals:** Single file/function edit, typo fix, simple lookup, grep/search, boilerplate snippet, one-step unambiguous outcome.

**Sonnet signals (default):** Multi-file feature, moderate debugging, writing tests, focused PR review, bounded refactor, graphify navigation, standard dev tasks.

**Opus signals:** Architecture decisions, cross-service debugging, deep root-cause reasoning, strategic planning, security audit with parallel agents, cross-repo analysis, many conflicting constraints.

Assign the tier with the most signals. Ties → Sonnet.

### Suggest only if current ≠ recommended

| Current | Recommended | Suggest? |
|---------|-------------|----------|
| Opus | Haiku/Sonnet | Yes |
| Sonnet | Haiku | Yes |
| Sonnet | Opus | Yes |
| Haiku | Sonnet/Opus | Yes |
| Any | Same | No — exit silently |

Also check task-type learnings: if that transition has been rejected 2+ times for this task type → suppress silently.

If suggesting:

```
🤖 Model suggestion:

Task complexity: [simple / medium / complex]
Current model:   [name]
Suggested model: [name] — [one-line reason]

To switch: /model [model-id]

[y] Got it — I'll switch  [s] Skip  [r] Skip — tell me why
```

Task always proceeds regardless of response.

Save to `~/.claude/.sarthi-model-learnings.json`. If `session_consecutive_rejects` ≥ 2: suppress for rest of session.

Model IDs: Haiku → `claude-haiku-4-5-20251001`, Sonnet → `claude-sonnet-4-6`, Opus → `claude-opus-4-7`.

---

## Slash commands (forwarded to individual skills)

- `/sarthi-prompt-optimizer status|reset|off|clear` → invoke `sarthi-prompt-optimizer` skill
- `/sarthi-model-advisor status|reset|off|clear` → invoke `sarthi-model-advisor` skill
