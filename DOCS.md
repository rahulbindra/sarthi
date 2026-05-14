# Sarthi — Full Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [How It Works](#how-it-works)
4. [Intent Detection](#intent-detection)
5. [Tool Routing Reference](#tool-routing-reference)
6. [Cost Guard](#cost-guard)
7. [Auto-activation](#auto-activation)
8. [Without Any Tools](#without-any-tools)
9. [Extending Sarthi](#extending-sarthi)
10. [FAQ](#faq)

---

## Overview

Sarthi is a Claude Code plugin that acts as an intelligent routing layer sitting between you and your AI development toolstack. When you describe a task in plain language, Sarthi:

1. Detects your intent
2. Checks which tools are installed
3. Routes to the best available tool — or falls back to vanilla Claude
4. Applies a cost-guard pattern before starting

The name comes from Sanskrit (सारथी) meaning charioteer or guide — in the Mahabharata, Krishna was Arjuna's Sarthi, steering the chariot while Arjuna focused on the battle. Sarthi does the same: it handles the routing so you can focus on building.

---

## Installation

### One-command install (Claude Code)

```
/plugin marketplace add https://github.com/rahulbindra/sarthi
/plugin install sarthi
/reload-plugins
```

### Verify

After reloading, you should see `sarthi` in your skills list. Test it:

```
/sarthi
```

---

## How It Works

Sarthi runs in three stages on every task:

### Stage 1: Tool Detection
At the start of each session, Sarthi silently checks which tools are available:
- Looks for CLI binaries (`graphify`, `codeburn`)
- Checks for knowledge graph files (`graphify-out/graph.json`)
- Scans available skills for compound-engineering, firecrawl, codex, claude-md-management

### Stage 2: Intent Matching
Sarthi reads your message and matches it to one of 13 intent categories using signal words and patterns. It never routes to a tool that isn't installed.

### Stage 3: Cost Guard + Routing
Before acting, Sarthi runs a four-point cost check, then either invokes the tool immediately (clear match) or presents 2–3 options (ambiguous).

---

## Intent Detection

Sarthi recognises these intents:

| Intent | Example messages |
|--------|-----------------|
| **Build** | "add push notifications", "implement dark mode", "create a settings screen" |
| **Debug** | "the app is crashing", "this test is failing", "fix this error: [stack trace]" |
| **Frontend** | "redesign the home screen", "add a loading skeleton", "fix the layout on mobile" |
| **Review** | "review my PR", "check this before I merge", "is this code good?" |
| **Ship** | "commit this", "push and open a PR", "ship what I have" |
| **Navigate** | "how does auth work", "where is the notification logic", "what calls PulseScreen" |
| **Strategy** | "what should we build next", "update the roadmap", "write our strategy" |
| **Brainstorm** | "give me ideas for", "what are the options", "brainstorm how we could" |
| **Research** | "look up the Stripe docs", "what does this library do", "scrape this URL" |
| **Cost** | "how much have I spent", "optimize my usage", "what's my token burn" |
| **New repo** | "just cloned this", "set up a new project", "map this codebase" |
| **Learnings** | "remember this", "save this approach", "update CLAUDE.md" |
| **Parallel** | "do these two things at once", "run this in parallel" |

---

## Tool Routing Reference

### compound-engineering routes
| Intent | Skill invoked |
|--------|--------------|
| Build | `/ce-plan` → `/ce-work` |
| Debug | `/ce-debug` |
| Frontend | `/ce-frontend-design` |
| Review | `/ce-code-review` |
| Ship | `/ce-commit-push-pr` |
| Strategy | `/ce-strategy` |
| Brainstorm | `/ce-brainstorm` |
| Parallel | `/ce-worktree` |
| Learnings | N/A (routes to claude-md-management) |

### graphify routes
| Intent | Command |
|--------|---------|
| Navigate (graph exists) | `graphify query "..."` |
| Navigate (no graph) | `graphify extract . --backend claude` |
| Cross-module question | `graphify path "A" "B"` |
| Explain a concept | `graphify explain "X"` |

### Other tools
| Tool | Intent | Action |
|------|--------|--------|
| codex | Review (expensive) | `/codex rescue` |
| firecrawl | Research | `/firecrawl-search` or `/firecrawl-scrape` |
| codeburn | Cost | `codeburn` or `codeburn optimize` |
| claude-md-management | Learnings | `/revise-claude-md` |

---

## Cost Guard

The cost guard runs **before every task** regardless of which tool is used.

### Check 1: Named deliverable
If your message doesn't have a clear outcome, Sarthi asks:
> "What's the one-sentence result of this task?"

This prevents the most common source of wasted tokens: open-ended sessions without a defined endpoint.

### Check 2: Graphify first
If `graphify-out/graph.json` exists, Sarthi always queries the knowledge graph before reading files or running grep. This can significantly reduce the tokens spent on codebase navigation — graphify's semantic index replaces many grep-and-read cycles.

### Check 3: Codex delegation
For investigation and review tasks, Sarthi offers to dispatch to Codex:
> "This looks like a good Codex task — want me to dispatch it to save Claude tokens?"

Reviews and investigations don't need Claude's full capability. Codex handles them well at lower cost.

### Check 4: Retry guard
If the same approach fails twice, Sarthi stops:
> "Same approach failed twice. Let's step back and reconsider before trying again."

This prevents the retry spiral that causes expensive sessions.

---

## Auto-activation

By default, Sarthi is invoked manually with `/sarthi`. To activate it automatically at the start of every session, add a `SessionStart` hook to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "statusMessage": "Sarthi loading...",
        "command": "python3 -c \"import json; print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': 'Act as Sarthi: read ~/.claude/skills/sarthi/SKILL.md and apply its routing rules to every user message this session.'}}))\" "
      }]
    }]
  }
}
```

This makes Sarthi active for all sessions across all repos.

---

## Without Any Tools

Sarthi works even with zero additional tools installed. When no specialized tool is available, it falls back to structured vanilla Claude approaches:

| Intent | Vanilla Claude fallback |
|--------|------------------------|
| Build | Plan in chat → implement step by step |
| Debug | Request error + context → systematic root cause |
| Frontend | Build with explicit design quality instructions |
| Review | Correctness → security → style structured review |
| Ship | Conventional commit message → git push |
| Navigate | Targeted grep → read key files → explain |
| Research | WebFetch on provided URLs |
| Cost | Suggest `/compact` or starting a fresh session |

---

## Extending Sarthi

Sarthi's routing rules are plain markdown in `SKILL.md`. To add routing for a new tool:

1. Add a new section under **Step 2: Route by Intent**
2. Add a row to the detection table with signal words
3. Add fallback behavior for when the tool isn't installed

PRs welcome.

---

## FAQ

**Does Sarthi work with Cursor / other IDEs?**
Currently optimised for Claude Code. The skill format may work in other Claude-based tools but isn't tested.

**What if Sarthi routes to the wrong tool?**
Just say "no, do X instead" — Sarthi will re-route. Or invoke the tool directly with its slash command.

**Does Sarthi collect any data?**
No. Sarthi is a plain markdown skill file. It runs entirely inside Claude Code on your machine and makes no network calls of its own. No telemetry, no analytics, no external services. Tools you install separately (graphify, firecrawl, etc.) may make their own network calls per their own documentation.

**Does Sarthi add latency?**
The SessionStart hook adds ~100ms at session open. Per-message routing adds no latency — it's part of Claude's response, not a separate call.

**Is it safe to use without compound-engineering?**
Yes. Sarthi detects what's installed and only routes to available tools. Without compound-engineering, it falls back to vanilla Claude for all development tasks.

**Can I use Sarthi with just graphify?**
Absolutely. Sarthi + graphify alone significantly improves codebase navigation and reduces grep-heavy sessions.
