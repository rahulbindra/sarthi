<div align="center">

# 🪄 Sarthi

### Your AI Charioteer for Claude Code

*Sarthi (Sanskrit: सारथी) — charioteer, guide, the one who steers*

[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://github.com/rahulbindra/sarthi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/rahulbindra/sarthi)

</div>

---

Sarthi is a Claude Code plugin that acts as an **intelligent routing layer** for your AI development stack. Instead of remembering which tool to use when, Sarthi detects your intent from natural language and routes you to the right tool automatically — or falls back gracefully to vanilla Claude if you don't have it installed.

## ✨ What Sarthi Does

- **Detects intent** from your message — build, debug, review, ship, navigate, research, and more
- **Routes automatically** to the best available tool in your stack
- **Falls back gracefully** — if a tool isn't installed, Sarthi uses vanilla Claude with the same structured approach
- **Enforces a cost-guard** on every task — confirms your deliverable, catches retry loops, offers smarter delegation

## 📦 Install

```
/plugin marketplace add https://github.com/rahulbindra/sarthi
/plugin install sarthi
/reload-plugins
```

Then invoke manually with `/sarthi`, or activate automatically every session (see [Auto-activation](#auto-activation)).

## 🚀 Usage

Just describe what you want to do in plain language:

```
"The login screen is crashing on iOS"
→ Routing to /ce-debug.

"Add push notifications to the home screen"
→ Routing to /ce-plan to scope this, then /ce-work.

"How does the auth flow connect to the session manager?"
→ Using graphify. [runs: graphify query "auth flow session manager"]

"Ship what I have"
→ Routing to /ce-commit-push-pr.

"How much have I spent this week?"
→ [runs: codeburn]
```

## 🗺️ Routing Table

| Intent | With tools | Without tools |
|--------|-----------|---------------|
| Build feature | `/ce-plan` → `/ce-work` | Step-by-step in chat |
| Debug / Fix | `/ce-debug` | Systematic root cause |
| Frontend / UI | `/ce-frontend-design` | Design-quality prompting |
| Review / PR | `/ce-code-review` + Codex | Structured review |
| Ship | `/ce-commit-push-pr` | git add/commit/push |
| Codebase nav | `graphify query` | Targeted grep |
| Strategy | `/ce-strategy` | Strategy doc in chat |
| Brainstorm | `/ce-brainstorm` | Structured ideation |
| Research | `/firecrawl-search` | WebFetch |
| Cost check | `codeburn optimize` | Suggest `/compact` |
| New repo | `graphify extract .` | Read README + structure |
| Save learnings | `/revise-claude-md` | Manual CLAUDE.md edit |
| Parallel work | `/ce-worktree` + agents | Sequenced tasks |

## 🛡️ Cost Guard

Sarthi runs a four-point check before every task:

1. **Deliverable named?** — Asks for a one-sentence outcome if missing
2. **Graphify available?** — Uses knowledge graph before grepping files if graph exists
3. **Better for Codex?** — Offers to delegate investigation/review tasks to save Claude tokens
4. **Retry guard** — Stops after two failed attempts and prompts reconsideration

## ⚡ Auto-activation

Add to `~/.claude/settings.json` to activate Sarthi automatically at the start of every session:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "statusMessage": "Sarthi loading...",
        "command": "python3 -c \"import json; print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': 'Act as Sarthi: read ~/.claude/skills/sarthi/SKILL.md and apply its routing rules to every user message this session. Detect intent, check available tools, route automatically.'}}))\" "
      }]
    }]
  }
}
```

## 🧰 Works Great With

Sarthi routes to these tools when installed — but works without any of them:

| Tool | Install |
|------|---------|
| [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin) | `/plugin install compound-engineering` |
| [graphify](https://github.com/safishamsi/graphify) | `pip install graphifyy && graphify install` |
| [superpowers](https://github.com/anthropics/claude-plugins-official) | `/plugin install superpowers` |
| [codex](https://github.com/openai/codex-plugin-cc) | `/plugin install codex` |
| [firecrawl](https://github.com/anthropics/claude-plugins-official) | `/plugin install firecrawl` |
| [codeburn](https://github.com/nichochar/codeburn) | `npm install -g codeburn` |
| [morph](https://github.com/morphllm/morph) | `npx @morphllm/morph-setup` |

## 🤔 Why "Sarthi"?

In the Mahabharata, Lord Krishna served as Arjuna's Sarthi — not just driving the chariot, but guiding decisions at every crossroads. That's what this plugin does: it doesn't replace your tools, it steers between them intelligently, so you spend time building instead of remembering which command to run.

## 📄 License

MIT — built by [Rahul Bindra](https://github.com/rahulbindra)
