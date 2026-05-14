# PRODUCT_PRINCIPLES.md

## Purpose
Defines product philosophy and UX decision-making principles for this project.
Claude Code uses this to make implementation decisions that align with product intent.

---

## Product Summary
<!-- One paragraph describing what this product is, who it is for, and what problem it solves -->

---

## Product Philosophy
<!-- Define the core values that guide product decisions -->
- Prioritise clarity over feature density
- Favour simplicity over complexity
- Optimise for intuitive flows — users should not need to be taught
- Prefer frictionless interactions
- Avoid unnecessary complexity
- Shipping a focused thing well beats shipping many things poorly

---

## Product Decision Heuristics
When tradeoffs exist, default to:
- Clarity over feature density
- Calm UX over visual complexity
- Speed of interaction over excessive animation
- Intuitive defaults over heavy customisation
- Shipping velocity over overengineering
- UX consistency across all flows

When a UI decision is not clear — stop. Do not implement a guess. Resolve visually first.

---

## UX Principles
- Keep interfaces visually clean
- Minimise cognitive load
- Use progressive disclosure when complexity is unavoidable
- Design for smooth onboarding and discoverability
- Ensure consistent behaviour across all screens and flows

---

## What Belongs Where
| Decision Type | Where to Resolve |
|--------------|-----------------|
| Screen layout, spacing, visual hierarchy | Visual prototyping tool (e.g. Lovable) |
| User flow and navigation sequencing | Visual prototyping tool |
| Component look and feel | Visual prototyping tool |
| "Does this feel right?" | Visual prototyping tool |
| Logic, data handling, integrations | Claude Code |
| Auth, APIs, backend | Claude Code |
| Final implementation of decided UI | Claude Code |

Never use Claude Code to make visual or flow decisions. That is where build cycles get wasted.

---

## Accessibility Expectations
- Maintain accessible typography and contrast ratios
- Support keyboard navigation where applicable
- Use touch-friendly tap targets on mobile
- Avoid inaccessible interaction patterns

---

## AI Agent Guidance
Make implementation decisions that align with:
- Simplicity and clarity
- Consistency across flows
- Usability and discoverability
- Maintainability
- Production readiness
- Token efficiency — do not over-build or gold-plate
