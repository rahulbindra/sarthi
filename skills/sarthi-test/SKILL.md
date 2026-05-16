---
name: sarthi-test
description: "Persona-based automated app testing. Spawns one browser sub-agent per persona to test a locally-started app against the latest GitHub commit, writes an HTML report with optional feedback fields, and maintains per-persona memory files that accumulate observations over runs. Use when you want to run persona tests, test your app as specific users, or get qualitative UX feedback on recent commits."
argument-hint: "[optional: feedback --persona <name> --note '...' | setup]"
---

# Sarthi Test — Persona-Based Automated App Testing

Runs one browser sub-agent per persona against your locally-started app, scoped to the latest GitHub commit. Each persona navigates the app as a real user would, reports findings in an HTML report with optional feedback fields, and builds a persistent memory file of observations over time.

---

## Step 0 — Sub-command routing

Check the arguments passed to this skill.

**If arguments include `feedback`:**

Parse `--persona <name>` and `--note <text>` from the arguments.

If `--note` is missing or empty, print:
```
Usage: sarthi test feedback --persona <name> --note "your observation here"
```
Then exit without writing anything.

If both are present:
- Determine the target project by reading `.sarthi/tester.yml` in the current directory (or prompt: "Run this from your project root where .sarthi/tester.yml lives.")
- Construct the path: `.sarthi/persona-memory/<name>.md`
- If the file does not exist, create it with a header: `# Persona Memory: <name>\n\n`
- Append the following line:
  ```
  [developer-feedback] <ISO-8601-timestamp>: <note text>
  ```
- Confirm: "Feedback recorded for <name>. It will be included in the next test run."
- Exit.

**If arguments include `setup`:**

Read `.sarthi/tester.yml` to get `cron_interval` (default: `*/30 * * * *`). Get the absolute path of the current working directory as `PROJECT_PATH`. Derive `PROJECT_SLUG` by taking the last component of `PROJECT_PATH` and replacing non-alphanumeric characters with hyphens.

Generate a macOS launchd plist at:
`~/Library/LaunchAgents/com.sarthi.test.<project-slug>.plist`

Plist content (use the actual values for PROJECT_SLUG, PROJECT_PATH, and interval in seconds — convert cron interval to seconds, default 30min = 1800):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.sarthi.test.PROJECT_SLUG</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/claude</string>
    <string>-p</string>
    <string>sarthi test</string>
    <string>--cwd</string>
    <string>PROJECT_PATH</string>
  </array>
  <key>StartInterval</key>
  <integer>1800</integer>
  <key>RunAtLoad</key>
  <false/>
  <key>StandardOutPath</key>
  <string>PROJECT_PATH/.sarthi/sarthi-test.log</string>
  <key>StandardErrorPath</key>
  <string>PROJECT_PATH/.sarthi/sarthi-test.log</string>
</dict>
</plist>
```

If the plist already exists, do not overwrite it — just print the load command.

Print:
```
Plist written to ~/Library/LaunchAgents/com.sarthi.test.<project-slug>.plist

To activate:
  launchctl load ~/Library/LaunchAgents/com.sarthi.test.<project-slug>.plist

To deactivate:
  launchctl unload ~/Library/LaunchAgents/com.sarthi.test.<project-slug>.plist

The skill will run every 30 minutes and check for new commits. Logs go to .sarthi/sarthi-test.log
```

Exit.

**If no sub-command arguments (or arguments are empty):** proceed to Step 1 for a normal test run.

---

## Step 1 — State management and commit detection

**Load state:**
```bash
python3 -c "
import json, os
path = os.path.expanduser('~/.claude/.sarthi-test-state.json')
try:
    print(open(path).read())
except:
    print(json.dumps({'last_tested_sha': None, 'last_full_crawl_sha': None, 'last_run_findings': {}}))
"
```

**Read config:**

Check that `.sarthi/tester.yml` exists in the current directory. If not, print:
```
sarthi-test: no .sarthi/tester.yml found.

Create one with at minimum:
  repo: owner/repo-name
  branch: main
  start_command: npm run dev
  start_url: http://localhost:3000

Run 'sarthi test setup' to register the launchd cron trigger.
```
Then exit.

Parse the config. Required fields: `repo`, `branch`, `start_command`, `start_url`. Optional with defaults: `readiness_timeout_seconds: 30`, `persona_cap: 3`, `diff_files_threshold: 10`, `diff_lines_threshold: 200`.

**Fetch latest commit SHA:**
```bash
gh api repos/<repo>/commits/<branch> --jq '.sha'
```

If `gh` returns an error (auth, not found, rate limit), print the error message and exit cleanly — do not start the app.

**Compare to last-tested SHA:**

If the fetched SHA equals `state.last_tested_sha`, print nothing and exit silently. Log to `~/.claude/.sarthi-test-log.jsonl`:
```json
{"ts": "<ISO-8601>", "sha": "<sha>", "skipped": "no_new_commits"}
```

**Compute diff stats:**
```bash
gh api repos/<repo>/compare/<last_tested_sha>...<latest_sha> --jq '{files: (.files | length), additions: .ahead_by, lines: ([.files[].additions, .files[].deletions] | flatten | add // 0), changed_files: [.files[].filename]}'
```

If `last_tested_sha` is null (first ever run), treat as a full crawl scenario — set `diff_files = 999`, `diff_lines = 999`, `changed_files = []`.

If `files_changed == 0` (empty diff), exit silently and log:
```json
{"ts": "<ISO-8601>", "sha": "<sha>", "skipped": "empty_diff"}
```

Store in working context: `latest_sha`, `diff_files`, `diff_lines`, `changed_files`.

---

## Step 2 — Crawl mode decision

**Check time since last full crawl:**
```bash
python3 -c "
import os, time
ts_path = os.path.expanduser('~/.claude/.sarthi-test-ts')
if os.path.exists(ts_path):
    days = (time.time() - os.path.getmtime(ts_path)) / 86400
    print(f'{days:.2f}')
else:
    print('999')
"
```

**Apply dual-gate logic:**

Full crawl condition: `days_elapsed >= 3 AND (diff_files >= diff_files_threshold OR diff_lines >= diff_lines_threshold)`

- If BOTH conditions are true → `crawl_mode = "full"`
- If either condition is false → `crawl_mode = "diff"`

First-run case (days_elapsed = 999): time condition is satisfied. If diff is large → full crawl. If diff is small (first run with a tiny initial commit) → diff-scoped, which will still test the start URL and available flows.

Store `crawl_mode` in working context. Note: `diff_summary` for agent briefs = `{crawl_mode, diff_files, diff_lines, changed_files}`.

Log crawl mode decision for the run.

---

## Step 3 — Persona resolution and memory load

**Check for declared personas:**

If `.sarthi/personas.yml` exists and is non-empty, parse it. Expected YAML format:
```yaml
personas:
  - name: sarah
    role: First-time user
    goals:
      - Understand what the product does
      - Complete onboarding without help
    pain_points:
      - Gets confused by jargon
      - Abandons if too many steps

  - name: alex
    role: Power user / returning customer
    goals:
      - Get to their primary workflow fast
      - Use advanced features
    pain_points:
      - Impatient with tutorials they've already seen
```

If `.sarthi/personas.yml` does not exist or is empty, **infer personas from the codebase:**

Scan in this priority order and synthesize 2–3 representative personas:
1. User model role enumerations (e.g., `role: admin | member | guest` in models/user files)
2. Onboarding copy files (e.g., `onboarding.md`, welcome email templates, step-by-step guides)
3. Seed data user fixtures (e.g., `db/seeds.rb`, `fixtures/users.yml`, `prisma/seed.ts`)
4. README persona sections (e.g., "For developers...", "For end users...")

Mark each inferred persona with `inferred: true`. The HTML report and agent brief will note they were inferred.

**Apply persona cap** (default 3): if more personas are defined than the cap, use the first N from the file. Log any skipped personas.

**Load persona memory files:**

For each persona, check `.sarthi/persona-memory/<name>.md`. If the file exists, read its full contents into `persona.memory`. If it does not exist, set `persona.memory = null` (first-run bootstrap — agent receives profile only).

Store `personas` list in working context.

---

## Step 4 — App lifecycle: start and readiness check

**Start the app:**

Run the configured `start_command` as a background process using the Bash tool with `run_in_background: true`.

Immediately after the process starts, capture its PID and write it to a temp file:
```bash
echo $! > ~/.claude/.sarthi-test-app.pid
```

(Instruct Claude: "After launching the background process, run this echo command as the very next Bash call to capture the PID before any other work proceeds.")

**Poll for readiness:**

Every 2 seconds, attempt an HTTP GET to `start_url`. Any HTTP response (including 4xx) means the app is serving. Use:
```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 <start_url> 2>/dev/null || echo "0"
```

Continue polling up to `readiness_timeout_seconds` (default 30). If any call returns a non-"0" response code → app is ready.

If timeout is reached with no response:
- Read PID from `~/.claude/.sarthi-test-app.pid` and kill the process
- Log: `{"ts": "<ISO>", "sha": "<sha>", "status": "app_start_timeout"}`
- Print: "sarthi-test: app did not respond at <start_url> within <timeout>s. Check start_command and start_url in .sarthi/tester.yml."
- Exit.

If `start_command` fails immediately (process exits with non-zero before first poll), detect this and log `status: "app_start_failed"`, then exit.

Store `app_pid_file = ~/.claude/.sarthi-test-app.pid` in working context. The app shutdown in Step 6 reads this file.

---

## Step 5 — Persona sub-agent dispatch

Launch one sub-agent per persona **in parallel**. Each sub-agent uses an independent browser session (agent-browser substrate) for full state isolation — no shared cookies or localStorage between personas.

For each persona, build this brief:

---
**Persona brief template:**

You are testing a web application as the following persona.

**Persona profile:**
- Name: <name>
- Role: <role>
- Goals: <goals as bullet list>
- Pain points: <pain_points as bullet list>
[If inferred: "Note: This persona was inferred from the codebase, not declared in .sarthi/personas.yml. Declare it explicitly to override this inference."]

**Prior observations and developer feedback** (from memory file — include if persona.memory is non-null):
<full contents of .sarthi/persona-memory/<name>.md>

**Test scope:**
- Crawl mode: <crawl_mode>
- [If diff-scoped]: Focus your testing on flows that touch these changed files: <changed_files list>
- [If full crawl]: Explore all reachable screens from the start URL.
- Start URL: <start_url>

**Your task:**
Navigate the app as this persona using your browser. Act as this person would genuinely act — follow your goals, get confused where they would get confused, succeed where they would succeed. Do not test everything; focus on what matters to this persona.

For diff-scoped runs, start at the start URL and navigate to flows that are likely affected by the changed files. For full crawls, explore all reachable screens from the start URL.

At each key interaction point (page load, form submit, CTA click, error state, success state), note your experience. Capture a screenshot at each key moment.

When you're done, return your findings as a JSON object matching this contract exactly:

```json
{
  "persona_name": "<name>",
  "inferred": <true|false>,
  "flows_tested": ["<flow label>", ...],
  "findings": [
    {
      "flow": "<flow label>",
      "sentiment": "positive|neutral|negative",
      "observation": "<what you experienced as this persona>",
      "screenshot_ref": "<screenshot filename or null>"
    }
  ],
  "overall_assessment": "<1-3 sentence summary of the experience as this persona>",
  "errored": false,
  "error_reason": null
}
```

If you cannot complete the test due to a browser error or unrecoverable issue, return:
```json
{
  "persona_name": "<name>",
  "inferred": <true|false>,
  "flows_tested": [],
  "findings": [],
  "overall_assessment": "",
  "errored": true,
  "error_reason": "<brief description of what went wrong>"
}
```
---

Dispatch all persona agents in parallel. Collect all results before proceeding to Step 6.

**Sequential fallback:** If parallel dispatch fails (harness rejects concurrent sub-agents), run persona agents one at a time. Between each persona, reset browser state:
1. Navigate to `about:blank`
2. Run via browser JavaScript: `localStorage.clear(); sessionStorage.clear();`
3. Clear cookies: `document.cookie.split(';').forEach(c => { document.cookie = c.replace(/^ +/, '').replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/'); });`
4. Navigate to `start_url` for the next persona.

**Failure handling:** If a persona agent returns `errored: true`, include its section in the report as errored and continue. Do not abort remaining agents.

Store all results in working context as `persona_results`.

---

## Step 6 — HTML report generation and app shutdown

**Shut down the app first:**
```bash
PID=$(cat ~/.claude/.sarthi-test-app.pid 2>/dev/null)
if [ -n "$PID" ]; then kill "$PID" 2>/dev/null; fi
rm -f ~/.claude/.sarthi-test-app.pid
```

**Create output directory:**
```bash
mkdir -p docs/persona-tests
```

**Generate the HTML report:**

Write a self-contained HTML file to `docs/persona-tests/<latest_sha>.html`. All CSS must be inline — no external dependencies so the file renders correctly when opened as a local file.

Report structure:

```
Header:
  - Title: "Persona Test Report"
  - Commit: <latest_sha> (linked to https://github.com/<repo>/commit/<sha>)
  - Branch: <branch>
  - Timestamp: <ISO-8601>
  - Crawl mode: <crawl_mode> ("diff-scoped" or "full crawl")
  - Personas tested: <count>

For each persona (one <section class="persona"> per persona):
  - Heading: <name> — <role>
  - [inferred badge if applicable]: "inferred from codebase"
  - Overall assessment paragraph
  - Findings list: for each finding:
      - Flow label
      - Sentiment indicator (✓ positive / · neutral / ✗ negative)
      - Observation text
      - Screenshot if captured
  - [If errored]: "⚠ Agent did not complete — <error_reason>"
  - Feedback block:
      <div class="feedback">
        <label>Optional developer feedback for <name>:</label>
        <textarea placeholder="What should <name> do differently? What did they miss?"></textarea>
        <p>To record your feedback, run this command in your terminal:</p>
        <pre>sarthi test feedback --persona <name> --note "YOUR NOTE HERE"</pre>
      </div>

Footer:
  - "Generated by sarthi-test · <timestamp>"
```

Use clean inline CSS: white background, readable font (system-ui), section cards with subtle border, sentiment color coding (green for positive, gray for neutral, red for negative), feedback block with a light background to distinguish it from findings.

Write the completed HTML to `docs/persona-tests/<latest_sha>.html` using the Write tool.

Print: "Report written to docs/persona-tests/<latest_sha>.html"

---

## Step 7 — State update and run logging

**Update state:**

```bash
python3 -c "
import json, os
from datetime import datetime, timezone

state_path = os.path.expanduser('~/.claude/.sarthi-test-state.json')
try:
    state = json.load(open(state_path))
except:
    state = {'last_tested_sha': None, 'last_full_crawl_sha': None, 'last_run_findings': {}}

# Update from this run — substitute actual values
state['last_tested_sha'] = 'LATEST_SHA'

# Update per-persona flow negative counts from this run's findings
# PERSONA_FLOW_COUNTS = {'sarah': {'onboarding': 1, 'checkout': 0}, ...}
for persona_name, flow_counts in PERSONA_FLOW_COUNTS.items():
    state['last_run_findings'][persona_name] = flow_counts

json.dump(state, open(state_path, 'w'), indent=2)
print('state updated')
"
```

Compute `PERSONA_FLOW_COUNTS` from `persona_results`: for each non-errored persona agent, count how many findings per flow had `sentiment == "negative"`.

**Touch full-crawl timestamp** (only if this was a full crawl):
```bash
# Only run if crawl_mode == "full"
touch ~/.claude/.sarthi-test-ts
```

Also update `state.last_full_crawl_sha = latest_sha` in the state when crawl_mode is full.

**Append JSONL log entry:**
```bash
python3 -c "
import json, os
from datetime import datetime, timezone
entry = {
    'ts': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'sha': 'LATEST_SHA',
    'crawl_mode': 'CRAWL_MODE',
    'personas_tested': PERSONAS_TESTED_COUNT,
    'personas_errored': PERSONAS_ERRORED_COUNT,
    'report_path': 'docs/persona-tests/LATEST_SHA.html'
}
path = os.path.expanduser('~/.claude/.sarthi-test-log.jsonl')
with open(path, 'a') as f:
    f.write(json.dumps(entry) + '\n')
" 2>/dev/null || true
```

Substitute actual values for `LATEST_SHA`, `CRAWL_MODE`, counts.

**Cleanup:**
```bash
rm -f ~/.claude/.sarthi-test-app.pid
```

**Print completion summary:**
```
sarthi-test complete
  Commit:  <short-sha>
  Mode:    <crawl_mode>
  Personas: <count> tested, <errored> errored
  Report:  docs/persona-tests/<sha>.html
```

---

## Configuration reference

`.sarthi/tester.yml` schema:
```yaml
repo: owner/repo-name          # GitHub repo (required)
branch: main                   # Branch to watch (required)
start_command: npm run dev     # Shell command to start the app (required)
start_url: http://localhost:3000  # URL to poll for readiness (required)
readiness_timeout_seconds: 30  # How long to wait for app to start (default: 30)
persona_cap: 3                 # Max concurrent persona agents (default: 3)
diff_files_threshold: 10       # Files-changed threshold for full crawl (default: 10)
diff_lines_threshold: 200      # Lines-changed threshold for full crawl (default: 200)
cron_interval: "*/30 * * * *"  # Cron expression for launchd interval (default: every 30min)
```

`.sarthi/personas.yml` schema:
```yaml
personas:
  - name: <slug>              # Lowercase, used as memory file name (required)
    role: <role title>        # Human-readable role description (required)
    goals:                    # List of what this persona wants to achieve (required)
      - <goal>
    pain_points:              # List of friction points this persona has (required)
      - <pain point>
```

---

## Self-learning: persona memory files

Each persona has a persistent memory file at `.sarthi/persona-memory/<name>.md`.

This file accumulates context across runs:
- `[developer-feedback] <timestamp>: <note>` — written by `sarthi test feedback` sub-command
- `[system-observed] <timestamp>: <observation>` — written by sarthi-test (v2, not yet active)
- `[system-resolved] <timestamp>: <note>` — written by sarthi-test (v2, not yet active)

The file is included verbatim in each persona sub-agent's brief, compounding context from past runs.

Memory files are **append-only** — the skill never removes or overwrites entries. Deletion is always a developer action (direct edit to the file).

If you want to correct or override an observation, add a new `[developer-feedback]` entry — the agent will read all entries and weigh the most recent ones more heavily.
