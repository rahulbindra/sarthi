# ARCHITECTURE.md

## Purpose
Defines the core architecture and non-negotiable system patterns for this project.
Claude Code must consult this file before implementing any feature.

---

## Architectural Non-Negotiables
- Avoid introducing new state management approaches without discussion
- Prefer extending existing abstractions over creating new ones
- Keep business logic separated from UI components
- Maintain predictable folder structure
- Avoid premature optimisation abstractions
- Reuse existing implementation patterns whenever possible
- Prefer modular readable implementations over clever abstractions
- Never introduce a new dependency without flagging it first

---

## Fill This Section for Your Project

### Tech Stack
<!-- Languages, frameworks, platforms, runtime -->

### High-Level Architecture
<!-- How the app is structured at a high level — frontend, backend, services -->

### State Management
<!-- Library used, what is global vs local, conventions -->

### Routing and Navigation
<!-- Library, screen or page structure, deep linking if applicable -->

### Auth and Session Handling
<!-- Auth provider, token storage, session refresh strategy -->

### Database and Storage
<!-- Local storage, remote database, sync strategy -->

### Folder Structure
<!-- Top-level directory layout with the purpose of each folder -->

### Reusable Abstractions
<!-- Key hooks, utilities, services, components that already exist — do not recreate these -->

### Performance Considerations
<!-- Lazy loading, memoisation rules, list or data optimisation -->

### Anti-Patterns to Avoid
<!-- What has caused problems or been rejected — do not repeat these -->

---

## AI Agent Guidance
Before scanning the repository broadly:
1. Read this file
2. Reuse known patterns — do not rediscover what already exists
3. Extend existing architecture before inventing new structures
4. Propose new patterns before implementing them
5. Keep all implementation aligned with the conventions defined here
