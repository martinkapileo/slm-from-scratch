#!/usr/bin/env python3
"""PostToolUse hook: after Claude edits a .py file, make sure it still compiles,
and lint it with ruff when ruff is installed.

Exit code 2 sends stderr back to Claude so it fixes the problem immediately.
"""

import json
import py_compile
import shutil
import subprocess
import sys

payload = json.load(sys.stdin)
path = (payload.get("tool_input") or {}).get("file_path", "")
if not path.endswith(".py"):
    sys.exit(0)

try:
    py_compile.compile(path, doraise=True)
except py_compile.PyCompileError as e:
    print(f"Syntax error in {path}:\n{e.msg}", file=sys.stderr)
    sys.exit(2)

if shutil.which("ruff"):
    r = subprocess.run(["ruff", "check", "--quiet", path], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ruff found issues in {path}:\n{r.stdout}{r.stderr}", file=sys.stderr)
        sys.exit(2)
