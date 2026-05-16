#!/usr/bin/env python3
"""
PostToolUse hook for Bash.
- Tracks consecutive bash failures. Injects hard-stop at 2 in a row.
- Detects successful git commits and writes to session delivery log.
"""
import sys, json, os, re

data = json.load(sys.stdin)
tool_input    = data.get('tool_input', {})
tool_response = data.get('tool_response', '')

command = tool_input.get('command', '')

# Normalise response to string
if isinstance(tool_response, dict):
    resp_str      = tool_response.get('output', '') or str(tool_response)
    exit_code_raw = tool_response.get('exit_code', None)
else:
    resp_str      = str(tool_response)
    exit_code_raw = None

# Detect failure
failed = False
if exit_code_raw is not None:
    failed = int(exit_code_raw) != 0
else:
    m = re.search(r'exit code[:\s]+(\d+)', resp_str, re.IGNORECASE)
    if m:
        failed = m.group(1) != '0'
    elif resp_str.strip().startswith('Error') or resp_str.strip().startswith('error:'):
        failed = True

fail_path     = os.path.expanduser('~/.claude/.sarthi-bash-fail-count')
delivery_path = os.path.expanduser('~/.claude/.sarthi-session-delivery')
pending_path  = os.path.expanduser('~/.claude/.sarthi-pending-warning')

output = {}

if failed:
    try:
        count = int(open(fail_path).read().strip()) + 1
    except:
        count = 1
    open(fail_path, 'w').write(str(count))

    if count >= 2:
        warning = (
            f'🛑 TWO-RETRY HARD STOP (harness-enforced): {count} consecutive bash failures.\n'
            'STOP — do NOT attempt another fix with the same approach.\n'
            'Required: restate the problem from scratch, propose a different strategy, '
            'confirm with user before proceeding.'
        )
        # Inject immediately via PostToolUse additionalContext
        output = {
            'hookSpecificOutput': {
                'hookEventName': 'PostToolUse',
                'additionalContext': warning
            }
        }
        # Also write to pending file as fallback for UserPromptSubmit
        try:
            open(pending_path, 'w').write(warning)
        except:
            pass
else:
    # Reset fail counter on success
    try:
        open(fail_path, 'w').write('0')
    except:
        pass
    # Clear any pending warning from a previous failure
    try:
        open(pending_path, 'w').write('')
    except:
        pass

    # Detect successful git commit
    if 'git commit' in command:
        no_commit = 'nothing to commit' in resp_str.lower()
        is_error  = resp_str.strip().lower().startswith('error')
        if not no_commit and not is_error:
            try:
                open(delivery_path, 'a').write(command[:120] + '\n')
            except:
                pass

if output:
    print(json.dumps(output))
