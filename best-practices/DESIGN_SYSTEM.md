# DESIGN_SYSTEM.md

## Purpose
Defines reusable visual and interaction standards for this project.
Prevents design drift and reduces repetitive styling prompts to Claude Code.

---

## Critical Rule
Do not make visual design decisions inside Claude Code.
If a component's visual behaviour is undecided, stop and flag it.
Visual decisions are resolved in a prototyping tool first, then implemented here.

---

## Design Philosophy
- Prefer clean, purposeful layouts
- Maintain visual consistency across all screens
- Avoid excessive decoration or animation
- Use restrained, purposeful motion only
- Prioritise readability and clarity above all

---

## Fill This Section for Your Project

### Spacing Scale
<!-- Define your spacing tokens e.g. 4, 8, 12, 16, 24, 32, 48px -->

### Typography Hierarchy
<!-- Heading levels, body, caption — font family, size, weight, line height for each -->

### Colour Usage Rules
<!-- Primary, secondary, background, surface, error, success, warning, text colours -->
<!-- Light and dark mode values if applicable -->

### Component Standards
<!-- Define reusable components: cards, list items, section headers, badges -->

### Button Patterns
<!-- Primary, secondary, ghost, destructive — default, hover, disabled, loading states -->

### Form Patterns
<!-- Input fields, labels, placeholder text, validation states, error messages -->

### Cards
<!-- Border radius, shadow, padding, content layout rules -->

### Modals and Overlays
<!-- When to use modals vs bottom sheets vs drawers, header treatment, dismiss behaviour -->

### Loading States
<!-- Skeleton screens vs spinners — when to use each -->

### Empty States
<!-- Copy tone, illustration guidance, CTA placement -->

### Error States
<!-- Inline errors, full-page errors, toast notifications — when to use each -->

### Animations and Transitions
<!-- What animates, duration, easing values — keep minimal and purposeful -->

### Responsive Behaviour
<!-- Breakpoints, how layouts adapt across screen sizes or devices -->

### Dark Mode
<!-- Token swaps, exceptions, surface treatments -->

### Icons
<!-- Icon library used, sizing conventions, usage rules -->

---

## AI Agent Guidance
- Reuse existing UI components before creating new ones
- Maintain visual consistency across all screens
- Prefer established patterns over novelty
- If a visual decision is not defined here and not in CURRENT_SPRINT.md — stop and ask
- Do not invent new visual patterns mid-implementation
