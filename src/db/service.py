"""Local PostgreSQL cluster management utility."""

import os
import subprocess
import sys
from pathlib import Path

USER_HOME = Path(os.environ.get("USERPROFILE", os.path.expanduser("~")))
PG_DIR = USER_HOME / ".pgsql"
PG_DATA_DIR = PG_DIR / "data"
BIN_DIR = PG_DIR / "pgsql" / "bin"
PG_CTL = BIN_DIR / "pg_ctl.exe"
LOG_FILE = PG_DATA_DIR / "server.log"


def status() -> bool:
    """Check if the local PostgreSQL server is running."""
    if not PG_CTL.exists():
        print(f"[ERROR] pg_ctl not found at {PG_CTL}")
        return False
    res = subprocess.run([str(PG_CTL), "-D", str(PG_DATA_DIR), "status"], capture_output=True, text=True)
    is_running = "server is running" in res.stdout
    print(res.stdout.strip() if res.stdout else res.stderr.strip())
    return is_running


def start():
    """Start local PostgreSQL server as a background service."""
    if not PG_DATA_DIR.exists():
        print(f"[ERROR] Data directory {PG_DATA_DIR} does not exist.")
        return
    print(f"Starting PostgreSQL server using data dir: {PG_DATA_DIR}...")
    res = subprocess.run(
        [str(PG_CTL), "-D", str(PG_DATA_DIR), "-l", str(LOG_FILE), "start"],
        capture_output=True,
        text=True,
    )
    print(res.stdout.strip() if res.stdout else res.stderr.strip())


def stop():
    """Stop local PostgreSQL server gracefully."""
    print("Stopping PostgreSQL server...")
    res = subprocess.run(
        [str(PG_CTL), "-D", str(PG_DATA_DIR), "-m", "fast", "stop"],
        capture_output=True,
        text=True,
    )
    print(res.stdout.strip() if res.stdout else res.stderr.strip())


if __name__ == "__main__":
    action = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
    if action == "start":
        start()
    elif action == "stop":
        stop()
    elif action == "status":
        status()
    else:
        print("Usage: python -m src.db.service [start|stop|status]")

