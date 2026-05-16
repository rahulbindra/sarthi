#!/usr/bin/env python3
"""
PostToolUse hook for Read.
Increments the session read counter used by the ratio check.
"""
import sys, json, os

json.load(sys.stdin)  # consume stdin

path = os.path.expanduser('~/.claude/.sarthi-session-reads')
try:
    count = int(open(path).read().strip()) + 1
except:
    count = 1
open(path, 'w').write(str(count))
