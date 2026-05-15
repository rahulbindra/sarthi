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

Sarthi is a Claude Code plugin that acts as an **intelligent routing layer** for your AI development stack. Instead of remembering which tool to use when, describe what you want in plain language — Sarthi detects your intent and routes to the right tool automatically. Falls back gracefully to vanilla Claude if you don't have a tool installed.

## 📦 Install

### Prerequisites

Sarthi is a router — it needs tools to route to. Install any combination of these before running setup:

| Tool | Install | What it unlocks |
|------|---------|----------------|
| [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin) | `/plugin install compound-engineering@compound-engineering-plugin` | Build, debug, review, ship, frontend, strategy |
| [graphify](https://github.com/safishamsi/graphify) | `pip install graphifyy` | Codebase knowledge graph navigation |
| [morph](https://github.com/morphllm/morph-claude-code-plugin) | See Morph docs | Fast bulk code edits via MCP |
| [firecrawl](https://github.com/mendableai/firecrawl) | `/plugin install firecrawl@claude-plugins-official` | Web research and scraping |
| [codex](https://github.com/openai/codex-plugin-cc) | `/plugin install codex@openai-codex` | Parallel code review |
| [codeburn](https://github.com/getagentseal/codeburn) | `npm install -g codeburn` | Token spend analytics |
| [superpowers](https://github.com/obra/superpowers) | `/plugin install superpowers@claude-plugins-official` | Parallel agents, TDD, worktrees |

Sarthi works with any subset — or none at all. Start with compound-engineering and graphify for the most impact.

> **Note for graphify users:** Claude Code authenticates via OAuth, not an API key — so `ANTHROPIC_API_KEY` is not set in your shell automatically. Graphify is a separate CLI that makes direct API calls and needs its own key. Create one at [console.anthropic.com/keys](https://console.anthropic.com/keys) and add it to your shell profile:
> ```bash
> export ANTHROPIC_API_KEY=sk-ant-...
> ```
> Only the initial `graphify extract .` costs tokens. All subsequent `graphify update .` calls (run automatically by the PostToolUse hook after every file edit) are free.

### Step 1 — Install the plugin
```
/plugin marketplace add https://github.com/rahulbindra/sarthi
/plugin install sarthi
/reload-plugins
```

### Step 2 — Run setup (one command does everything)
```
/sarthi-setup
```

This automatically configures:
- The **SessionStart hook** so Sarthi activates at the start of every session
- The **PostToolUse hook** so graphify stays fresh after every code edit
- **codeburn menubar** for passive background cost monitoring

> ⚠️ **Restart Claude Code after setup for hooks to take effect.**

<details>
<summary>Manual setup (if you prefer to configure hooks yourself)</summary>

**SessionStart hook** — add to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "statusMessage": "Sarthi loading...",
        "command": "python3 -c \"import json; print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': 'Act as Sarthi. Load ~/.claude/skills/sarthi/SKILL.md and follow it exactly, including the Session Onboarding block: detect tools silently, auto-setup graphify if needed, then present the welcome prompt listing active tools and asking the user if they want to skip any before routing.'}}))\" "
      }]
    }]
  }
}
```

**PostToolUse hook** — keeps graphify graph fresh after edits:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{
        "type": "command",
        "command": "[ -f graphify-out/graph.json ] && python3 -c \"import os,time; exit(0 if time.time()-os.path.getmtime('graphify-out/graph.json')>30 else 1)\" 2>/dev/null && graphify update . > /dev/null 2>&1 || true"
      }]
    }]
  }
}
```

**codeburn menubar** — passive cost monitoring:
```
codeburn menubar
```

> **Security note:** Always read hook commands before adding them. These commands make no network calls and execute no external code. See [DOCS.md](DOCS.md) for details.

</details>

## 🔄 Updating

```
/plugin install sarthi
/reload-plugins
```

This pulls the latest skill files from GitHub. Your hooks (`~/.claude/settings.json`) and Morph MCP config (`~/.claude.json`) are untouched — no need to re-run `/sarthi-setup`.

## ✨ What Sarthi Does

At the start of every session, Sarthi presents a brief welcome showing which tools are active, and lets you skip any of them for that session:

```
Sarthi ready. Here's what's active this session:

  [1] compound-engineering  — build, debug, review, ship, frontend, strategy, brainstorm
  [2] graphify              — codebase navigation via knowledge graph
  [3] morph                 — fast bulk code edits (MCP active)
  [4] firecrawl             — web research and scraping
  [5] codex                 — parallel code review and investigation
  [6] codeburn              — token spend analytics (audit due every 3 days)
  [7] superpowers           — parallel agents, TDD, git worktrees

Skip any tool for this session? Type e.g. "skip 3 5" — or just start working to use all.
Skipped tools fall back to standard Claude behaviour.
```

After that, just describe what you want. Sarthi handles the rest.

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
| Cost check | `codeburn status` | Suggest `/compact` |
| New repo | `graphify extract .` (auto) | Read README + structure |
| Save learnings | `/revise-claude-md` | Manual CLAUDE.md edit |
| Parallel work | `/ce-worktree` + parallel agents | Sequenced tasks |

## 🚀 Usage

Just describe what you want in plain language. Sarthi detects intent and routes — no slash commands needed.

**Building & debugging**
```
"The login screen is crashing on iOS"
→ Routing to /ce-debug.

"Add push notifications to the home screen"
→ Routing to /ce-plan to scope this, then /ce-work.

"The payment flow is broken after the last merge"
→ Routing to /ce-debug. What's the error or stack trace?
```

**Refactoring & bulk edits**
```
"Refactor all API calls to use the new client"
→ Morph is active — bulk edits will be applied faster. Routing to /ce-work.

"Rename UserProfile to AccountProfile across the whole codebase"
→ Morph is active. Routing to /ce-work to apply this rename.
```

**Codebase navigation**
```
"How does the auth flow connect to the session manager?"
→ Using graphify. [runs: graphify query "auth flow session manager"]

"Where is the push notification logic?"
→ [runs: graphify query "push notification logic"] — found in src/services/notifications.ts.

"What calls the checkout function?"
→ [runs: graphify path "checkout" "<callers>"]
```

**Frontend & UI**
```
"Redesign the home screen to feel more like Linear"
→ Routing to /ce-frontend-design.

"The settings screen layout is broken on smaller phones"
→ Routing to /ce-frontend-design with the layout fix as scope.
```

**Review & shipping**
```
"Review this PR before I merge"
→ Routing to /ce-code-review. Want me to also dispatch to Codex for an independent parallel review?

"Ship what I have"
→ Routing to /ce-commit-push-pr.

"Open a PR with a proper description"
→ Routing to /ce-commit-push-pr.
```

**Research & strategy**
```
"Look up the Stripe webhooks documentation"
→ Routing to /firecrawl-scrape.

"What should we build next quarter?"
→ Routing to /ce-strategy.

"Brainstorm ways to improve onboarding retention"
→ Routing to /ce-brainstorm.
```

**Cost & session hygiene**
```
"How much have I spent this week?"
→ [runs: codeburn]

"Save this approach to CLAUDE.md"
→ Routing to /revise-claude-md.
```

## 🛡️ Cost Guard

Before every task, Sarthi checks five things:

1. **Deliverable named?** — Asks for a one-sentence outcome if missing
2. **Graphify available?** — Queries the knowledge graph before any file reads or grep. On a new repo, builds the graph automatically in the background (`graphify extract .` uses LLM tokens once; all subsequent refreshes are free)
3. **Morph available?** — Surfaces Morph automatically for bulk/refactor edits
4. **Better for Codex?** — Offers an independent parallel review rather than doing it inline
5. **Retry guard** — Stops after two failed attempts and prompts reconsideration

## 📊 Automated Codeburn Audit

Sarthi tracks when you last reviewed your token spend. Every session start, it checks whether a codeburn audit is due:

- If codeburn hasn't been run in **3+ days**, the onboarding prompt shows:
  ```
  ⚠️  Codeburn audit due — last review was 3+ days ago. Type "codeburn audit" to run it now.
  ```
- Running the audit surfaces usage patterns and improvement areas for the last 3 days
- The 3-day clock resets automatically after each audit

You can ignore the nudge and start working — it won't interrupt your session. The timestamp is stored locally in `~/.claude/.sarthi-codeburn-ts`.

## 🔍 Weekly Project Audit

Sarthi prompts you once a week to run a multi-domain audit across your project. At session start, it checks whether an audit is due:

```
⚠️  Weekly project audit due. Type "sarthi audit" to run security, privacy, vulnerability,
    engineering, attribution, usability, legal, ethical hacker, and keys/PII checks.
```

Running `sarthi audit` dispatches **9 parallel sub-agents**, one per domain:

| Domain | What it checks |
|--------|---------------|
| **Security** | OWASP Top 10 — injection, broken auth, XSS, CSRF, missing input validation |
| **Privacy** | PII collection, data retention, third-party exfiltration, GDPR/CCPA gaps |
| **Vulnerability** | Dependency CVEs (`npm audit`, `pip-audit`), outdated packages, deprecated APIs |
| **Engineering** | Logic errors, N+1 queries, missing error handling, dead code, test coverage gaps |
| **Fair Attribution** | Copied code without credit, license incompatibilities, missing copyright headers |
| **Usability** | Missing ARIA labels, keyboard nav, alt text, error message quality, empty states |
| **Legal** | License compliance, copyleft contamination, missing privacy policy, export controls |
| **Ethical Hacker** | Injection vectors (SQLi, SSTI, XXE, log injection), information extraction points (verbose errors, open introspection, permissive CORS, over-fetching) |
| **Keys & PII** | Hardcoded API keys, tokens, private keys, SSNs, credit card numbers, `.env` files committed to git |

Each domain returns `pass / warn / fail` with file paths and line numbers. The report is aggregated into a single summary.

You can target a specific domain: `sarthi audit keys`, `sarthi audit security`, etc.

The weekly clock resets after each audit. Timestamp stored in `~/.claude/.sarthi-audit-ts`.

## 📁 Best Practices Templates

The [`best-practices/`](best-practices/) folder contains 9 governance templates for running Claude Code efficiently on any project:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Drop-in AI instruction file for your repo root |
| `CURRENT_SPRINT.md` | Scope-lock for the active sprint — prevents token waste from drift |
| `ARCHITECTURE.md` | Non-negotiable system patterns Claude must respect |
| `DESIGN_SYSTEM.md` | Visual standards to keep UI consistent across sessions |
| `API_PATTERNS.md` | Backend integration conventions |
| `IMPLEMENTATION_PATTERNS.md` | Coding style and conventions |
| `PRODUCT_PRINCIPLES.md` | UX and product decision heuristics |
| `AI_WORKFLOW.md` | How Claude should operate within your repo |
| `PLACEMENT_AND_USAGE_GUIDE.md` | Where each file goes and how to use it |

Copy the ones you need into your project. See `PLACEMENT_AND_USAGE_GUIDE.md` for setup instructions.

## 🏆 Tools & Full Credits

> Sarthi is a thin routing layer — a skill file that detects your intent and points Claude at the right tool. All capability, all innovation, and all credit belong entirely to the original tool authors. **Please go star their repos.**

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

*Sarthi works with any combination of the above — or none at all. Each tool is installed independently.*

## 🤔 Why "Sarthi"?

In the Mahabharata, Lord Krishna served as Arjuna's Sarthi — not just driving the chariot, but guiding decisions at every crossroads. That's what this plugin does: it doesn't replace your tools, it steers between them intelligently so you stay in flow.

## 📖 Full Documentation

See [DOCS.md](DOCS.md) for the complete routing reference, cost guard details, FAQ, and extension guide.

## 🔒 Privacy

Sarthi collects no data. It is a plain markdown skill file that runs entirely on your machine inside Claude Code. No telemetry, no network calls, no external services. The only tools that make network calls are the ones you explicitly install (graphify, firecrawl, etc.) — Sarthi itself is just routing instructions.

## 💬 Feedback & Support

- **Bug reports / feature requests:** [Open an issue](https://github.com/rahulbindra/sarthi/issues)
- **Security concerns or sensitive feedback:** rahulbindra@gmail.com

## 🤝 Contributing

PRs welcome. The routing rules are plain markdown in `skills/sarthi/SKILL.md` — easy to extend for new tools.

## 📄 License

MIT — built by [Rahul Bindra](https://github.com/rahulbindra)
