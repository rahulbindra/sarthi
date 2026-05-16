#!/usr/bin/env python3
"""
Sarthi SessionStart hook.
Resets all session counters, clears delivery log, marks onboarding pending,
and injects the mandatory onboarding instruction.
"""
import json, os

d = os.path.expanduser('~/.claude')

# Reset numeric counters
for fname in ['.sarthi-session-reads', '.sarthi-session-edits',
              '.sarthi-bash-fail-count', '.sarthi-session-counter',
              '.sarthi-ratio-warned-at']:
    try:
        open(os.path.join(d, fname), 'w').write('0')
    except:
        pass

# Reset dict state
try:
    open(os.path.join(d, '.sarthi-session-warned'), 'w').write('{}')
except:
    pass

# Clear delivery and pending-warning logs for new session
for fname in ['.sarthi-session-delivery', '.sarthi-pending-warning']:
    try:
        open(os.path.join(d, fname), 'w').write('')
    except:
        pass

# Mark onboarding as pending (UserPromptSubmit checks this on first prompt)
try:
    open(os.path.join(d, '.sarthi-onboarding-pending'), 'w').close()
except:
    pass

print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': (
            'MANDATORY — execute before responding to the user: '
            'You must run the Sarthi Session Onboarding block. '
            'Do NOT process the user first message yet. '
            'Required steps in order: '
            '(1) Run all bash detection commands from the Session Onboarding block in '
            '~/.claude/skills/sarthi/SKILL.md — graphify, codeburn, morph, skills list checks. '
            '(2) Auto-setup graphify if CLI detected. '
            '(3) Present the welcome prompt listing every detected tool. '
            '(4) Wait for the user skip choices. '
            '(5) Only then process the user message. '
            'Skill load is NOT skill execution. '
            'Skipping onboarding breaks all tool routing for the session.'
        )
    }
}))
