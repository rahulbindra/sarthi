---
name: sarthi-pm
description: Guided product management flow for turning ideas into implementation-ready briefs. Use when the user has an idea, wants to design an app, plan a product, or think through features before building. Produces design principles, a design overview, SMART objectives, sprint breakdown, and a /goal-ready output. Triggers on "I have an idea", "help me design", "I want to build X", "product planning", "think through this with me", "design an app", "feature planning", "startup idea".
argument-hint: "[optional: describe your idea to skip the opening question]"
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
> "A product brief already exists at `docs/pm/PRODUCT_BRIEF.md`. Do you want to update it or start fresh?"
> - Update existing brief
> - Start fresh

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
Update the "Current sprint goal" line as you advance through sprints.
```

---

## Routing

If compound-engineering is installed:
- After Phase 2, optionally offer: "Want me to run `/ce-strategy` to write a formal STRATEGY.md alongside the brief?"
- After Phase 4, optionally offer: "Want me to run `/ce-brainstorm` to go deeper on the design before we build?"

These are additive — the brief is always produced regardless.
