# AI_WORKFLOW.md

## Purpose
Defines how Claude Code should operate within this repository to maximise output quality and minimise token consumption.

---

## Execution Philosophy
Optimise for sustained implementation momentum and production-quality output.

Prefer completing coherent feature slices end-to-end rather than fragmented partial implementations.

Pause and ask when:
- Architecture would change significantly
- A destructive action is involved
- Requirements are genuinely ambiguous
- A UI or flow decision has not been resolved yet — do not guess, ask

---

## Token Efficiency
Token waste causes mid-session cutoffs and lost momentum. These rules are non-negotiable:

- Consult governance markdown files before scanning the broader codebase
- Make targeted minimal edits — do not touch unrelated files
- Do not re-summarise completed work within the same session
- Batch related changes into one coherent pass rather than sequential small edits
- If a requirement is unclear, ask once concisely rather than implementing a guess
- Do not implement improvements outside the current task scope — note them as comments instead

---

## Workflow Principles
- Prefer minimal targeted edits over broad rewrites
- Avoid modifying unrelated files
- Reuse existing abstractions before inventing new ones
- Keep implementations modular and maintainable
- Prioritise readability and production readiness
- Avoid unnecessary dependency additions
- Briefly explain implementation approach before execution

---

## Pre-Implementation Gate
Before writing any code:
1. Is the UI and flow for this feature already decided? If not — do not implement. Resolve visually first.
2. Is this in scope per CURRENT_SPRINT.md? If not — flag it, don't build it.
3. Does an existing abstraction already handle this? Reuse it.

---

## Build Gate
Before suggesting or triggering a build:
- A complete tested feature slice is ready for validation
- This is not a visual check — visual decisions must precede implementation
- The sprint explicitly requires a build at this stage

Unnecessary builds waste time and, depending on the platform, build credits.

---

## Autonomous Behaviour
Proceed autonomously when:
- Requirements are clear and in scope
- Patterns already exist to follow
- Changes are contained to the targeted feature

Stop and ask when:
- UI layout or user flow has not been decided
- Requirements conflict with existing architecture
- A change would affect files beyond the targeted feature
- A new dependency would be introduced

---

## Primary Goal
Convert product requirements written in English into clean, maintainable, production-quality implementations with minimal supervision and maximum token efficiency.
