#!/usr/bin/env python3
"""
Sarthi UserPromptSubmit hook.
Fires before every Claude response. Checks (in order):
  1. Onboarding guard    — first prompt of session
  2. Pending warnings    — picked up from PostToolUse hooks (bash fail, ratio)
  3. Session monitor     — context fill nudge (opt-in)
  4. Model advisor       — model complexity suggestion (opt-in)
  5. Delivery nudge      — no git commits after significant edits
"""
import sys, json, os, time

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
# SessionStart touches .sarthi-onboarding-pending. <120s old = first prompt.
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
        open(warn_path, 'w').write('')  # clear after pickup
except:
    pass

# ── 3. Session Monitor (opt-in) ──────────────────────────────────────────────
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

# ── 4. Model Advisor (opt-in) ────────────────────────────────────────────────
if os.path.exists(os.path.expanduser('~/.claude/.sarthi-model-advisor-enabled')):
    try:
        learnings = json.loads(open(os.path.expanduser('~/.claude/.sarthi-model-learnings.json')).read())
        rejects = learnings.get('session_consecutive_rejects', 0)
    except:
        rejects = 0

    if rejects < 2:
        words = prompt.split()

        pure_ack_words = {'ok','okay','got','it','thanks','i','see','makes','sense','noted',
                          'understood','sure','alright','great','perfect','yes','no','yep','nope'}
        is_pure_ack = (
            len(words) <= 5
            and all(w.lower().rstrip('.,!') in pure_ack_words for w in words)
        )
        is_question_only = (
            prompt_lower.startswith(('what ', 'how ', 'why ', 'when ', 'where ', 'who ',
                                     'is ', 'does ', 'can ', 'will ', 'should '))
            and '?' in prompt
            and len(words) < 15
            and not any(s in prompt_lower for s in
                        ['fix','add','update','create','build','edit','change',
                         'implement','write','delete','remove','refactor','generate'])
        )

        if not is_pure_ack and not is_question_only:
            opus_signals = [
                'architecture','security audit','sprint plan','roadmap','system design',
                'strategic','vulnerability','sarthi audit','run audit','cross-service',
                'multi-system','major refactor','investigate all','deep dive',
                'design decision','product planning','i have an idea',
            ]
            haiku_signals = [
                'typo','rename ','find ','grep','where is','list ','format ',
                'quick fix','one line','single file','lookup','move file',
                'delete file','copy file','check if',
            ]

            opus_score  = sum(1 for s in opus_signals  if s in prompt_lower)
            haiku_score = sum(1 for s in haiku_signals if s in prompt_lower)

            if opus_score >= 1:
                messages.append(
                    '🤖 MODEL ADVISOR: Complexity = COMPLEX — Opus 4.7 recommended.\n'
                    '   Switch now if not already on Opus: /model claude-opus-4-7\n'
                    '   Reply [y] noted / [s] skip / [r] skip + reason'
                )
            elif haiku_score >= 2:
                messages.append(
                    '🤖 MODEL ADVISOR: Complexity = SIMPLE — Haiku 4.5 recommended.\n'
                    '   Switch now if not already on Haiku: /model claude-haiku-4-5-20251001\n'
                    '   Reply [y] noted / [s] skip / [r] skip + reason'
                )

# ── 5. Delivery nudge ────────────────────────────────────────────────────────
# At prompt 20, if 5+ edits made but no git commits: soft check-in.
# Fires once per session (only at count == 20).
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
