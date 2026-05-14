<div align="center">

# 🪄 Sarthi

### Your AI Charioteer for Claude Code

*Sarthi (Sanskrit: सारथी) — charioteer, guide, the one who steers*

[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blue)](https://github.com/rahulbindra/sarthi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green)](https://github.com/rahulbindra/sarthi/releases)

**Built by [Rahul Bindra](https://github.com/rahulbindra)**

</div>

---

Sarthi is a Claude Code plugin that acts as an **intelligent routing layer** for your AI development stack. Instead of remembering which tool to use when, Sarthi detects your intent from natural language and routes you to the right tool automatically — or falls back gracefully to vanilla Claude if you don't have it installed.

## ✨ What Sarthi Does

- **Detects intent** from your message — build, debug, review, ship, navigate, research, refactor, and more
- **Routes automatically** to the best available tool in your stack
- **Falls back gracefully** — works with any combination of tools, or none at all
- **Enforces a cost-guard** — confirms deliverables, catches retry loops, surfaces Morph for bulk edits, offers Codex for reviews

## 📦 Install

```
/plugin marketplace add https://github.com/rahulbindra/sarthi
/plugin install sarthi
/reload-plugins
```

Then invoke with `/sarthi`, or see [Auto-activation](#-auto-activation) to have it load every session automatically.

## 🚀 Usage

Just describe what you want in plain language:

```
"The login screen is crashing on iOS"
→ Routing to /ce-debug.

"Add push notifications to the home screen"
→ Routing to /ce-plan to scope this, then /ce-work.

"Refactor all API calls to use the new client"
→ Morph is active — bulk edits will be applied faster. Routing to /ce-work.

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
| Large refactor | Morph active + `/ce-work` | Edit file by file |
| Debug / Fix | `/ce-debug` | Systematic root cause |
| Frontend / UI | `/ce-frontend-design` | Design-quality prompting |
| Review / PR | `/ce-code-review` + Codex dispatch | Structured review |
| Ship | `/ce-commit-push-pr` | git add/commit/push |
| Codebase nav | `graphify query/path/explain` | Targeted grep |
| Strategy | `/ce-strategy` | Strategy doc in chat |
| Brainstorm | `/ce-brainstorm` | Structured ideation |
| Research | `/firecrawl-search` or `/firecrawl-scrape` | WebFetch |
| Cost check | `codeburn optimize` | Suggest `/compact` |
| New repo | `graphify extract .` | Read README + structure |
| Save learnings | `/revise-claude-md` | Manual CLAUDE.md edit |
| Parallel work | `/ce-worktree` + parallel agents | Sequenced tasks |

## 🛡️ Cost Guard

Before every task, Sarthi checks five things:

1. **Deliverable named?** — Asks for a one-sentence outcome if missing
2. **Graphify available?** — Uses knowledge graph before grepping if graph exists
3. **Morph available?** — Surfaces Morph for bulk/refactor edits automatically
4. **Better for Codex?** — Offers to delegate review/investigation to save Claude tokens
5. **Retry guard** — Stops after two failed attempts and prompts reconsideration

## ⚡ Auto-activation

Add to `~/.claude/settings.json` to activate Sarthi at the start of every session across all repos:

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

## 🧰 Compatible Tools & Credits

Sarthi routes to these tools when installed. Full credit to each team:

| Tool | What Sarthi uses it for | Credit |
|------|------------------------|--------|
| [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin) | Build, debug, review, ship, frontend, strategy, brainstorm | [Kieran Klaassen](https://github.com/kieranklaassen) @ [Every.to](https://every.to) |
| [graphify](https://github.com/safishamsi/graphify) | Codebase navigation, knowledge graph queries | [Safi Shamsi](https://github.com/safishamsi) |
| [superpowers](https://github.com/anthropics/claude-plugins-official) | Parallel agents, TDD, git worktrees, verification | [Jesse Vincent](https://github.com/jesse-c) @ Anthropic |
| [codex](https://github.com/openai/codex-plugin-cc) | Parallel review and investigation (saves Claude tokens) | [OpenAI](https://openai.com) |
| [firecrawl](https://github.com/mendableai/firecrawl) | Web research, scraping, search | [Mendable / Firecrawl](https://firecrawl.dev) |
| [codeburn](https://github.com/nichochar/codeburn) | Token spend analytics, cost optimization | [Nicholas Charriere](https://github.com/nichochar) |
| [morph](https://morphllm.com) | Fast bulk code application via MCP | [MorphLLM](https://github.com/morphllm) |
| [claude-md-management](https://github.com/anthropics/claude-plugins-official) | Saving session learnings to CLAUDE.md | Anthropic |
| [skill-creator](https://github.com/anthropics/claude-plugins-official) | Generating skills from documentation URLs | Anthropic |
| [frontend-design](https://github.com/anthropics/claude-plugins-official) | High-quality UI building with design system awareness | Anthropic |

*Sarthi works with any combination of the above — or none at all.*

## 🤔 Why "Sarthi"?

In the Mahabharata, Lord Krishna served as Arjuna's Sarthi — not just driving the chariot, but guiding decisions at every crossroads. That's what this plugin does: it doesn't replace your tools, it steers between them intelligently so you stay in flow.

## 📖 Full Documentation

See [DOCS.md](DOCS.md) for the complete routing reference, cost guard details, FAQ, and extension guide.

## 🤝 Contributing

PRs welcome. The routing rules are plain markdown in `skills/sarthi/SKILL.md` — easy to extend for new tools.

## 📄 License

MIT — built by [Rahul Bindra](https://github.com/rahulbindra)
