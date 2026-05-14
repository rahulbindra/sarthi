# Optimizer — Intent Router for Claude Code

Optimizer detects what you're trying to do and routes you to the right tool automatically. It works with any combination of installed Claude Code tools and falls back gracefully to vanilla Claude when specialized tools aren't available.

## What it does

- **Detects intent** from your message (build, debug, review, ship, navigate, research...)
- **Routes automatically** to the best available tool in your stack
- **Falls back gracefully** — if a tool isn't installed, it uses vanilla Claude with the same structured approach
- **Enforces a cost-guard** — confirms your deliverable before starting, catches retry loops, suggests Codex for review tasks

## Install

```
/plugin marketplace add https://github.com/rahulbindra/optimizer-plugin
/plugin install optimizer
/reload-plugins
```

## Usage

Invoke manually at any time:
```
/optimizer
```

Or add to your global `~/.claude/settings.json` as a `SessionStart` hook to activate automatically every session:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "statusMessage": "Loading optimizer...",
        "command": "python3 -c \"import json; print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': 'Act as the Optimizer: read ~/.claude/skills/optimizer/SKILL.md and apply its routing rules to every user message this session.'}}))\" "
      }]
    }]
  }
}
```

## Routing table

| Intent | With tools | Without tools |
|--------|-----------|---------------|
| Build feature | `/ce-plan` → `/ce-work` | Step-by-step in chat |
| Debug | `/ce-debug` | Systematic root cause |
| Frontend/UI | `/ce-frontend-design` | Design-quality prompting |
| Review / PR | `/ce-code-review` + Codex | Structured review |
| Ship | `/ce-commit-push-pr` | git add/commit/push |
| Codebase nav | `graphify query` | Targeted grep |
| Research | `/firecrawl-search` | WebFetch |
| Cost check | `codeburn optimize` | Suggest `/compact` |
| Save learnings | `/revise-claude-md` | Manual CLAUDE.md edit |

## Cost guard

Before every task, Optimizer:
1. Asks for the one-sentence deliverable if missing
2. Uses graphify before grepping if a graph exists
3. Offers Codex dispatch for review/investigation tasks
4. Stops after two failed attempts and reconsiders

## Works great alongside

- [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin)
- [graphify](https://github.com/safishamsi/graphify)
- [superpowers](https://github.com/anthropics/claude-plugins-official)
- [codex](https://github.com/openai/codex-plugin-cc)
- [codeburn](https://github.com/nichochar/codeburn)
- [firecrawl](https://github.com/anthropics/claude-plugins-official)

## License

MIT
