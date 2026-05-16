---
name: researcher
description: Autonomous research agent — accepts a research brief, fetches and scores sources across web/YouTube/PDF/OCR/structured data, ingests survivors into a wiki vault, and produces a post-run report. Callable from Sarthi, Cowork, or directly.
argument-hint: '"<brief>" [--vault <path>] [--threshold 6] [--cap 5] [--budget 20] [--timeout 15] [--every <cron>]'
triggers: ["research this", "researcher agent", "run researcher", "researcher brief", "autonomous research", "research for me"]
---

# Researcher Agent

*Autonomous multi-source research loop: brief in, wiki pages out, report ready to interrogate.*

One command replaces the full manual cycle of finding → saving → ingesting → querying. The agent searches across web, YouTube, PDF, scanned docs, and structured data — scores each source against your brief — ingests survivors into a wiki vault — and produces a post-run report you can question in-session.

---

## Prerequisites

Check before running:

```bash
python3 -c "import youtube_transcript_api" 2>/dev/null && echo "yt-api:yes" || echo "yt-api:no"
command -v firecrawl > /dev/null && echo "firecrawl:yes" || echo "firecrawl:no"
```

| Dependency | Install | Used for |
|------------|---------|----------|
| `youtube-transcript-api` | `pip install youtube-transcript-api` | YouTube transcript extraction (primary) |
| `firecrawl` | already installed via plugin | Web search + scrape + PDF parsing |

If `youtube-transcript-api` is missing: narrate "youtube-transcript-api not found — YouTube sources will fall back to firecrawl scrape or manual raw/ drop" and continue. Non-blocking.

---

## Invocation

```
researcher "<brief>" [--vault <path>] [--threshold 6] [--cap 5] [--budget 20] [--timeout 15]
researcher stop <agent_id>
```

| Argument | Default | Meaning |
|----------|---------|---------|
| `<brief>` | required | Topic, question, or seed URLs to research |
| `--vault` | auto-detect | Path to target wiki vault |
| `--threshold` | 6.0 | Minimum relevance score (1–10) to keep a source |
| `--cap` | 5 | Maximum sources to ingest per run |
| `--budget` | 20 | Maximum sources to check before stopping |
| `--timeout` | 15 | Hard timeout in minutes |
| `--every` | — | Cron expression or shorthand (e.g. `daily`, `"0 9 * * 1"`) for recurring runs |

---

## Phase 1: Brief Intake and Session Init (U1)

### 1.1 Parse arguments

Extract `brief`, `vault`, `threshold`, `cap`, `budget`, `timeout` from the invocation. If brief is ambiguous (fewer than 4 words and no URLs), ask one clarifying question before proceeding:

> "What specific aspect of [topic] do you want to research? Any particular angle or question?"

### 1.2 Resolve vault target

```bash
ls ~/wikis/ 2>/dev/null && echo "wikis:exist" || echo "wikis:none"
```

- `--vault` explicitly given → use it
- No `--vault` + one vault exists at `~/wikis/` → use it, confirm with narration: "Targeting vault: ~/wikis/<name>"
- No `--vault` + multiple vaults → ask which one:
  > "Which vault should this research go into? [list vault names]"
- No `--vault` + no vaults → infer a domain slug from the brief (e.g. "transformer architectures" → `transformer-architectures`), create the vault inline:
  ```bash
  mkdir -p ~/wikis/<domain-slug>/raw ~/wikis/<domain-slug>/wiki
  touch ~/wikis/<domain-slug>/wiki/index.md ~/wikis/<domain-slug>/wiki/log.md
  ```
  Write `~/wikis/<domain-slug>/CLAUDE.md` using the sarthi-wiki template. Narrate: "No vault found — created ~/wikis/<domain-slug>/ for this research." Then continue with that vault as the target.

### 1.3 Generate session ID and init status object

```bash
AGENT_ID="res-$(date +%s)"
echo $AGENT_ID
```

Initialize and write the status object to `~/.researcher-status-<agent_id>.json`:

```json
{
  "agent_id": "<agent_id>",
  "brief": "<brief>",
  "status": "running",
  "sources_checked": 0,
  "sources_kept": 0,
  "sources_discarded": 0,
  "elapsed_time": 0,
  "current_action": "initializing",
  "vault_target": "<vault_path>"
}
```

Write this JSON via:
```bash
cat > ~/.researcher-status-<agent_id>.json << 'EOF'
{ ... }
EOF
```

### 1.4 Announce and begin

Narrate:
```
Researcher agent started — <agent_id>
Brief: "<brief>"
Vault: <vault_path>
Settings: threshold=<N> | cap=<N> | budget=<N> | timeout=<N>min

Checking prerequisites...
[narrate yt-api and firecrawl status]

Starting source discovery...
```

Record start time (capture current Unix timestamp for elapsed-time calculations throughout the run).

---

## Phase 2: Source Fetching (U2)

For each source, narrate one line before fetching: `Fetching [N/budget]: <title or URL>...`

### 2.1 Web search (topic brief)

If brief does not contain seed URLs:
1. Run `firecrawl-search "<brief>" --limit 10` to get candidate URLs
2. Narrate: "Found N candidate URLs via web search"
3. Queue all for scraping

### 2.2 Seed URLs (URL brief)

If brief contains one or more URLs:
1. Skip web search entirely
2. Scrape each URL directly: `firecrawl-scrape <url>`
3. Narrate: "Scraping seed URL: <url>"

### 2.3 Web scrape

For each candidate URL:
```
firecrawl-scrape <url>
```
Extract: title, full text content, URL. On scrape failure: narrate "Scrape failed for <url> — skipping" and continue.

### 2.4 YouTube

For a YouTube URL:

**Step 1 — youtube-transcript-api (primary):**
```bash
# Extract video ID
VIDEO_ID=$(echo "<url>" | grep -oP '(?<=v=)[^&]+|(?<=youtu.be/)[^?]+')
python3 -m youtube_transcript_api $VIDEO_ID --languages en 2>/dev/null
```
If successful: narrate "Fetched transcript via youtube-transcript-api: [video title if known]"

**Step 2 — firecrawl scrape fallback:**
If `youtube-transcript-api` fails or is not installed:
```bash
firecrawl-scrape <youtube_url>
```
Narrate: "youtube-transcript-api unavailable — trying firecrawl scrape"

**Step 3 — manual fallback:**
If both fail: narrate:
```
Could not auto-extract transcript for <url>.
To include this source: drop the transcript file into <vault>/raw/<video-id>.txt
then run: wiki ingest
```
Skip this source and continue.

### 2.5 Digital PDF

- **Local file path ending in `.pdf`**: Read it directly (Claude native PDF support)
- **PDF URL**: `firecrawl-scrape <pdf_url>` — firecrawl extracts PDF text content
- **Local file, firecrawl available**: `firecrawl parse <local_path>` as fallback
- On failure: narrate "Could not extract PDF content from <source> — skipping"

### 2.6 Scanned / image-heavy documents

```bash
cat ~/.researcher-config.json 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('ocr_service','none'))" 2>/dev/null || echo "none"
```

- If OCR service configured: pass document to service, await text
- If not configured: narrate "OCR service not configured — skipping scanned document. Add `ocr_service` to `~/.researcher-config.json` to enable." Skip this source.

**`~/.researcher-config.json` schema:**
```json
{
  "ocr_service": "textract | google-vision | none",
  "ocr_api_key": "optional"
}
```

### 2.7 Structured data (CSV / spreadsheet)

- **CSV**: Read as plain text — treat rows as content to summarize
- **XLSX local**: `firecrawl parse <file>` if available; else skip with narration
- **Financial tables in web pages**: captured naturally by firecrawl scrape (no special handling needed)

---

## Phase 3: Relevance Scoring and Quality Controls (U3)

After fetching each source, score it before deciding to keep or discard.

### 3.1 Scoring protocol

Read the first ~800 words (or full content if shorter). Score 1–10 against the brief:

| Score | Meaning |
|-------|---------|
| 9–10 | Directly addresses the brief with new, specific information |
| 7–8 | Substantially relevant, covers key aspects |
| 5–6 | Partially relevant, some useful content |
| 3–4 | Tangentially related, mostly off-topic |
| 1–2 | Not relevant to the brief |

Narrate score result: `Scored 7.4 — keeping` or `Below threshold (4.1) — discarding`

### 3.2 Quality controls (evaluated in this order)

**Control 1 — Source budget:**
```
if sources_checked >= budget:
  narrate "Source budget reached (N sources checked) — wrapping up"
  → proceed to Phase 5 (ingest)
```

**Control 2 — Relevance threshold:**
```
if score < threshold:
  discard source
  increment sources_discarded
  update status JSON
  continue loop
```

**Control 3 — Quantity cap:**
```
if sources_kept >= cap:
  narrate "Quantity cap reached (N sources ingested) — stopping collection"
  → proceed to Phase 5 (ingest)
```

**Control 4 — Keep:**
```
keep source
increment sources_kept
queue for ingest
```

### 3.3 Status update

After each source (kept or discarded), update `~/.researcher-status-<agent_id>.json`:
```json
{
  "sources_checked": <n>,
  "sources_kept": <n>,
  "sources_discarded": <n>,
  "elapsed_time": <seconds since start>,
  "current_action": "scored: <title> (<score>)"
}
```

Use Write tool to overwrite the status file on each update.

---

## Phase 4: Runtime Guards (U4)

These checks run **before each fetch operation**. They never interrupt mid-fetch — they gate the start of the next operation.

### 4.1 Hard timeout check

Before each fetch:
```
elapsed = current_unix_time - start_unix_time
if elapsed > timeout_minutes * 60:
  narrate "Hard timeout reached (<N>min elapsed) — wrapping up"
  update status: "status": "timed-out"
  → proceed to Phase 5 (ingest) then Phase 6 (report)
```

### 4.2 Manual stop check

Before each fetch:
```bash
[ -f ~/.researcher-stop-<agent_id> ] && echo "stop:requested" || echo "stop:none"
```

If stop file exists:
- Narrate: "Stop signal received — completing current operation then stopping"
- Finish the current in-flight operation (do not abort mid-fetch)
- Update status: `"status": "stopped"`
- Remove the stop flag file
- → Proceed to Phase 5 (ingest) then Phase 6 (report)

### 4.3 Watchdog (stall detection)

Track a `consecutive_stalls` counter (starts at 0).

Before each fetch operation, note the start timestamp. After the operation completes:
- If elapsed for that single operation > 30s and no content was returned: increment `consecutive_stalls`, narrate "Fetch appears stalled — retrying once", retry the operation
- If retry also returns no content in 30s: narrate "Operation stuck — moving to next source", skip source, continue
- If `consecutive_stalls >= 3`: narrate "Too many consecutive stalls — stopping run", update status: `"status": "stuck"`, → proceed to Phase 5 then Phase 6

Reset `consecutive_stalls` to 0 whenever a fetch succeeds.

### 4.4 `researcher stop` command

When the user runs `researcher stop <agent_id>`:
```bash
touch ~/.researcher-stop-<agent_id>
echo "Stop signal sent to agent <agent_id>. Agent will finish its current operation then stop."
```

---

## Phase 5: Wiki Ingest (U5)

For each source in the kept list, create a wiki page matching sarthi-wiki format exactly.

### 5.1 Deduplication (recurring mode)

Before fetching any source, check:
```bash
SEEN_FILE="<vault>/.researcher-seen-urls.txt"
grep -qF "<url>" "$SEEN_FILE" 2>/dev/null && echo "seen" || echo "new"
```

If `seen`: narrate "Already in wiki — skipping <url>" and skip.

After successful ingest of a source, append its URL:
```bash
echo "<url>" >> "<vault>/.researcher-seen-urls.txt"
```

### 5.2 Page creation

For each kept source, create `<vault>/wiki/<slug>.md`:

```markdown
---
tags: [<inferred tags from content and brief>]
source: <url or file path>
updated: <YYYY-MM-DD>
---

# <Title>

<2–4 sentence summary of the source>

## Detail

<main content, condensed and organized>

## Related

- [[<existing wiki page>]] — <relationship to this source>
```

**Slug naming:**
- Source pages: `src-<kebab-title>.md`
- Concept pages extracted from source: `<kebab-concept>.md`

**Cross-linking:** Before creating the page, read `<vault>/wiki/index.md` to find related existing pages. Add `## Related` backlinks for any semantic matches.

### 5.3 Index update

Append to `<vault>/wiki/index.md`:
- Under `## Sources`: `- [[src-<slug>]] — <one-line description> (researcher, <date>)`
- Under relevant concept sections: link any new concept pages created
- Update the page count in the index header: `*Pages: N | Sources: M*`

If `index.md` doesn't exist: create it with the standard structure before updating.

### 5.4 Log update

Append one line to `<vault>/wiki/log.md`:
```
[<YYYY-MM-DD>] Researcher agent (res-<agent_id>) ingested: "<brief>" → <N> pages created
```

---

## Phase 6: Post-Run Report (U6)

After every run — complete, stopped, or timed-out — produce this report:

```
Research run complete — res-<agent_id>
Brief: "<brief>"
Vault: <vault_path>
Duration: Xm Ys  |  Status: <complete|stopped|timed-out|stuck>

Sources:
  Checked: N  |  Kept: M  |  Discarded: K

Kept (scored ≥ <threshold>):
  8.2 — [Title] (<url>)
  6.7 — [Title] (<url>)

Discarded:
  3.1 — [Title] — below threshold
  (and N more below threshold)

Key themes across ingested sources:
  - <theme 1>
  - <theme 2>

You can ask follow-up questions now:
  "What did you find about X?"
  "Which source scored highest?"
  "Did you find anything about Y?"

Ingest this report as an analysis page? [y/n]

Task cost estimate: ~<N>k tokens (~$<X>)
```

**Edge cases:**
- 0 sources kept → report states "No sources passed the relevance threshold (scores ranged N–M). Try lowering --threshold or broadening the brief."
- stopped run → stop reason in status line: `Status: stopped (manual)`
- timed-out → `Status: timed-out after Nmin`
- stuck → `Status: stuck (3 consecutive stalls)`

### 6.1 Ingestable report

If user says yes to "Ingest this report as an analysis page?":
- Create `<vault>/wiki/analysis-researcher-<agent_id>.md` with the full report as content
- Append under `## Analysis` in index.md: `- [[analysis-researcher-<agent_id>]] — Research run: "<brief>" (<date>)`
- Narrate: "Report saved as analysis page."

### 6.2 Follow-up questions

After the report, stay in session. The kept sources are in context from Phase 3 scoring. Answer follow-up questions directly without re-fetching. If a question falls outside what was fetched: "That topic wasn't covered in this run. Want me to run a follow-up researcher brief on it?"

---

## Phase 7: Execution Modes (U7)

### 7.1 One-shot (default)

Run Phases 1–6 once and exit. This is the base behavior.

### 7.2 Recurring mode

If `--every` is provided:

Parse the schedule:
- `--every daily` → cron `0 9 * * *`
- `--every weekly` → cron `0 9 * * 1`
- `--every "0 9 * * 1"` → use as-is

Create a scheduled task via `mcp__scheduled-tasks__create_scheduled_task` with:
- The full researcher invocation as the prompt (use skill name, not embedded logic)
- Schedule set to the cron expression

Narrate:
```
Recurring research scheduled — res-<agent_id>
Schedule: <cron expression> (<human-readable>)
Deduplication active: <vault>/.researcher-seen-urls.txt will prevent re-ingesting known sources.
To stop recurring runs: delete the scheduled task or run `researcher stop --recurring <agent_id>`
```

### 7.3 Parallel mode (Cowork)

Each parallel research direction is a separate researcher invocation with its own brief and vault target:
- Status objects land at separate `~/.researcher-status-<agent_id>.json` paths — no shared state
- Each run operates independently; they never interfere

To run two directions simultaneously in Cowork: open two Cowork cards and invoke `researcher` in each. The agent IDs will be different timestamps and their outputs will be completely isolated.

---

## Stop Command Reference

| Command | Effect |
|---------|--------|
| `researcher stop <agent_id>` | Creates `~/.researcher-stop-<agent_id>` — agent finishes current operation then stops |
| `researcher stop --recurring <agent_id>` | Cancels the associated scheduled task (if one exists) |

---

## Self-Learning Design

This agent is designed to compound over runs:

- **Dedup list** (`<vault>/.researcher-seen-urls.txt`) grows with each recurring run — over time the agent focuses only on new sources
- **Wiki cross-links**: each new page references related existing pages — the wiki builds a richer semantic graph over time
- **Log**: `wiki/log.md` records every researcher run — provides history for auditing and understanding what's been covered
- **Analysis pages**: researcher reports ingested as analysis pages serve as indexed run histories

---

## Status Object Schema

Written to `~/.researcher-status-<agent_id>.json` after each operation. Parseable by Cowork and future control center UI.

```json
{
  "agent_id": "res-1747384200",
  "brief": "LLM context window techniques",
  "status": "running | complete | stopped | timed-out | stuck",
  "sources_checked": 12,
  "sources_kept": 4,
  "sources_discarded": 8,
  "elapsed_time": 143,
  "current_action": "scoring: 'Efficient LLM inference...'",
  "vault_target": "~/wikis/ai-research"
}
```

---

## Cost Guidance

| Operation | Approximate cost |
|-----------|-----------------|
| One-shot run (5 sources kept) | ~50–100k tokens |
| Source scoring (per source) | ~2–5k tokens |
| Wiki ingest (per page) | ~5–10k tokens |
| Post-run report | ~3–5k tokens |

For large briefs (budget 20, cap 5): expect ~150k tokens total. Run in a dedicated session.

---

## Example Interactions

**"researcher 'LLM context window techniques'"**
→ Searches web, finds 10 candidates, scores each, ingests 5 highest-scoring into ~/wikis/ai-research, produces report

**"researcher 'https://arxiv.org/abs/2501.12345' --vault ~/wikis/ml-papers"**
→ Ingests a specific paper directly (seed URL), scores against brief, ingests to ml-papers vault

**"researcher 'AI safety' --every daily"**
→ Runs once now, schedules daily repeats, deduplication prevents re-ingesting already-known sources

**"researcher stop res-1747384200"**
→ Signals the running agent to stop after its current operation

**"What did you find about attention mechanisms?"**
→ Follow-up answered from in-session context, no additional fetches
