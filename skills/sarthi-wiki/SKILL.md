---
name: sarthi-wiki
description: LLM Wiki agent — Karpathy-style personal knowledge base using Claude Code and markdown files. Turns raw documents (articles, transcripts, meeting notes, research) into a structured, queryable wiki with auto-maintained relationships and indexes. No vector DB or embeddings needed. Triggers on "build a wiki", "second brain", "llm wiki", "knowledge base", "ingest this", "add to my wiki", "query my wiki", "wiki lint", "sarthi wiki".
argument-hint: "[init <domain> | ingest | query <question> | lint | status | help]"
---

# Sarthi Wiki

*Karpathy-style LLM knowledge base: raw documents in, organized queryable wiki out. No vector DB. No embeddings. Just markdown.*

Based on [Andrej Karpathy's LLM wiki approach](https://x.com/karpathy) — give Claude Code a folder of raw documents, and it auto-organizes them into a structured wiki with cross-links, an index, and a log. One user cited 95% token reduction when querying vs. raw context. The wiki compounds over time.

**Private wikis stay local.** This skill creates vaults in user-chosen directories. Nothing in this skill references or commits personal project data to the Sarthi repository.

---

## Sub-commands

| Command | What it does |
|---------|-------------|
| `wiki init [domain]` | Set up a new wiki vault for a given domain |
| `wiki ingest` | Process files in raw/ into organized wiki pages |
| `wiki query <question>` | Answer a question using the wiki |
| `wiki lint` | Health check — find inconsistencies, gaps, impute missing data |
| `wiki status` | Show vault stats: page count, sources, last update |
| `wiki link <path>` | Point another project's CLAUDE.md at this wiki |

If no sub-command is given — detect context (Is there a raw/ with unprocessed files? Is there a wiki/? Is there a question?) and route to the most likely sub-command. Ask if ambiguous.

---

## Phase 0 — Detect context

```bash
# Check if we're inside a wiki vault already
[ -f "CLAUDE.md" ] && grep -q "LLM Wiki" CLAUDE.md 2>/dev/null && echo "vault:exists" || echo "vault:none"
[ -d "raw" ] && echo "raw:exists" || echo "raw:none"
[ -d "wiki" ] && echo "wiki:exists" || echo "wiki:none"
[ -d "raw" ] && ls raw/ | grep -v "^$" | wc -l | xargs echo "raw_files:"
[ -d "wiki" ] && ls wiki/*.md 2>/dev/null | wc -l | xargs echo "wiki_pages:"
```

Use the output to orient:
- `vault:none` + user said "init" → run **Init**
- `vault:exists` + files in raw/ → offer to **Ingest**
- `vault:exists` + user asked a question → run **Query**
- `vault:exists` + user said "lint" → run **Lint**
- Ambiguous → ask one question: "Set up a new wiki, ingest documents, or query an existing one?"

---

## Sub-command: `wiki init`

### Step 1 — Name and locate the vault

Ask:
> "What domain is this wiki for? (e.g., AI research, YouTube transcripts, business ops, personal second brain)"

Then ask:
> "Where should the vault live? Default: `~/wikis/<domain-slug>/`"

Use `AskUserQuestion` (load via `ToolSearch select:AskUserQuestion` first). Ask one question at a time.

### Step 2 — Create the directory structure

```bash
VAULT="<user_path>"
mkdir -p "$VAULT/raw"
mkdir -p "$VAULT/wiki"
touch "$VAULT/wiki/index.md"
touch "$VAULT/wiki/log.md"
```

### Step 3 — Write CLAUDE.md

Write `<vault>/CLAUDE.md` with this template (substitute domain name and path):

```markdown
# LLM Wiki — <domain>

## Purpose
<user-provided description of what this wiki is for>

## Vault location
<absolute path>

## Structure
- `raw/`         — source documents. Drop files here. Do not edit manually.
- `wiki/`        — organized knowledge pages. Auto-maintained by Claude Code.
- `wiki/index.md` — master index: all pages, tags, and relationships at a glance.
- `wiki/log.md`  — operation log: every ingest, lint, and update recorded.

## How to query (read this before answering any question about this wiki)
1. Read `wiki/index.md` first — it's the map.
2. Follow the links to the 2–4 most relevant pages. Read those.
3. Do NOT read raw/ unless the user explicitly asks for the original source.
4. Do NOT read every wiki page — that defeats the purpose. Index + targeted reads only.

## How to ingest a new document
1. User drops a file into `raw/`.
2. Read the file fully.
3. Identify: entities (people, orgs, products), concepts, events, claims.
4. Create or update one wiki page per entity/concept. Keep pages focused.
5. Add backlinks: every page references the source and related pages.
6. Update `wiki/index.md` — add new pages under the correct section.
7. Append one line to `wiki/log.md`: `[date] Ingested: <source> → <N> pages created/updated`

## Wiki page format
Every wiki page must have:
```
---
tags: [<tag1>, <tag2>]
source: <source file or URL>
updated: <YYYY-MM-DD>
---

# <Title>

<2–4 sentence summary>

## Detail
<main content>

## Related
- [[<page1>]] — <one line on the relationship>
- [[<page2>]] — <one line on the relationship>
```

## Index format
`wiki/index.md` sections (add only sections that apply):
- `## Sources` — one line per ingested document
- `## Concepts` — key ideas, frameworks, techniques
- `## People` — individuals mentioned
- `## Organizations` — companies, institutions
- `## Events` — dated occurrences
- `## Analysis` — cross-source insights, patterns, gaps
- `## Hot` — last ~500 words of most recent update (optional, saves a file read)

## Naming conventions
- Page files: `<kebab-case-title>.md`
- Source pages: prefix with `src-` (e.g., `src-ai-2027.md`)
- Concept pages: no prefix (e.g., `compute-scaling.md`)
- Analysis pages: prefix with `analysis-`

## Lint instructions (run periodically)
Check for:
- Pages with no backlinks (orphans)
- Index entries that point to missing files
- Duplicate concepts (same idea, different page names)
- Pages with vague or missing summaries
- Sources ingested but not yet linked to enough concept pages
For each issue: fix inline or flag with `<!-- LINT: <issue> -->` for human review.
```

### Step 4 — Write the initial index

```markdown
# Wiki Index — <domain>

*Last updated: <today>*
*Pages: 0 | Sources: 0*

---

## Sources
<!-- Ingested documents appear here -->

## Concepts
<!-- Key ideas, frameworks, techniques -->

## People
<!-- Individuals -->

## Organizations
<!-- Companies, institutions -->

## Analysis
<!-- Cross-source insights -->
```

### Step 5 — Confirm and orient

Tell the user:
```
Wiki vault created at: <path>

Next steps:
  1. Drop documents into <path>/raw/
  2. Run: wiki ingest
  3. Query with: wiki query <your question>

To use this wiki from another Claude Code project, run:
  wiki link <path>
```

---

## Sub-command: `wiki ingest`

### Step 1 — Find unprocessed files

```bash
# List files in raw/ and check which ones are already in the log
ls raw/ 2>/dev/null
grep -h "Ingested:" wiki/log.md 2>/dev/null | sed 's/.*Ingested: //' | cut -d'→' -f1 | sed 's/ *$//'
```

Cross-reference: files in `raw/` that don't appear in `wiki/log.md` are unprocessed.

If all files are already processed: "All files in raw/ have been ingested. Drop new files to ingest more."

If there are new files, confirm:
> "Found [N] new file(s) in raw/: [list]. Ingest all? [y] Yes  [s] Select which ones"

### Step 2 — For each file, ingest

For each file to ingest:

**2a. Read the file fully.**

**2b. Identify entities and concepts.** List them before creating pages:
- Entities: people, organizations, products, projects
- Concepts: frameworks, techniques, ideas, claims
- Events: dated occurrences

**2c. Estimate page count.** A 5,000-word article typically yields 10–20 wiki pages. Tell the user: "This source will generate approximately N pages."

**2d. Create the source page.**
File: `wiki/src-<slug>.md`
Include: tags, source path, date, key takeaways, all concepts and entities found (as backlinks).

**2e. Create or update one page per entity/concept.**
- If a page for this entity/concept already exists: read it, add new information, update backlinks, bump the `updated` date.
- If new: create with proper format from CLAUDE.md template.

**2f. Update `wiki/index.md`.**
- Add source under `## Sources`
- Add new concepts/entities under their sections
- Update page count in the header

**2g. Append to `wiki/log.md`.**
```
[<date>] Ingested: <filename> → <N> pages created, <M> pages updated
```

**2h. Ask follow-up questions** (per Karpathy's approach):
> "I've ingested [source]. A few questions that would help me make better connections:
> 1. What's the focus of this wiki — what should I emphasize from this source?
> 2. Any gaps I should know about — are there related topics you'd want me to watch for?"

These answers go into a `wiki/context.md` file (append-only). Claude reads this on every future ingest to keep emphasis consistent.

### Step 3 — Summary

After all files are ingested:
```
Ingest complete.
  Sources processed: N
  Pages created: X
  Pages updated: Y
  Wiki now has: Z total pages

Task cost estimate: ~[tokens]k tokens (~$[cost])
```

---

## Sub-command: `wiki query`

**Important: always use index-first reading. Never read every page.**

### Step 1 — Read the index

```bash
cat wiki/index.md
```

### Step 2 — Identify relevant pages

From the index, identify the 2–4 most relevant pages for the question. Name them explicitly before reading.

### Step 3 — Read only those pages

Read the identified pages. If a page's Related section points to another page that's clearly relevant, read that too — but cap at 6 total page reads.

### Step 4 — Answer

Answer the question directly, citing which wiki pages informed the answer. Format as:
```
[Answer]

Sources: [[page1]], [[page2]]
```

If the answer isn't in the wiki: say so explicitly. Offer to ingest a source that would fill the gap.

---

## Sub-command: `wiki lint`

Per Karpathy: *"run LLM health checks over the wiki to find inconsistent data, impute missing data with web searches, find interesting connections for new article candidates."*

### Step 1 — Read index and all wiki pages

```bash
cat wiki/index.md
ls wiki/*.md
```

Read all pages (this is the one case where reading all pages is correct — lint needs full coverage).

### Step 2 — Check for issues

| Check | What to look for |
|-------|-----------------|
| Orphans | Pages not linked from any other page and not in index |
| Broken links | Index entries pointing to files that don't exist |
| Duplicates | Two pages for the same concept (similar titles, overlapping content) |
| Thin pages | Pages with < 3 sentences of actual content |
| Missing summaries | Pages with no 2–4 sentence summary at the top |
| Stale sources | Source pages with no concept backlinks |
| Connection gaps | Two concepts that appear in the same sources but aren't linked to each other |

### Step 3 — Impute and fix

For each issue:
- **Fixable inline** (orphan, broken link, thin page): fix it. Log the fix.
- **Needs more data** (gap in knowledge): flag with `<!-- LINT: needs source on <topic> -->` and list it in the lint report.
- **Interesting connection found**: create an `analysis-<topic>.md` page, link both concepts to it.

### Step 4 — Report

```
Lint complete — <date>

Fixed:
  - [N] orphaned pages linked
  - [M] broken index entries repaired
  - [K] thin pages expanded

Flagged for human review:
  - <list of pages with LINT comments>

New connections found:
  - <list of new analysis pages created>

Suggested sources to fill gaps:
  - <topic>: suggest searching for <query>
```

Append a one-line summary to `wiki/log.md`:
```
[date] Lint run → N fixes, M flags, K new connections
```

---

## Sub-command: `wiki status`

```bash
echo "=== Wiki Status ==="
echo "Pages: $(ls wiki/*.md 2>/dev/null | wc -l)"
echo "Sources: $(grep -c "^-" wiki/index.md 2>/dev/null || echo 0)"
echo "Last update: $(tail -1 wiki/log.md 2>/dev/null || echo 'never')"
echo "Raw unprocessed: $(comm -23 <(ls raw/ | sort) <(grep 'Ingested:' wiki/log.md | sed 's/.*Ingested: //' | cut -d'→' -f1 | sed 's/ *$//' | sort) 2>/dev/null | wc -l)"
du -sh wiki/ 2>/dev/null | cut -f1 | xargs echo "Wiki size:"
```

Present as a clean summary.

---

## Sub-command: `wiki link`

Points another Claude Code project at this wiki via its CLAUDE.md, so Claude Code in that project can query the wiki without the user having to explain it.

### Step 1 — Identify the wiki path

Either from the argument (`wiki link <path>`) or from context (current vault).

### Step 2 — Identify the target project

Ask: "Which project should I link this wiki to? Provide the path to the project's CLAUDE.md."

### Step 3 — Append to target project's CLAUDE.md

Add this block:

```markdown
## External Wiki — <domain>

When you need information about <domain> that isn't in this codebase:
1. Navigate to `<vault_path>`
2. Read `wiki/index.md` first
3. Read only the 2–4 most relevant pages — never read all pages
4. Do NOT read raw/ — wiki/ only
5. Return to this project after querying

Trigger: user asks about <domain>, or a task requires context about <topic1>, <topic2>.
```

Confirm: "Wiki linked. Claude Code in [project] will now query [domain] wiki automatically when relevant."

---

## Self-learning design

This skill is designed to compound:

- **Append-only log**: `wiki/log.md` and `wiki/context.md` grow over time and are never overwritten. Claude reads them to understand the wiki's history and emphasis.
- **Lint accumulates patterns**: Each lint run may find the same recurring gap. After 2 consecutive lint runs flagging the same topic, the lint report surfaces it as a "persistent gap" — worth actively sourcing.
- **Context file builds focus**: Every answer to the post-ingest questions goes into `wiki/context.md`. Over time this becomes a precise description of what matters to the user in this domain.
- **Hot cache** (optional): `wiki/hot.md` — a ~500-word summary of the most recent update. Saves a page read when the user's question is about recent additions.

---

## Cost guidance

| Operation | Approximate cost |
|-----------|-----------------|
| Init | ~2k tokens |
| Ingest 1 article (5k words) | ~15–25k tokens |
| Ingest batch of 10 articles | ~150–250k tokens |
| Query (index + 3 pages) | ~3–6k tokens |
| Lint (full wiki, 50 pages) | ~40–80k tokens |

Token savings vs. raw context: querying a 50-page wiki costs ~5k tokens. Querying the same 50 raw documents costs ~500k tokens. **100× reduction.**

For large batch ingests (10+ documents), suggest running in a fresh session with `/compact` disabled — these are long tasks.

---

## Example interactions

**"Build me a wiki for my AI research"**
→ `wiki init AI research` — creates vault, writes CLAUDE.md schema, confirms location

**"Ingest this article" (file in raw/)**
→ `wiki ingest` — reads raw/, creates wiki pages, updates index, asks follow-up questions

**"What does the wiki say about compute scaling?"**
→ `wiki query compute scaling` — reads index, reads 2–3 relevant pages, answers

**"Run a health check on my wiki"**
→ `wiki lint` — reads all pages, fixes orphans, flags gaps, creates analysis pages

**"How big is my wiki?"**
→ `wiki status` — page count, source count, last update, unprocessed raw files

**"Let my AltJunction project use this wiki"**
→ `wiki link` — appends query block to AltJunction's CLAUDE.md (project file stays local)
