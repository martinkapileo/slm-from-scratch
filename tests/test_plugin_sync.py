import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_plugin_matches_dot_claude():
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_plugin.py"), "--check"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
