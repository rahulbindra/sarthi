---
name: sarthi-pm
description: Guided product management flow for turning ideas into implementation-ready briefs, and for planning upcoming sprints. Use when the user has an idea, wants to design an app, plan a product, or think through features before building. Also use when the user wants to plan next sprint(s), update sprint goals, or advance through a sprint breakdown. Produces design principles, a design overview, SMART objectives, sprint breakdown, and a /goal-ready output per sprint. Triggers on "I have an idea", "help me design", "I want to build X", "product planning", "think through this with me", "design an app", "feature planning", "startup idea", "plan next sprint", "sprint planning", "update sprint goal", "plan sprints".
argument-hint: "[optional: describe your idea or say 'plan next sprint' to go straight to sprint planning]"
---

# Sarthi PM Flow

*Guides the user from raw idea → implementation-ready product brief with SMART objectives and a `/goal`-ready output.*

This skill runs a structured PM interview, synthesises the answers, and produces:
1. A **Product Brief** (`docs/pm/PRODUCT_BRIEF.md`) — problem, users, design principles, design overview, SMART objectives, sprint breakdown
2. A **/goal statement** — a single paragraph the user can paste into `/goal` to anchor their Claude Code session to this product

When compound-engineering is installed, this skill hands off to `ce-strategy`, `ce-brainstorm`, and `ce-plan` at the right phases and enriches their output with SMART objectives and the `/goal` block. When compound-engineering is not installed, it runs the full flow natively.

---

## Interaction Method

Use `AskUserQuestion` (call `ToolSearch` with `select:AskUserQuestion` first to load its schema). Ask **one question at a time**. Wait for the answer before continuing. Never batch questions.

---

## Phase 0 — Check for existing brief

```bash
[ -f docs/pm/PRODUCT_BRIEF.md ] && echo "exists" || echo "new"
```

If a brief exists, ask:
> "A product brief already exists at `docs/pm/PRODUCT_BRIEF.md`. What would you like to do?"
> - Plan next sprint(s) — advance the sprint breakdown and get a /goal statement
> - Update the brief — revise problem, objectives, or scope
> - Start fresh — new product, new brief

**If the user chooses "Plan next sprint(s)"** — jump directly to the Sprint Planning Flow below. Skip Phases 1–6 entirely.

If updating: read the existing file, use it as context, and skip questions the file already answers clearly. Only ask about gaps or changed areas.

---

## Phase 1 — Discovery Interview

Ask the following questions one at a time. Adapt the phrasing naturally — don't read them verbatim if the conversation has already covered the answer.

**Q1 — The Problem**
> "What problem are you trying to solve — and who has this problem? Be as specific as you can."

Push back if the answer is too broad (e.g. "people don't have enough time"). Ask: "Can you describe a specific moment when someone feels this problem?"

**Q2 — The User**
> "Who is your primary user? Describe them concretely — their role, context, and what they're trying to accomplish."

**Q3 — The Core Action**
> "What is the single most important thing your product lets someone do that they can't do easily today?"

**Q4 — Success**
> "What does success look like 3 months after launch? What would you see happening — in numbers, behaviour, or outcomes — that would tell you it's working?"

Use this answer to anchor the SMART objectives later.

**Q5 — Scope**
> "What are the must-have features for the first version — the ones without which the product doesn't work? And what's explicitly out of scope for now?"

**Q6 — Constraints**
> "What are your biggest constraints? (e.g. team size, timeline, budget, technology, regulatory)"

**Q7 — Inspiration & Differentiation**
> "Are there existing products that solve part of this problem? What do you want to do differently or better?"

---

## Phase 2 — Synthesise

After all questions are answered, synthesise without asking further questions. Produce the following internally (you will write them to the brief in Phase 5):

### Problem Statement
One paragraph. Format:
> "[User type] struggle to [problem] when [context]. Today they [current workaround], which [why it fails]. [Product name / "This product"] solves this by [core approach]."

### User Persona
Name, role, context, primary goal, biggest frustration.

### Design Principles
3–5 opinionated principles that should guide every product and design decision. These are not values — they are decision rules. Each principle must have a name and a one-sentence "this means we will / won't" rule.

Example format:
> **Speed over completeness** — We ship a working slice before a full solution. A partial feature that ships beats a perfect one that doesn't.

### Design Overview
- Core user flows (numbered, 3–5 steps each)
- Key surfaces / screens
- Data model sketch (primary entities and relationships)
- Technical stack recommendation (if enough context exists)

---

## Phase 3 — SMART Objectives

Derive 3–5 SMART objectives from the success answer in Q4 and the scope from Q5.

Each objective must follow this format exactly:

```
Objective N: [Name]
  Specific:     [What exactly will be achieved]
  Measurable:   [How it will be measured — metric + target number]
  Achievable:   [Why this is realistic given constraints]
  Relevant:     [How it connects to the core problem]
  Time-bound:   [Deadline — use absolute date: e.g. 2026-08-15]
```

Produce a summary line after each objective:
> "By [date], [metric] will reach [target], measured by [measurement method]."

---

## Phase 4 — Sprint Breakdown

Break the must-have scope into sprints of 1–2 weeks each. Use this structure:

```
Sprint 0 — Foundation (Week 1)
  Goal: [One sentence]
  Deliverables:
    - [ ] Set up repo, CI, dev environment
    - [ ] Data model implemented and migrated
    - [ ] Auth flow working end-to-end
  Definition of done: [Specific, testable condition]

Sprint 1 — Core Flow (Weeks 2–3)
  Goal: [One sentence — the MVP user journey]
  Deliverables:
    - [ ] [Feature A]
    - [ ] [Feature B]
  Definition of done: [A real user can complete [core action] end-to-end]

Sprint 2 — Feedback Loop (Weeks 4–5)
  Goal: [One sentence — iterate based on early use]
  Deliverables:
    - [ ] [Improvement or additional feature]
  Definition of done: [Specific condition]

[Continue for remaining scope...]

Launch Sprint — Polish & Ship
  Goal: [Production readiness]
  Deliverables:
    - [ ] Error handling, edge cases
    - [ ] Analytics instrumentation for SMART metrics
    - [ ] Documentation
  Definition of done: [All SMART objectives have tracking in place]
```

If compound-engineering is installed, invoke `/ce-plan` with the scope summary as input and incorporate its output into the sprint breakdown.

---

## Phase 5 — Write the Product Brief

Create `docs/pm/` if it doesn't exist. Write `docs/pm/PRODUCT_BRIEF.md`:

```markdown
# Product Brief — [Product Name]

> Last updated: [today's date]

---

## Problem Statement

[Phase 2 output]

## User Persona

[Phase 2 output]

## Design Principles

[Phase 2 output — numbered list]

## Design Overview

### Core User Flows
[Phase 2 output]

### Key Surfaces
[Phase 2 output]

### Data Model
[Phase 2 output]

### Technical Stack
[Phase 2 output — or "TBD" if insufficient context]

---

## SMART Objectives

[Phase 3 output — all objectives in structured format]

---

## Sprint Breakdown

[Phase 4 output]

---

## /goal Statement

> Copy the block below and paste it into `/goal` to anchor your Claude Code session to this product.

```
[Product Name] — [one-sentence problem statement]

Users: [user persona summary]

Design principles:
- [Principle 1 name]: [rule]
- [Principle 2 name]: [rule]
- [Principle 3 name]: [rule]

Current sprint goal: [Sprint 1 goal — update as sprints advance]

SMART objective in focus: [Most important current objective summary line]

Out of scope for now: [Key exclusions]
```
```

---

## Phase 6 — Present the /goal Output

After writing the file, present this to the user in the chat:

```
Product brief written to docs/pm/PRODUCT_BRIEF.md.

─────────────────────────────────────────────
Your /goal statement (copy and run in Claude Code):
─────────────────────────────────────────────

/goal [Product Name] — [one-sentence problem]. Users: [persona]. Current sprint: [Sprint 1 goal]. Key principles: [principle 1], [principle 2], [principle 3]. SMART target: [most important objective summary line]. Out of scope: [exclusions].

─────────────────────────────────────────────

Paste this into Claude Code at the start of any session to keep Claude
anchored to your product context, sprint goal, and SMART objectives.
Run /sarthi-pm and choose "Plan next sprint(s)" when you're ready to advance.
```

---

## Sprint Planning Flow

*Triggered when the user says "plan next sprint", "sprint planning", "update sprint goal", "plan sprints", or chooses "Plan next sprint(s)" at Phase 0.*

This flow reads the existing product brief, identifies where you are in the sprint breakdown, and guides you through planning the next 1–N sprints. It produces a `/goal`-ready block for the sprint you are about to start.

---

### SP Phase 1 — Read context from existing brief

```bash
cat docs/pm/PRODUCT_BRIEF.md 2>/dev/null || echo "no-brief"
```

If no brief exists:
> "No product brief found at `docs/pm/PRODUCT_BRIEF.md`. Run `/sarthi-pm` first to create one, then come back for sprint planning."
Exit.

If brief exists, extract:
- Product name and one-line problem statement
- Sprint breakdown (all sprints with their goals and completion status)
- SMART objectives
- Current sprint (infer from checked-off deliverables or "Current sprint goal" in the /goal block)

Identify the **next sprint to plan** — the first sprint in the breakdown with no goal or unchecked deliverables and no explicit start.

---

### SP Phase 2 — Confirm sprint position and scope

Use `AskUserQuestion` to ask:

> "Based on your brief, the next sprint to plan appears to be **[Sprint N — Name]**. How many sprints would you like to plan in this session?"

Options:
- Just the next sprint (Sprint N)
- Next 2 sprints
- Next 3 sprints
- Let me choose a different sprint

Wait for the answer. Adjust the sprint range accordingly.

---

### SP Phase 3 — Interview for each sprint

For each sprint being planned, ask the following one at a time using `AskUserQuestion`:

**Goal question:**
> "What is the single-sentence goal for [Sprint N]? What should someone be able to do or see at the end of this sprint that they couldn't before?"

Push back if the goal is too vague or covers too much. A good sprint goal fits in one sentence and is testable.

**Deliverables question:**
> "What are the 3–5 key deliverables for [Sprint N]? List the concrete outputs, not the work tasks."

**End date question:**
> "When does [Sprint N] end? Give me an absolute date (e.g. 2026-06-30)."

**Blockers question:**
> "Any known blockers, dependencies, or risks for [Sprint N]? (Press enter to skip)"

Repeat for each sprint in the planned range.

---

### SP Phase 4 — Update PRODUCT_BRIEF.md

Update the Sprint Breakdown section of `docs/pm/PRODUCT_BRIEF.md` with the newly planned sprints. Use this format for each:

```
Sprint N — [Name] (ends [date])
  Goal: [One sentence]
  Deliverables:
    - [ ] [Deliverable 1]
    - [ ] [Deliverable 2]
    - [ ] [Deliverable 3]
  Blockers: [Any flagged, or "None"]
  Definition of done: [A real user can / [specific testable condition]]
```

Also update the `/goal Statement` section in the brief — set "Current sprint goal" to the goal of the first sprint being started now.

Update the `Last updated` date at the top of the file.

---

### SP Phase 5 — Present /goal output per sprint

Present the /goal block for the sprint the user is about to start (the first one planned):

```
Sprint [N] planned and brief updated.

─────────────────────────────────────────────
/goal statement for Sprint [N] — paste into Claude Code:
─────────────────────────────────────────────

/goal [Product Name] — [one-sentence problem]. Users: [persona]. Current sprint: [Sprint N goal]. Key principles: [principle 1], [principle 2]. SMART target: [objective most relevant to this sprint]. Sprint ends: [date]. Out of scope this sprint: [anything explicitly deferred].

─────────────────────────────────────────────

When Sprint [N] is complete, run /sarthi-pm → "Plan next sprint(s)" to advance to Sprint [N+1].
```

If multiple sprints were planned, also show the /goal blocks for subsequent sprints so the user can save them:

```
Upcoming sprint /goal statements (save these for later):

Sprint [N+1]: /goal [Product Name] — [...]. Current sprint: [Sprint N+1 goal]. Sprint ends: [date].
Sprint [N+2]: /goal [Product Name] — [...]. Current sprint: [Sprint N+2 goal]. Sprint ends: [date].
```

---

## Routing

If compound-engineering is installed:
- After Phase 2, optionally offer: "Want me to run `/ce-strategy` to write a formal STRATEGY.md alongside the brief?"
- After Phase 4, optionally offer: "Want me to run `/ce-brainstorm` to go deeper on the design before we build?"

These are additive — the brief is always produced regardless.
