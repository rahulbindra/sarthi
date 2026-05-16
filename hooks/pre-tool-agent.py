#!/usr/bin/env python3
"""
PreToolUse hook for Agent tool dispatches.
Fires before every sub-agent is spawned. If the session already has
significant context (counter > 15), warns that the agent will inherit
that context and suggests /compact to reduce cost.

Injects additionalContext (non-blocking) — never exits with code 2
so the agent dispatch always proceeds.
"""
import sys, json, os

data = json.load(sys.stdin)

# Only act on Agent tool dispatches
tool_name = data.get('tool_name', '')
if tool_name != 'Agent':
    sys.exit(0)

counter_path  = os.path.expanduser('~/.claude/.sarthi-session-counter')
agents_path   = os.path.expanduser('~/.claude/.sarthi-agents-dispatched')
suppressed_path = os.path.expanduser('~/.claude/.sarthi-agent-warn-suppressed')

# Read session exchange count
try:
    count = int(open(counter_path).read().strip())
except:
    count = 0

# Track agents dispatched this session
try:
    agents = int(open(agents_path).read().strip()) + 1
except:
    agents = 1
open(agents_path, 'w').write(str(agents))

# Only warn when session is long enough to matter (> 15 exchanges)
# and not already suppressed for this session
if count <= 15:
    sys.exit(0)

try:
    suppressed = open(suppressed_path).read().strip() == '1'
except:
    suppressed = False

if suppressed:
    sys.exit(0)

# Build warning — reference the sub-agent type if available
tool_input   = data.get('tool_input', {})
agent_type   = tool_input.get('subagent_type', 'sub-agent')
description  = tool_input.get('description', '')
desc_snippet = f' ("{description[:50]}")' if description else ''

warning = (
    f'⚡ AGENT DISPATCH WARNING — session has {count} exchanges of accumulated context.\n'
    f'Dispatching {agent_type}{desc_snippet} will inherit this full context, '
    f'multiplying its input cost.\n'
    f'Consider running /compact before this dispatch to reduce cost by ~60%.\n'
    f'Type [s] to suppress this warning for the rest of the session, or proceed to dispatch.'
)

print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'PreToolUse',
        'additionalContext': warning
    }
}))
