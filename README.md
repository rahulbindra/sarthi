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

## ⚡ Install (2 steps)

**Step 1 — Run in your terminal:**
```bash
curl -fsSL https://raw.githubusercontent.com/rahulbindra/sarthi/main/install.sh | bash
```
This clones Sarthi, installs all skills to `~/.claude/skills/`, and registers them in `~/.claude/CLAUDE.md` — idempotent, safe to re-run.

**Step 2 — Open Claude Code and run:**
```
/sarthi-setup
```
Setup configures all hooks, enables advisors, installs the pre-commit secrets scan, and wires Morph MCP if you have a key. Run in a **fresh session** (no prior history) so it doesn't hit context limits.

> **⚠️ Restart Claude Code after setup completes** — hooks don't activate until restart.

**Recommended first install:** [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin) + [graphify](https://github.com/safishamsi/graphify) covers 80% of daily use.

> **Using graphify?** It needs its own `ANTHROPIC_API_KEY` — Claude Code uses OAuth, but graphify calls the API directly. Add it before running setup, otherwise graph builds will fail silently:
> ```bash
> echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.zprofile && source ~/.zprofile
> ```
> Get a key at [console.anthropic.com/keys](https://console.anthropic.com/keys). Only the first graph build costs tokens — all subsequent refreshes are free.

---

## 📦 Install

### Prerequisites

Sarthi is a router — it needs tools to route to. Install any combination of these before running setup:

| Tool | Install | What it unlocks |
|------|---------|----------------|
| [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin) | `/plugin install compound-engineering@compound-engineering-plugin` | Build, debug, review, ship, frontend, strategy |
| [graphify](https://github.com/safishamsi/graphify) | `pip install graphifyy` *(note: two y's — this is the correct PyPI package name)* | Codebase knowledge graph navigation |
| [morph](https://github.com/morphllm/morph-claude-code-plugin) | Get a free key at [morphllm.com](https://morphllm.com), then re-run `/sarthi-setup` | Fast bulk code edits via MCP |
| [firecrawl](https://github.com/mendableai/firecrawl) | `/plugin install firecrawl@claude-plugins-official` | Web research and scraping |
| [codex](https://github.com/openai/codex-plugin-cc) | `/plugin install codex@openai-codex` | Parallel code review |
| [codeburn](https://github.com/getagentseal/codeburn) | `npm install -g codeburn` | Token spend analytics |
| [superpowers](https://github.com/obra/superpowers) | `/plugin install superpowers@claude-plugins-official` | Parallel agents, TDD, worktrees |
| [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | `/plugin marketplace add multica-ai/andrej-karpathy-skills` then `/plugin install andrej-karpathy-skills@karpathy-skills` | Extended Karpathy discipline guidelines (optional — Sarthi includes the Karpathy pre-flight check built-in regardless) |

Sarthi works with any subset — or none at all. **Recommended start:** compound-engineering + graphify.

### Step 1 — Run in terminal

```bash
curl -fsSL https://raw.githubusercontent.com/rahulbindra/sarthi/main/install.sh | bash
```

Clones Sarthi, installs all skills to `~/.claude/skills/`, and registers them in `~/.claude/CLAUDE.md`. Idempotent — safe to re-run.

### Step 2 — Run setup inside Claude Code

Open Claude Code in a **fresh session** (important — setup can hit context limits in a long session):

```
/sarthi-setup
```

This automatically configures:
- The **SessionStart hook** so Sarthi activates at the start of every session
- The **PostToolUse hook** so graphify stays fresh after every code edit
- **All three advisors** (prompt optimizer, session monitor, model advisor)
- A **global pre-commit hook** that scans staged files for hardcoded secrets
- **codeburn menubar** for passive background cost monitoring

> **⚠️ Restart Claude Code after setup finishes** — hooks don't activate until restart.

### Configure later (no setup required)

**Morph MCP** — get a free API key at [morphllm.com](https://morphllm.com), then re-run `/sarthi-setup`. It skips already-configured items and just wires Morph.

**ANTHROPIC_API_KEY** (needed for graphify — Claude Code uses OAuth, graphify calls the API directly):
```bash
echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.zprofile && source ~/.zprofile
```
Get a key at [console.anthropic.com/keys](https://console.anthropic.com/keys). Only the first graph build costs tokens.

### Troubleshooting

**Hooks not firing after restart?** Check `~/.claude/settings.json` — this is where Sarthi's SessionStart, PostToolUse, and UserPromptSubmit hooks live. Run `jq '.hooks' ~/.claude/settings.json` to inspect.

**Morph not working?** Morph MCP is configured in `~/.claude.json` (separate from settings.json). Run `jq '.mcpServers["morph-mcp"]' ~/.claude.json` to inspect. Re-run `/sarthi-setup` to repair.

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

```bash
curl -fsSL https://raw.githubusercontent.com/rahulbindra/sarthi/main/install.sh | bash
```

Re-runs the same installer — idempotent, overwrites skill files with the latest, never touches hooks or Morph MCP config. No need to re-run `/sarthi-setup`.

## ✨ What Sarthi Does

At the start of every session, Sarthi presents a brief welcome showing which tools are active, and lets you skip any of them for that session:

```
Sarthi ready. Here's what's active this session:

  [1] compound-engineering  — build, debug, review, ship, frontend, strategy, brainstorm
  [2] graphify              — codebase navigation via knowledge graph
  [3] morph                 — fast bulk code edits (MCP active)
  [4] firecrawl             — web research and scraping
  [5] codex                 — parallel code review and investigation
  [6] codeburn              — token spend analytics (run: codeburn)
  [7] superpowers           — parallel agents, TDD, systematic debugging, code review, verification

Skip any tool for this session? Type e.g. "skip 3 5" — or just start working to use all.
Skipped tools fall back to standard Claude behaviour.
```

After that, just describe what you want. Sarthi handles the rest.

## 🗺️ Routing Table

| Intent | With tools | Without tools |
|--------|-----------|---------------|
| **Idea → product brief** | `/sarthi-pm` — full PM flow | `/sarthi-pm` — always available |
| **Sprint planning** | `/sarthi-pm` Sprint Planning Flow | `/sarthi-pm` Sprint Planning Flow |
| Build feature | `/ce-plan` → `/ce-work` | Step-by-step in chat |
| Large refactor | Morph (`mcp__morph-mcp__edit_file`) + `/ce-work` | Edit file by file |
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
```

**Research & strategy**
```
"Look up the Stripe webhooks documentation"
→ Routing to /firecrawl-scrape.

"What should we build next quarter?"
→ Routing to /ce-strategy.
```

**Cost & session hygiene**
```
"How much have I spent this week?"
→ [runs: codeburn]

"Save this approach to CLAUDE.md"
→ Routing to /revise-claude-md.
```

## 🛡️ Cost Guard

Before every task, Sarthi checks six things:

1. **Deliverable named?** — Asks for a one-sentence outcome if missing (skipped for informational queries and navigation requests)
2. **Graphify available?** — Queries the knowledge graph before any file reads or grep. On a new repo, builds the graph automatically in the background (`graphify extract .` uses LLM tokens once; all subsequent refreshes are free)
3. **Morph available?** — For tasks touching 3+ files, switches to `mcp__morph-mcp__edit_file` for all edits in the task. Morph's MCP server starts automatically but edits must be explicitly routed through it.
4. **Better for Codex?** — Offers an independent parallel review rather than doing it inline
5. **Retry guard** — Stops after two failed attempts and prompts reconsideration
6. **Karpathy pre-flight** — Before any non-trivial code change: stops and asks the user to confirm assumptions, scope, and success criteria interactively before writing a single line

## 📏 Session Monitor (opt-in)

Watches your context fill and nudges you **twice per session** — before Claude's reasoning quality degrades.

Enable during `/sarthi-setup` or: `touch ~/.claude/.sarthi-session-monitor-enabled`

| Mark | Threshold | What it shows |
|------|-----------|---------------|
| First nudge | ~90% context | Suggests `/compact` to compress history in place, or a new session |
| Final nudge | ~100% context | Recommends a fresh session, with a clean handoff checklist |

Both nudges are **non-blocking** — the current task proceeds regardless. Neither fires more than once. Once both have fired, Sarthi goes silent for the rest of the session.

Context fill is estimated from conversation signals — message count, tool output volume, file edit count, and `/compact` history. Codeburn tracks daily/monthly spend totals only and does not expose per-session token counts.

---

## 🤖 Model Advisor (opt-in)

Before each task, assesses complexity and suggests the most token-efficient Claude model. Learns from your accept/reject decisions over time.

Enable during `/sarthi-setup` or: `touch ~/.claude/.sarthi-model-advisor-enabled`

| Complexity | Suggested model | Typical tasks |
|------------|----------------|---------------|
| Simple | Haiku 4.5 | Single-file edits, typos, lookups, renames, boilerplate |
| Medium | Sonnet 4.6 | Multi-file features, debugging, tests, code review |
| Complex | Opus 4.7 | Architecture, cross-system debugging, PM planning, audits |

A suggestion only appears when your **current model is sub-optimal** for the task — e.g. using Opus for a typo fix, or Haiku for an architecture decision. Since Claude Code model switching requires a user action, Sarthi tells you the exact `/model <id>` command to run — it can't switch automatically.

**How it looks:**
```
🤖 Model suggestion:

Task complexity: simple
Current model:   Opus 4.7
Suggested model: Haiku 4.5 — single-file rename, no reasoning depth needed

To switch: /model claude-haiku-4-5-20251001

[y] Note taken — I'll switch  [s] Skip  [r] Skip — tell me why
```

Same learning loop as the prompt optimizer — accepts/rejects saved to `~/.claude/.sarthi-model-learnings.json`. Two consecutive rejects → silent for the session.

Commands: `/sarthi-model-advisor status`, `reset`, `off`, `clear`

---

## ✏️ Prompt Optimizer (opt-in)

Before routing any task, Sarthi can assess your prompt for token-inefficiency signals and suggest a tighter reword — reducing clarifying round trips and wasted work.

### Inefficiency signals it detects

| Signal | Example |
|--------|---------|
| Vague verb | "fix this", "make it better" |
| Missing deliverable | "look at the auth flow" |
| Multi-concern | "fix X and also update Y and check Z" |
| Repeated context | Re-explains stack or bug already discussed this session |
| Scope creep | "while you're at it", "and anything else you notice" |
| Ambiguous referent | "fix it", "update this" without a clear subject |
| Over-long | 200+ word prompt with a buried one-line ask |

A suggestion only appears when **2 or more** signals are present — never for a single signal alone.

### How it looks

```
💡 Token suggestion — your prompt may cause extra round trips:

Original:  "fix the login thing and also make signup better"
Suggested: "Fix the JWT expiry bug on /login. Separately: improve signup form validation feedback."

Why: splits two unrelated tasks, adds specific deliverables

[y] Use suggested  [s] Skip  [r] Skip — tell me why (one line)
```

### How it learns

Every accept or reject is saved to `~/.claude/.sarthi-prompt-learnings.json`. Over time, Sarthi stops suggesting patterns you consistently reject and prioritises patterns you consistently accept. A short optional reason on rejection accelerates this.

**Session suppression:** if you reject 2 suggestions in a row, the optimizer goes quiet for the rest of that session automatically.

### Commands

| Command | What it does |
|---------|-------------|
| `/sarthi-prompt-optimizer status` | Shows accept/reject stats and strongest/weakest patterns |
| `/sarthi-prompt-optimizer reset` | Re-enables suggestions after session suppression |
| `/sarthi-prompt-optimizer off` | Disables optimizer entirely |
| `/sarthi-prompt-optimizer clear` | Clears learnings and starts fresh |

## 📊 Automated Codeburn Audit

Sarthi tracks when you last reviewed your token spend. Every session start, it checks whether a codeburn audit is due:

- If codeburn hasn't been run in **3+ days**, the onboarding prompt shows:
  ```
  ⚠️  Codeburn audit due — last review was 3+ days ago. Type "codeburn audit" to run it now.
  ```
- Running the audit surfaces usage patterns and improvement areas for the last 3 days
- The 3-day clock resets automatically after each audit

You can ignore the nudge and start working — it won't interrupt your session. The timestamp is stored locally in `~/.claude/.sarthi-codeburn-ts`.

## 🗂️ Product Management Flow

When you have an idea and need to shape it before building, Sarthi runs a guided PM interview and produces a complete product brief.

**Trigger:** Say "I have an idea", "help me design an app", "I want to build X", or any pre-implementation framing.
**Route:** `/sarthi-pm` — always available, no extra tools required.

The flow works in 6 phases:

| Phase | What happens |
|-------|-------------|
| **1. Discovery** | 7 focused questions — problem, users, core action, success definition, scope, constraints, differentiation |
| **2. Synthesis** | Problem statement, user persona, 3–5 opinionated design principles |
| **3. SMART Objectives** | 3–5 objectives in Specific / Measurable / Achievable / Relevant / Time-bound format |
| **4. Sprint Breakdown** | Sprints with goals, deliverables, and definitions of done |
| **5. Product Brief** | Written to `docs/pm/PRODUCT_BRIEF.md` — a durable, updatable doc |
| **6. /goal Output** | A ready-to-paste `/goal` statement to anchor your Claude Code session |

### Sprint Planning

Once a brief exists, Sarthi can guide you through planning the next 1–N sprints and produce a `/goal` block for each.

**Trigger:** Say "plan next sprint", "sprint planning", "update sprint goal", or choose "Plan next sprint(s)" when `/sarthi-pm` detects an existing brief.

| Phase | What happens |
|-------|-------------|
Reads `docs/pm/PRODUCT_BRIEF.md`, confirms how many sprints to plan, then interviews you per sprint (goal, deliverables, end date, blockers). Writes new entries to the Sprint Breakdown section and emits a ready-to-paste `/goal` block for each sprint.

### /goal Integration

At the end of the flow, Sarthi produces a `/goal`-ready block:

```
/goal TaskFlow — help solo founders capture and prioritise tasks without switching apps.
Users: indie hackers running 1-person businesses. Current sprint: core capture + inbox flow.
Key principles: speed over completeness, one action per screen, offline-first.
SMART target: by 2026-08-15, 60% of users complete their first task within 5 min of signup.
Out of scope: team collaboration, billing, integrations.
```

Paste this into Claude Code at the start of any session. Claude stays anchored to your product context, sprint goal, and SMART objectives throughout — no repeated re-explaining needed. Update the `Current sprint` line as you advance.

If compound-engineering is installed, the flow optionally hands off to `/ce-strategy` and `/ce-brainstorm` to go deeper after the brief is written.

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

## 🔐 Pre-commit Secrets Scan (opt-in)

Installed during `/sarthi-setup`, this global git hook scans staged files for hardcoded secrets before every `git commit` — catching keys before they enter git history, not just during weekly audits.

**What it scans staged files for:**
- Anthropic, AWS, GitHub, Slack, and Google API keys
- Private key blocks (`-----BEGIN PRIVATE KEY-----`)
- Hardcoded `password`, `secret`, `api_key`, and `token` assignments

**How it works:**
- Runs automatically on every `git commit` across all repos on your machine
- Blocks the commit and shows the file path + line number if a match is found
- To bypass intentionally: `git commit --no-verify`
- To disable globally: `git config --global --unset core.hooksPath`

Enable during `/sarthi-setup`.

<details>
<summary>Manual install (if you prefer to configure the hook yourself)</summary>

```bash
mkdir -p ~/.claude/.sarthi-hooks
# write hook script to ~/.claude/.sarthi-hooks/pre-commit (see sarthi-setup/SKILL.md)
chmod +x ~/.claude/.sarthi-hooks/pre-commit
git config --global core.hooksPath ~/.claude/.sarthi-hooks
```

</details>

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
| **security-guidance** | Per-edit security warnings (XSS, injection, unsafe patterns) | [Anthropic](https://anthropic.com) | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| **code-review** | PR-level parallel code review via gh CLI | [Anthropic](https://anthropic.com) | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) |
| **andrej-karpathy-skills** | Coding discipline: think before coding, simplicity, surgical changes | [Forrest Chang](https://github.com/forrestchang) · [multica-ai](https://github.com/multica-ai) · principles by [Andrej Karpathy](https://x.com/karpathy) | [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) |

*Sarthi works with any combination of the above — or none at all. Each tool is installed independently.*

### Attribution Notes

- **Karpathy pre-flight** (cost guard step 6) — derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls, implemented as a Claude Code plugin by [Forrest Chang](https://github.com/forrestchang) and extended by [multica-ai](https://github.com/multica-ai).
- **SMART objectives** (sarthi-pm) — framework originally described by George T. Doran (1981), "There's a S.M.A.R.T. Way to Write Management's Goals and Objectives."
- **sarthi-audit security grep patterns** — derived from community security research and well-known credential format specifications (AWS, GitHub, Anthropic, Slack, Google).
- **sarthi-audit ethical hacker domain** — structured around OWASP Testing Guide and common penetration testing frameworks.

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
