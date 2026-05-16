---
date: 2026-05-16
topic: sarthi-test
---

# sarthi-test — Persona-Based Automated App Testing

## Summary

A new general-purpose Sarthi skill (`sarthi-test`) that spawns one Claude sub-agent per persona to browser-test a locally-started app against the latest GitHub commit. Runs on a cron via Sarthi's `/schedule` infrastructure, uses diff-scoped testing by default, and produces per-run HTML reports with optional feedback fields. Personas self-learn over time — accumulating system observations from repeated runs and developer corrections from the HTML feedback surface — with zero mandatory developer input.

---

## Problem Frame

Developers building apps with real user personas — onboarding flows, role-specific dashboards, multi-step workflows — have no automated way to validate those flows from the perspective of each persona as commits land. Manual testing is expensive and skipped under time pressure. Existing CI solutions (Playwright, Cypress) catch regressions but produce pass/fail output, not the qualitative "this felt confusing to a first-time user" feedback that actually improves UX.

The gap is widest when a developer is coding independently and wants parallel feedback without context-switching. There is no tool today that runs in the background, reads who your users are, and reports back as if those users just tried your latest commit.

---

## Actors

- A1. **Developer**: Owns the app repo, configures the skill, reads HTML reports and optionally submits persona feedback.
- A2. **Persona sub-agent**: One Claude agent per persona — reads persona profile and memory file, drives the browser, writes its section of the report.
- A3. **Sarthi orchestrator**: The `sarthi-test` skill itself — polls GitHub, decides crawl mode, starts the app, spawns sub-agents, merges reports, and updates persona memory files.
- A4. **GitHub**: Source of commits and diffs; polled by the cron trigger.
- A5. **Persona memory file**: Per-persona persistent file (`.sarthi/persona-memory/<name>.md`) accumulating system observations and developer feedback across runs. Read by A2 at brief time; written by A3 (system) and A1 (developer).

---

## Key Flows

- F1. **Scheduled commit check**
  - **Trigger:** Sarthi `/schedule` cron fires (configurable interval, e.g., every 30 min)
  - **Actors:** A3, A4
  - **Steps:**
    1. Fetch latest commit SHA from GitHub for the configured repo/branch
    2. Compare against last-tested SHA stored in local state
    3. If no new commits — exit silently
    4. Compute diff stats (files changed, lines changed) since last-tested SHA
    5. Determine crawl mode: if 3+ days since last full crawl AND diff is large → full crawl; otherwise → diff-scoped
    6. Proceed to F2
  - **Outcome:** Crawl mode and diff summary are ready; run proceeds or exits
  - **Covered by:** R1, R2, R3, R4, R5

- F2. **App start and persona dispatch**
  - **Trigger:** F1 completes with a new commit to test
  - **Actors:** A3, A2
  - **Steps:**
    1. Read persona source: check for personas file; if absent, infer personas from codebase
    2. Start the app locally using the configured start command; wait for readiness
    3. Spawn one sub-agent per persona (up to the configured cap) in parallel
    4. Each sub-agent receives: persona profile, persona memory file contents, diff summary or full-crawl flag, start URL, report format contract
    5. Sub-agents navigate the app, interact as the persona, and write their findings
    6. Collect completed sub-agent outputs; if a sub-agent fails, its section is marked as errored and others continue
  - **Outcome:** All persona sections collected (complete or errored)
  - **Covered by:** R6, R7, R8, R9, R10, R11

- F3. **Report merge, delivery, and memory update**
  - **Trigger:** F2 completes
  - **Actors:** A3, A1, A5
  - **Steps:**
    1. Merge persona sections into a single HTML report with one feedback field per persona section
    2. Write report to `docs/persona-tests/<commit-sha>.html`
    3. Shut down the locally-started app
    4. For each persona: compare this run's findings against the previous run's findings; if the same flow produced a negative signal (confusion, error, dead end) in both runs, append a system observation to that persona's memory file
    5. For each persona: if a flow that was previously flagged in memory produced no negative signal this run, append a resolution note to that persona's memory file
    6. Persist updated state: last-tested SHA, last-full-crawl SHA, last-full-crawl diff stats, per-persona last-run findings summary
  - **Outcome:** HTML report available; persona memory files updated; developer reads report and optionally submits feedback
  - **Covered by:** R12, R13, R14, R18, R20, R21

- F4. **Developer feedback capture**
  - **Trigger:** Developer submits optional feedback for a persona section in the HTML report
  - **Actors:** A1, A5
  - **Steps:**
    1. Developer types feedback in the persona's feedback field in the HTML report
    2. Feedback is submitted (mechanism deferred to planning)
    3. Text is appended to that persona's memory file with a timestamp and labeled as developer feedback
  - **Outcome:** Persona memory file updated; feedback will be included in the next run's brief for that persona
  - **Covered by:** R19

---

## Requirements

**Trigger and scheduling**

- R1. The skill registers as a Sarthi `/schedule` cron job. The cron interval is configurable; default is every 30 minutes.
- R2. On each cron tick, the skill fetches the latest commit SHA from GitHub for the configured repo and branch, and compares it to the last-tested SHA in local state. If no new commits exist, the run exits silently with no output.
- R3. The skill skips a run entirely if the diff since the last-tested commit is empty (no file changes).

**Crawl mode selection**

- R4. By default, each run is diff-scoped: only flows touching files changed in the diff are tested.
- R5. A full app crawl is triggered when both conditions are true: (a) 3 or more days have elapsed since the last full crawl, AND (b) the diff since the last full crawl exceeds the configured size threshold. If either condition is false, the run stays diff-scoped.
- R6. The diff size threshold for triggering a full crawl is configurable per project, with a default of 10 files changed or 200 lines changed (whichever is reached first).

**Persona resolution**

- R7. If a personas file exists in the project (e.g., `.sarthi/personas.yml`), it is the authoritative persona source. Each persona entry includes at minimum: name, role, goals, pain points.
- R8. If no personas file exists, the skill infers personas from the codebase — reading user model definitions, onboarding copy, role enumerations, and similar sources. Inferred personas are included in the report with a note that they were inferred, not declared.

**Sub-agent dispatch**

- R9. The skill spawns one Claude sub-agent per persona in parallel, up to a configured cap (default: 3 concurrent persona agents).
- R10. Each sub-agent is briefed with: the persona profile, the persona's memory file contents (if any), a diff summary (or full-crawl flag), the app's start URL, and the expected report section format.
- R11. If a persona sub-agent fails or errors, its report section is marked as errored. The remaining sub-agents are not affected and the run continues to completion.

**App lifecycle**

- R12. The skill starts the app locally using the configured start command (e.g., `npm run dev`, `rails server`). It waits for the app to be ready before dispatching sub-agents, using a configurable readiness check (e.g., polling the start URL).
- R13. After all sub-agents complete, the skill shuts down the locally-started app process regardless of success or failure.

**Report output**

- R14. After each run, an HTML report is written to `docs/persona-tests/<commit-sha>.html` in the project repo. The report includes: commit SHA, timestamp, crawl mode used, one section per persona (findings, screenshots if captured, overall assessment, and an optional feedback text field), and a summary of any errored persona agents.

**Cost guard**

- R15. The number of concurrent persona sub-agents is capped (default 3, configurable). Runs with no new commits or an empty diff are skipped before any sub-agents are spawned. The cost guard rules are logged per run.

**Configuration**

- R16. Per-project configuration lives in a `.sarthi/tester.yml` file in the repo. It covers at minimum: GitHub repo and branch, app start command, start URL, persona cap, diff size threshold, readiness check, and cron interval.

**Self-learning and persona memory**

- R18. Each persona has a persistent memory file at `.sarthi/persona-memory/<persona-name>.md`. This file is included in the persona sub-agent's brief on every run, compounding context from past observations and developer corrections.
- R19. The HTML report includes an optional text feedback field per persona section. When a developer submits feedback for a persona, that text is appended to the persona's memory file with a timestamp, labeled as developer feedback.
- R20. After each run, the skill compares findings against the prior run for each persona. If the same flow, screen, or pattern produced a negative signal (confusion, friction, error, or dead end) in two or more consecutive runs, the skill appends a system-generated observation to the persona's memory file, labeled as system-observed.
- R21. When a flow previously flagged in a persona's memory file produces no negative signal for two or more consecutive runs, the skill appends a system-generated resolution note to the memory file.
- R22. Persona memory files are plain text and can be edited directly by the developer to add, correct, or remove observations at any time. Manual edits take effect on the next run.
- R23. If a persona has no memory file yet (first run), the sub-agent runs with profile only. The memory file is created automatically after the first run that produces any system observation.

**Sarthi router integration**

- R24. The skill is registered in the Sarthi router as a new intent, triggering on phrases such as "run persona tests", "sarthi test", and "test my app".

---

## Acceptance Examples

- AE1. **Covers R5, R6.** Given 4 days have elapsed since last full crawl and the diff since then is 3 files and 40 lines (below the 10-file / 200-line threshold), when the cron fires and finds a new commit, the run uses diff-scoped mode, not full crawl.

- AE2. **Covers R5, R6.** Given 4 days have elapsed since last full crawl and the diff since then is 15 files and 500 lines (above threshold), when the cron fires and finds a new commit, the run uses full crawl mode.

- AE3. **Covers R5.** Given only 1 day has elapsed since last full crawl and the diff is large (500+ lines), when the cron fires, the run stays diff-scoped — the time condition is not met.

- AE4. **Covers R11.** Given 3 persona sub-agents are dispatched and one crashes mid-run, when the remaining two complete, the report includes two complete persona sections and one section marked "errored — agent did not complete", and the app is shut down normally.

- AE5. **Covers R2, R3.** Given the last-tested SHA matches the latest GitHub commit SHA, when the cron fires, the run exits silently with no app start, no sub-agents spawned, and no report written.

- AE6. **Covers R8.** Given no `.sarthi/personas.yml` exists, when the skill runs, it reads the codebase to infer personas and the report notes each inferred persona with "inferred from codebase — declare in `.sarthi/personas.yml` to override."

- AE7. **Covers R20.** Given persona "Sarah" flagged confusion on the onboarding split-screen in run N and run N+1, after run N+1 completes the skill appends to `.sarthi/persona-memory/sarah.md`: a system-generated observation noting the onboarding split-screen has triggered friction in 2 consecutive runs.

- AE8. **Covers R21.** Given persona "Sarah" had a system observation flagging the onboarding split-screen, and run N+2 produces no negative signal on that flow, after run N+2 completes the skill appends a resolution note to sarah.md indicating the flagged flow now appears resolved.

- AE9. **Covers R18, R10.** Given `.sarthi/persona-memory/sarah.md` contains two prior observations (one system-generated, one developer feedback), when the next run dispatches Sarah's sub-agent, the brief includes the full contents of that memory file alongside the persona profile.

- AE10. **Covers R19.** Given a developer types "Sarah seemed to ignore the secondary CTA — she should be more likely to click it" in the HTML feedback field for Sarah's section and submits it, the text is appended to `.sarthi/persona-memory/sarah.md` with the current timestamp, labeled as developer feedback.

- AE11. **Covers R23.** Given it is Sarah's first ever run and no memory file exists, the sub-agent runs with Sarah's profile only and no memory context. If the run produces a system observation, `.sarthi/persona-memory/sarah.md` is created after the run. If not, no file is created.

---

## Success Criteria

- A developer can push a commit, continue coding, and find an HTML report in `docs/persona-tests/` within one cron interval — without any manual trigger.
- Feedback reads as qualitative, persona-voiced observations ("the onboarding CTA was not visible on the first screen for a first-time user") rather than pass/fail test output.
- Full crawl fires only when there is enough change to warrant it — small commits do not trigger expensive full runs.
- Adding a new persona to `.sarthi/personas.yml` automatically includes that persona in the next run with no other configuration.
- After 5 or more runs with zero developer feedback, persona memory files contain meaningful system-generated observations that measurably shape sub-agent behavior — the system learns without any manual input.
- A developer who submits one line of feedback in the HTML report sees that correction reflected in the next run's persona behavior, with no additional configuration.
- A planning agent reading this document can proceed without inventing trigger logic, crawl mode rules, persona resolution behavior, report structure, or memory accumulation logic.

---

## Scope Boundaries

- GitHub Actions or cloud-native CI integration — deferred; schedule cron is the trigger for v1
- API / HTTP-level testing — browser automation only; no raw HTTP persona simulation
- Deployed or staging URL targets — local app start only in v1
- Posting feedback to GitHub PRs as comments — HTML report only; no GitHub API writes
- Testing multiple apps in a single run — one app per run
- Cross-run dashboards or trend visualization — memory files and per-run HTML reports are the artifact; no aggregated UI
- Playwright or generated test script output — Approach B was explicitly rejected in favor of LLM-driven browser agents
- Mandatory developer feedback — feedback is always optional; the system learns from observations alone if the developer never submits any

---

## Key Decisions

- **Approach C (parallel sub-agents + Claude in Chrome MCP) over generated Playwright scripts:** Generated scripts catch regressions but lose persona nuance. The goal is qualitative, persona-voiced feedback — which requires LLM judgment per interaction, not script execution.
- **Diff-scoped by default, full crawl gated on both time AND diff size:** Running a full crawl on every small commit would be expensive and low-signal. The dual gate (3 days elapsed AND large diff) ensures full crawls fire when they actually matter.
- **Hybrid persona source (file overrides, codebase as fallback):** Requiring a personas file adds friction for new projects. Inferring from the codebase lowers the barrier to first run, with a clear path to declaring personas explicitly.
- **Local app start managed by the skill:** Avoids requiring a deployed staging environment. Developers testing on their local machine get coverage without CI/CD dependencies.
- **Per-persona sub-agent isolation:** Failure in one persona agent must not abort others. Partial reports are more useful than no report.
- **HTML report over markdown:** The report needs an interactive feedback field per persona. Markdown cannot host a feedback UX; HTML can. The HTML file is the single artifact — no separate markdown companion.
- **System + developer both write to persona memory:** Keeping a separate system state file would mean two sources of truth for each persona's learned context. A single human-readable memory file that both the system and developer append to is simpler, auditable, and correctable by direct edit.
- **Two-consecutive-run threshold for system observations:** A single run's negative signal could be a fluke (network hiccup, timing issue). Two consecutive runs on the same flow is the minimum evidence of a real pattern worth recording.
- **Self-learning is additive, never destructive:** The skill only appends to memory files; it never removes or overwrites entries. Removal is always a developer action. This ensures the developer stays in control of the ground truth.

---

## Dependencies / Assumptions

- Claude in Chrome MCP is installed and available in the developer's Claude Code environment (detected as present in the current setup).
- Sarthi's `/schedule` skill is available and functional for cron job creation.
- The app can be started and stopped via a single shell command; multi-process start sequences may require a wrapper script.
- `docs/persona-tests/` and `.sarthi/persona-memory/` directories will be created by the skill on first run if they do not exist.
- GitHub API access (public repos or a configured token) is available for commit and diff fetching.
- "Large diff" threshold defaults are calibrated for typical feature-sized commits; projects with unusually large or small commits may need to tune them.

---

## Outstanding Questions

### Resolve Before Planning

- [Affects R12][User decision] What is the readiness check strategy when the app's start URL is not HTTP-accessible immediately — should the skill poll with a timeout, or require the developer to specify a custom readiness command?

### Deferred to Planning

- [Affects R7][Technical] What is the exact YAML schema for `.sarthi/personas.yml` — field names, required vs optional, how multiple personas are listed?
- [Affects R9][Technical] Does the Claude in Chrome MCP support parallel sessions from within a single Claude Code instance, or must persona sub-agents be dispatched as separate Agent tool calls with sequential browser sessions?
- [Affects R8][Needs research] What codebase signals reliably indicate persona definitions — user model role fields, onboarding copy files, seed data, README personas sections? Which signals produce the highest-quality inferred personas?
- [Affects R14][Technical] Does Claude in Chrome MCP automatically capture screenshots, or must sub-agents explicitly invoke a screenshot tool at key moments?
- [Affects R19][Technical] How does the HTML feedback form submit data back to the local filesystem — options include a local server sidecar, a copy-to-clipboard CLI command, or a companion `sarthi-test feedback` command. Which mechanism fits the Sarthi ecosystem best?
- [Affects R20][Technical] How is "same flow" defined for cross-run comparison — by URL path, by DOM element, by persona-reported flow label, or by semantic similarity of the finding text?
