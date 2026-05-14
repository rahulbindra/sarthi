# IMPLEMENTATION_PATTERNS.md

## Purpose
Defines preferred implementation style and coding conventions for this project.
Keeps code consistent, readable, and maintainable regardless of which session generated it.

---

## Core Principles
- Keep components and modules small and focused
- Prefer readability over cleverness
- Reuse existing patterns before creating new ones
- Keep business logic separate from presentation
- Write code that can be understood without deep context

---

## Fill This Section for Your Project

### Naming Conventions
<!-- Components, hooks, utilities, constants, files — define casing and prefix rules -->
- Components: PascalCase
- Hooks: camelCase with `use` prefix
- Utilities and helpers: camelCase
- Constants: UPPER_SNAKE_CASE
- Files: match the name of the primary export

### Component Structure
<!-- Preferred order within a component file -->
- Imports
- Types and interfaces
- Constants local to the component
- Props destructuring
- Hooks
- Derived state and computed values
- Event handlers and callbacks
- Return / JSX
- Styles (or reference to style file)

### State Management Conventions
<!-- How local vs global state is decided, naming patterns, update patterns -->

### Hook Conventions
<!-- When to extract a custom hook, how hooks are structured and named -->

### Forms
- Use consistent validation patterns across all forms
- Handle loading, error, and success states explicitly on every form
- Never leave a form without a visible error state
- Avoid inconsistent field handling approaches

### Error Handling
- Use user-friendly error messages — never show raw error objects to users
- Fail gracefully — a broken feature must not crash the app
- Avoid silent failures — every error must be logged or surfaced
- Define fallback states for all async operations

### Loading and Empty States
- Every async data fetch must have a loading state
- Every list or data view must have an empty state
- Do not render blank screens while data is loading

### File Organisation
<!-- Where different types of files live in the project structure -->

### Import Conventions
<!-- Absolute vs relative imports, import ordering, aliasing -->

### Testing Conventions (if applicable)
<!-- What gets tested, naming patterns for test files, mocking conventions -->

### Comments and Documentation
<!-- When to comment, what to document, JSDoc usage -->

---

## Token Efficiency in Implementation
- Do not implement features beyond what CURRENT_SPRINT.md defines
- Do not refactor code outside the current task scope
- If you notice an improvement opportunity outside scope — add a comment, do not implement it
- Prefer one well-structured implementation over iterative small patches
- Do not add placeholder code, stub functions, or TODO blocks unless explicitly asked

---

## AI Agent Guidance
- Complete coherent feature slices end-to-end
- Avoid partially implemented workflows — half-built features cause confusion and wasted follow-up tokens
- Maintain consistency with existing code patterns
- Optimise for maintainability and production readiness
- When uncertain about approach — ask once, then implement decisively
