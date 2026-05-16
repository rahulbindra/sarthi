#!/usr/bin/env python3
"""
PostToolUse hook for Edit/Write.
Increments edit counter. Warns when edits outpace reads (ratio < 1:1 after 3+ edits).
Throttled: fires at most once per 5 additional edits while ratio stays bad.
"""
import sys, json, os

json.load(sys.stdin)  # consume stdin

reads_path      = os.path.expanduser('~/.claude/.sarthi-session-reads')
edits_path      = os.path.expanduser('~/.claude/.sarthi-session-edits')
warned_at_path  = os.path.expanduser('~/.claude/.sarthi-ratio-warned-at')
pending_path    = os.path.expanduser('~/.claude/.sarthi-pending-warning')

try:
    reads = int(open(reads_path).read().strip())
except:
    reads = 0

try:
    edits = int(open(edits_path).read().strip()) + 1
except:
    edits = 1
open(edits_path, 'w').write(str(edits))

# Only check after 3 edits to avoid noise at task start
if edits < 3:
    pass
elif reads < edits:
    try:
        last_warned = int(open(warned_at_path).read().strip())
    except:
        last_warned = 0

    # Fire on first detection, then every 5 additional edits while ratio stays bad
    if last_warned == 0 or edits >= last_warned + 5:
        open(warned_at_path, 'w').write(str(edits))
        ratio = reads / edits
        warning = (
            f'⚠️ READ:EDIT RATIO LOW: {reads} reads, {edits} edits ({ratio:.1f}:1 — target 4:1). '
            f'Read the file before the next edit.'
        )
        # Inject immediately; also write pending as fallback
        print(json.dumps({
            'hookSpecificOutput': {
                'hookEventName': 'PostToolUse',
                'additionalContext': warning
            }
        }))
        try:
            # Only overwrite pending if no bash failure is already pending
            existing = open(pending_path).read().strip()
            if not existing:
                open(pending_path, 'w').write(warning)
        except:
            try:
                open(pending_path, 'w').write(warning)
            except:
                pass
