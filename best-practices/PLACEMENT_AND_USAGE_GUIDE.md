# PLACEMENT AND USAGE GUIDE

## Overview
You have 8 governance files. This guide tells you exactly where each one goes,
how to use it, and when to update it — for both Claude.ai (chat UI) and Claude Code (terminal).

---

## The Two Environments

### Claude.ai (Chat UI)
Used for: planning, PRDs, sprint definition, architecture discussions, research,
document work, and conversations like this one.
Files go here as: Project Instructions (persistent) or uploaded attachments (per conversation).

### Claude Code (Terminal)
Used for: all actual coding, feature implementation, debugging, builds, deployments.
Files go here as: markdown files committed to your project repository.
Claude Code automatically reads CLAUDE.md from the repo root at the start of every session.

---

## File Placement — Complete Reference

| File | Claude.ai | Claude Code Repo Location |
|------|-----------|--------------------------|
| CLAUDE.md | Paste into Project Instructions | Root of repo (required name) |
| PRODUCT_PRINCIPLES.md | Paste into Project Instructions | /docs or repo root |
| CURRENT_SPRINT.md | Upload at start of planning chats | Root of repo, update each sprint |
| ARCHITECTURE.md | Upload when discussing architecture | /docs or repo root |
| DESIGN_SYSTEM.md | Upload when discussing UI | /docs or repo root |
| API_PATTERNS.md | Upload when discussing integrations | /docs or repo root |
| IMPLEMENTATION_PATTERNS.md | Rarely needed in chat | /docs or repo root |
| AI_WORKFLOW.md | Not needed in chat | /docs or repo root |

---

## Claude.ai Setup — Do This Once Per Project

### Step 1: Create a Project
In Claude.ai, create a Project for each app or major work area.
Example projects: "My iOS App", "Marketing Site", "Work Research"

### Step 2: Add Project Instructions
Inside each project → click the project name → Edit Project → Custom Instructions.

Paste the contents of these two files:
1. CLAUDE.md (the full text)
2. PRODUCT_PRINCIPLES.md (the full text, appended below CLAUDE.md)

These apply automatically to every conversation inside that project.
You do not need to re-upload them.

### Step 3: Upload Per-Conversation When Relevant
At the start of a planning or sprint conversation, upload:
- CURRENT_SPRINT.md — always, for any dev-related conversation
- ARCHITECTURE.md — when discussing technical structure
- DESIGN_SYSTEM.md — when discussing UI or visual decisions

Do not upload all files every conversation. Only upload what is relevant.
Uploading unnecessary files wastes context window and tokens.

---

## Claude Code Setup — Do This Once Per Repo

### Step 1: Add CLAUDE.md to Repo Root
Place CLAUDE.md in the root of your repository.
Claude Code reads this file automatically at the start of every session.
This is your most important file — it sets the rules for every session without you having to repeat them.

### Step 2: Add Governance Files to /docs
Place these files in a /docs folder (or repo root if you prefer flat structure):
- ARCHITECTURE.md
- PRODUCT_PRINCIPLES.md
- DESIGN_SYSTEM.md
- API_PATTERNS.md
- IMPLEMENTATION_PATTERNS.md
- AI_WORKFLOW.md
- CURRENT_SPRINT.md

Commit all of these to version control so they travel with the codebase.

### Step 3: Update CURRENT_SPRINT.md Before Every Session
This is the one file that changes regularly. Before opening Claude Code:
- Clear the previous sprint's content
- Fill in the new sprint goal, in-scope tasks, and UI/flow status table
- Commit the update

Claude Code reads this and stays within scope. An empty or stale CURRENT_SPRINT.md
is the most common cause of scope creep and token waste.

---

## Ongoing Maintenance

### Update Frequency

| File | When to Update |
|------|---------------|
| CURRENT_SPRINT.md | Before every development session |
| ARCHITECTURE.md | When architecture changes |
| DESIGN_SYSTEM.md | When new UI patterns are established |
| API_PATTERNS.md | When new integrations are added |
| IMPLEMENTATION_PATTERNS.md | When conventions evolve |
| PRODUCT_PRINCIPLES.md | When product direction changes |
| CLAUDE.md | Rarely — only if workflow fundamentally changes |
| AI_WORKFLOW.md | Rarely — only if workflow fundamentally changes |

### Filling Placeholder Sections
Several files contain placeholder sections marked with HTML comments.
Fill these with your actual project details as your codebase grows.

Priority order:
1. CURRENT_SPRINT.md — fill before every session, always
2. ARCHITECTURE.md — fill once early, critical for consistency
3. DESIGN_SYSTEM.md — fill before UI-heavy sprints
4. API_PATTERNS.md — fill as integrations are built
5. IMPLEMENTATION_PATTERNS.md — fill as conventions solidify

---

## The Single Most Important Workflow Rule

Before opening Claude Code for any new feature or change:

1. Is the UI and flow decided? → If not, use a visual prototyping tool first
2. Is CURRENT_SPRINT.md updated with exactly what you want? → If not, update it
3. Only then open Claude Code

This prevents the blind iteration loop: idea → build → doesn't look right →
back to Claude Code → repeat. That loop is the primary driver of token exhaustion
and unnecessary builds.

---

## Quick Reference Card

Starting a planning conversation in Claude.ai:
→ Open project → upload CURRENT_SPRINT.md → start conversation

Starting a dev session in Claude Code:
→ Update CURRENT_SPRINT.md → commit → open Claude Code → it reads CLAUDE.md automatically

Something looks wrong visually:
→ Do not ask Claude Code to fix it → open Lovable → resolve visually → come back with a clear brief

Adding a new project:
→ Copy all 8 files → fill in project-specific placeholders → add CLAUDE.md to repo root → add rest to /docs
