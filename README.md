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

> **Sarthi does not build any of these tools. It is a thin routing layer — a skill file that detects your intent and points Claude at the right tool. All capability, all innovation, and all credit belong entirely to the original tool authors listed below. Please star and support their repos directly.**

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

## 🏆 Tools & Full Credits

Sarthi is a wrapper. The real work is done by these tools and their creators. **Please go star their repos.**

| Tool | Purpose | Author / Org | Repo |
|------|---------|--------------|------|
| **compound-engineering** | Build, debug, review, ship, frontend, strategy, brainstorm | [Kieran Klaassen](https://github.com/kieranklaassen) @ [Every Inc](https://every.to) | [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) |
| **graphify** | Codebase knowledge graph, semantic navigation | [Safi Shamsi](https://github.com/safishamsi) | [safishamsi/graphify](https://github.com/safishamsi/graphify) |
| **superpowers** | Parallel agents, TDD, git worktrees, verification patterns | [Jesse Vincent](https://github.com/obra) @ [Prime Radiant](https://primeradiant.com) | [obra/superpowers](https://github.com/obra/superpowers) |
| **codex** | Parallel code review and investigation | [OpenAI](https://openai.com) | [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc) |
| **firecrawl** | Web research, scraping, search | [Firecrawl](https://firecrawl.dev) | [mendableai/firecrawl](https://github.com/mendableai/firecrawl) |
| **codeburn** | Token spend analytics, cost optimization | [AgentSeal](https://github.com/getagentseal) | [getagentseal/codeburn](https://github.com/getagentseal/codeburn) |
| **morph** | Fast bulk code application via MCP | [MorphLLM](https://morphllm.com) | [morphllm/morph-claude-code-plugin](https://github.com/morphllm/morph-claude-code-plugin) |
| **claude-md-management** | Saving session learnings to CLAUDE.md | [Anthropic](https://anthropic.com) | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| **skill-creator** | Generating skills from documentation URLs | [Anthropic](https://anthropic.com) | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| **frontend-design** | High-quality UI with design system awareness | [Anthropic](https://anthropic.com) | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |

*Sarthi works with any combination of the above — or none at all. Each tool can be installed independently.*

## 🤔 Why "Sarthi"?

In the Mahabharata, Lord Krishna served as Arjuna's Sarthi — not just driving the chariot, but guiding decisions at every crossroads. That's what this plugin does: it doesn't replace your tools, it steers between them intelligently so you stay in flow.

## 📖 Full Documentation

See [DOCS.md](DOCS.md) for the complete routing reference, cost guard details, FAQ, and extension guide.

## 🔒 Privacy

Sarthi collects no data. It is a plain markdown skill file that runs entirely on your machine inside Claude Code. No telemetry, no network calls, no external services. The only tools that make network calls are the ones you explicitly install (graphify, firecrawl, etc.) — Sarthi itself is just routing instructions.

## 🤝 Contributing

PRs welcome. The routing rules are plain markdown in `skills/sarthi/SKILL.md` — easy to extend for new tools.

## 📄 License

MIT — built by [Rahul Bindra](https://github.com/rahulbindra)
