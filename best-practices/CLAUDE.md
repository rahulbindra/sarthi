# CLAUDE.md
# Initial AI Coding Instruction

## Before Implementing Anything
Consult these files in order:
1. CURRENT_SPRINT.md — what is in scope right now
2. ARCHITECTURE.md — non-negotiable system patterns
3. PRODUCT_PRINCIPLES.md — UX and product decision heuristics
4. DESIGN_SYSTEM.md — visual and interaction standards
5. API_PATTERNS.md — backend integration standards
6. IMPLEMENTATION_PATTERNS.md — coding conventions
7. AI_WORKFLOW.md — how to operate within this repository

---

## Core Instructions
- Reuse existing patterns before introducing new abstractions.
- Prefer coherent end-to-end feature implementation over partial work.
- Avoid modifying unrelated files.
- Prioritize maintainability and readability.
- Avoid unnecessary dependency additions.
- Maintain architectural consistency.
- Preserve UX consistency across all flows.
- Briefly explain your implementation approach before writing any code.
- Complete production-quality implementations with minimal supervision.

---

## Token Efficiency Rules
- Only load files relevant to the current task. Do not scan the entire codebase unnecessarily.
- Make targeted minimal edits. Do not rewrite files that don't need changing.
- Do not re-explain or re-summarise completed work within the same session.
- Batch related changes into single coherent implementations rather than sequential small edits.
- If a UI or flow decision is unclear, stop and ask rather than guessing and iterating.
- Never implement a visual decision that hasn't been resolved outside of Claude Code first.

---

## Build and Deployment Discipline
Do not suggest or trigger a build unless:
- A complete tested feature slice is ready for validation
- A critical bug fix needs device or environment-level verification
- The current sprint explicitly requires a build

Do not build to check visual output. Visual decisions must be resolved before implementation begins.

---

## Pre-Implementation Gate
Before writing any code, confirm:
1. Is the UI and flow for this feature already decided? If not — stop. Resolve visually first.
2. Is this change in scope for the current sprint? Check CURRENT_SPRINT.md.
3. Does an existing pattern or abstraction already cover this? Reuse it.

---

## Primary Goal
Convert product requirements written in English into clean, maintainable, production-quality implementations while preserving implementation momentum, architectural consistency, and token efficiency.
