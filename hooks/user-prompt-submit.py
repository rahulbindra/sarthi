#!/usr/bin/env python3
"""
Sarthi UserPromptSubmit hook.
Runs inline session monitor + model advisor assessments before every response.
Outputs results directly — not a request to Claude, but a completed assessment.
"""
import sys, json, os

data = json.load(sys.stdin)
prompt = data.get('prompt', '')
prompt_lower = prompt.lower().strip()
messages = []

# ── Session Monitor ──────────────────────────────────────────────────────────
if os.path.exists(os.path.expanduser('~/.claude/.sarthi-session-monitor-enabled')):
    counter_path = os.path.expanduser('~/.claude/.sarthi-session-counter')
    warned_path  = os.path.expanduser('~/.claude/.sarthi-session-warned')

    try:
        count = int(open(counter_path).read().strip()) + 1
    except:
        count = 1
    open(counter_path, 'w').write(str(count))

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

# ── Model Advisor ────────────────────────────────────────────────────────────
if os.path.exists(os.path.expanduser('~/.claude/.sarthi-model-advisor-enabled')):
    # Check session suppression
    try:
        learnings = json.loads(open(os.path.expanduser('~/.claude/.sarthi-model-learnings.json')).read())
        rejects = learnings.get('session_consecutive_rejects', 0)
    except:
        rejects = 0

    if rejects < 2:
        words = prompt.split()

        # Skip: pure acknowledgments with no task
        pure_ack_words = {'ok','okay','got','it','thanks','i','see','makes','sense','noted',
                          'understood','sure','alright','great','perfect','yes','no','yep','nope'}
        is_pure_ack = (
            len(words) <= 5
            and all(w.lower().rstrip('.,!') in pure_ack_words for w in words)
        )

        # Skip: pure factual questions with no action
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
            # sonnet = no message (default; no switch needed)

# ── Output ───────────────────────────────────────────────────────────────────
if messages:
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'UserPromptSubmit',
            'additionalContext': '\n\n'.join(messages)
        }
    }))
