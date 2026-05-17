#!/usr/bin/env python3
"""
Sarthi UserPromptSubmit hook.
Fires before every Claude response. Checks (in order):
  1. Onboarding guard      — first prompt of session
  2. Pending warnings      — picked up from PostToolUse hooks (bash fail, ratio)
  3. MANDATORY: Prompt optimizer  — if enabled, Claude MUST invoke skill before responding
  4. MANDATORY: Model advisor     — if enabled, Claude MUST invoke skill before responding
  5. Parallel agent detector      — batch/multi-source tasks → flag parallelism opportunity
  6. Morph reminder               — if morph configured + bulk signals → enforce mcp__morph-mcp__edit_file
  7. Session monitor              — context fill nudge (opt-in, every 10 prompts)
  8. Delivery nudge               — no git commits after significant edits
"""
import sys, json, os, time, re

data = json.load(sys.stdin)
prompt       = data.get('prompt', '')
prompt_lower = prompt.lower().strip()
messages     = []

# ── Unconditional session counter ────────────────────────────────────────────
counter_path = os.path.expanduser('~/.claude/.sarthi-session-counter')
try:
    count = int(open(counter_path).read().strip()) + 1
except:
    count = 1
open(counter_path, 'w').write(str(count))

# ── 1. Onboarding guard ──────────────────────────────────────────────────────
pending_path = os.path.expanduser('~/.claude/.sarthi-onboarding-pending')
if os.path.exists(pending_path):
    age = time.time() - os.path.getmtime(pending_path)
    if age < 120:
        messages.append(
            '🚨 SARTHI ONBOARDING REQUIRED — do this before processing the user message:\n'
            '1. Run all bash detection commands from the Session Onboarding block in\n'
            '   ~/.claude/skills/sarthi/SKILL.md (graphify, codeburn, morph, skills checks)\n'
            '2. Auto-setup graphify if CLI is detected\n'
            '3. Present the welcome prompt listing every detected tool\n'
            '4. Wait for skip choices\n'
            'Then — and only then — process the user message.\n'
            'Skill load is NOT skill execution. This fires once per session.'
        )
        os.remove(pending_path)

# ── 2. Pending warnings from PostToolUse hooks ───────────────────────────────
warn_path = os.path.expanduser('~/.claude/.sarthi-pending-warning')
try:
    pending_warn = open(warn_path).read().strip()
    if pending_warn:
        messages.append(pending_warn)
        open(warn_path, 'w').write('')
except:
    pass

# ── Skip checks 3–6 for pure acknowledgements and trivial single-word prompts ─
pure_ack_words = {'ok','okay','got','it','thanks','i','see','makes','sense','noted',
                  'understood','sure','alright','great','perfect','yes','no','yep',
                  'nope','done','good','nice','cool','right','fine','k','y','n'}
words = prompt_lower.split()
is_pure_ack = len(words) <= 4 and all(w.rstrip('.,!?') in pure_ack_words for w in words)

if not is_pure_ack:

    # ── 3. MANDATORY: Prompt Optimizer ──────────────────────────────────────
    if os.path.exists(os.path.expanduser('~/.claude/.sarthi-prompt-optimizer-enabled')):
        messages.append(
            '🚨 MANDATORY PRE-TASK CHECK A — PROMPT OPTIMIZER ENABLED:\n'
            '   You MUST invoke: Skill(skill="sarthi-prompt-optimizer") BEFORE responding.\n'
            '   Do not rationalize past this. Do not batch it with the response.\n'
            '   Invoke the skill, wait for its output, then proceed.'
        )

    # ── 4. MANDATORY: Model Advisor ──────────────────────────────────────────
    if os.path.exists(os.path.expanduser('~/.claude/.sarthi-model-advisor-enabled')):
        try:
            learnings = json.loads(open(os.path.expanduser('~/.claude/.sarthi-model-learnings.json')).read())
            rejects = learnings.get('session_consecutive_rejects', 0)
        except:
            rejects = 0
        if rejects < 2:
            messages.append(
                '🚨 MANDATORY PRE-TASK CHECK B — MODEL ADVISOR ENABLED:\n'
                '   You MUST invoke: Skill(skill="sarthi-model-advisor") BEFORE responding.\n'
                '   Do not rationalize past this. Do not batch it with the response.\n'
                '   Invoke the skill, wait for its output, then proceed.'
            )

    # ── 5. Parallel agent detector ───────────────────────────────────────────
    batch_signals = [
        'all files', 'all sources', 'all unprocessed', 'each file', 'each source',
        'ingest all', 'process all', 'multiple sources', 'multiple files',
        'batch ', 'all raw', 'all pages', 'all of the', 'every file', 'every source',
        'both vaults', 'all vaults', '6 files', '7 files', '8 files', '10 files',
    ]
    has_batch = any(s in prompt_lower for s in batch_signals)
    # count numeric quantity signals: "5 sources", "8 files", etc
    qty_match = re.search(r'\b([5-9]|[1-9]\d+)\s*(files?|sources?|pages?|items?|tasks?|docs?)', prompt_lower)
    if has_batch or qty_match:
        messages.append(
            '⚡ PARALLEL AGENT OPPORTUNITY DETECTED:\n'
            '   This looks like a batch/multi-source task. Before starting:\n'
            '   1. Are the subtasks independent? (no shared files, no dependency chain?)\n'
            '   2. If yes → dispatch parallel agents via dispatching-parallel-agents skill\n'
            '      or use git worktrees (isolation: worktree) for concurrent execution.\n'
            '   3. Sequential processing of independent work wastes wall-clock time.\n'
            '   State explicitly: "I will use parallel agents" OR "sequential because: [reason]"'
        )

    # ── 6. Morph reminder ────────────────────────────────────────────────────
    morph_configured = False
    try:
        claude_json = json.load(open(os.path.expanduser('~/.claude.json')))
        morph_configured = 'morph-mcp' in claude_json.get('mcpServers', {})
    except:
        pass

    multi_file_signals = [
        'all files', 'multiple files', 'all pages', 'ingest', 'batch',
        'bulk', 'all sources', 'every file', 'wiki', 'create pages',
        'write pages', 'generate pages', '3 files', '4 files', '5 files',
    ]
    has_multi_file = any(s in prompt_lower for s in multi_file_signals)

    if morph_configured and has_multi_file:
        messages.append(
            '🔧 MORPH ACTIVE — MANDATORY FOR MULTI-FILE TASKS:\n'
            '   This task touches multiple files. You MUST use mcp__morph-mcp__edit_file\n'
            '   instead of native Edit/Write for every file change.\n'
            '   Announce once: "Using Morph for this task." then use it exclusively.\n'
            '   Do NOT mix Edit and mcp__morph-mcp__edit_file in the same task.'
        )

# ── 7. Session Monitor (opt-in, every 10 prompts) ───────────────────────────
if os.path.exists(os.path.expanduser('~/.claude/.sarthi-session-monitor-enabled')):
    warned_path = os.path.expanduser('~/.claude/.sarthi-session-warned')
    try:
        warned = json.loads(open(warned_path).read())
    except:
        warned = {}

    if count >= 35 and not warned.get('w100'):
        messages.append(
            '⚠️  SESSION MONITOR: Context is ~100% full (35+ exchanges).\n'
            '   Start a fresh session. Run /compact first to capture key context.'
        )
        warned['w100'] = True
        open(warned_path, 'w').write(json.dumps(warned))
    elif count >= 25 and not warned.get('w90'):
        messages.append(
            '⚠️  SESSION MONITOR: Context is ~90% full (25+ exchanges).\n'
            '   Consider /compact or starting a fresh session soon.'
        )
        warned['w90'] = True
        open(warned_path, 'w').write(json.dumps(warned))

# ── 8. Delivery nudge ────────────────────────────────────────────────────────
if count == 20:
    try:
        edits = int(open(os.path.expanduser('~/.claude/.sarthi-session-edits')).read().strip())
    except:
        edits = 0
    try:
        has_delivery = bool(open(os.path.expanduser('~/.claude/.sarthi-session-delivery')).read().strip())
    except:
        has_delivery = False

    if edits >= 5 and not has_delivery:
        messages.append(
            f'📦 DELIVERY CHECK: {edits} file edits this session, 0 git commits.\n'
            'Is the work ready to commit? Consider /ce-commit-push-pr or git add + commit.\n'
            'Ignore if this is an exploration or research session.'
        )

# ── Output ────────────────────────────────────────────────────────────────────
if messages:
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': '\n\n'.join(messages)
        }
    }))
