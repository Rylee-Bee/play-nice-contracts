#!/usr/bin/env python3
"""Deterministic fake agent launcher target for the playnice test suite.

`playnice` launches `agent.command agent.args <prompt>`; tests configure the
command to this script's interpreter path. The script records the invocation
(env, cwd, prompt) to FAKE_AGENT_LOG and exits with FAKE_AGENT_RC.
"""

import json
import os
import sys

log = os.environ.get("FAKE_AGENT_LOG", "")
if log:
    record = {
        "argv": sys.argv[1:],
        "cwd": os.getcwd(),
        "PLAY_NICE_LIBRARY": os.environ.get("PLAY_NICE_LIBRARY", ""),
        "PLAY_NICE_PERMIT": os.environ.get("PLAY_NICE_PERMIT", ""),
    }
    with open(log, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

sys.exit(int(os.environ.get("FAKE_AGENT_RC", "0")))
