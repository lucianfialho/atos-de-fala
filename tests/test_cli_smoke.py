import subprocess
import sys


def test_cli_help_runs():
    r = subprocess.run(
        [sys.executable, "-m", "atos.gen.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    assert "--n" in r.stdout
    assert "--out" in r.stdout
