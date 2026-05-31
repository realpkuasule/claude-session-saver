#!/usr/bin/env python3
"""
Batch restore: exports all recorded (but not yet exported) sessions
from ~/.claude/projects/ to ~/claude-sessions/ and ~/claude-session-logs/.
"""

import sys
import os

# Add the project directory to sys.path so we can import the saver
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the saver module (non-standard name with dashes — use importlib)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "claude_session_saver",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude-session-saver.py")
)
saver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(saver)

import glob
import time
from pathlib import Path
from datetime import datetime

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
SESSIONS_DIR = os.path.expanduser("~/claude-sessions")


def main():
    # Collect all source sessions
    source = {}
    for f in glob.glob(os.path.join(PROJECTS_DIR, "*", "*.jsonl")):
        sid = os.path.splitext(os.path.basename(f))[0]
        project = os.path.basename(os.path.dirname(f))
        source[sid] = (f, project)

    # Collect already exported session IDs
    exported = set()
    for f in glob.glob(os.path.join(SESSIONS_DIR, "*", "*", "*", "*.jsonl")):
        sid = os.path.splitext(os.path.basename(f))[0]
        exported.add(sid)

    # Find unexported, sorted by modification time (oldest first)
    unexported = []
    for sid, (path, proj) in source.items():
        if sid not in exported:
            unexported.append((os.path.getmtime(path), sid, path, proj))

    unexported.sort()  # oldest first

    total = len(unexported)
    print(f"=== Batch Session Restore ===")
    print(f"Total recorded: {len(source)}")
    print(f"Already exported: {len(exported)}")
    print(f"To restore: {total}")
    print()

    if total == 0:
        print("Nothing to do.")
        return

    success = 0
    skipped = 0
    errors = 0
    start_time = time.time()

    for i, (mtime, sid, src_path, project) in enumerate(unexported):
        dt = datetime.fromtimestamp(mtime)
        pct = (i + 1) / total * 100

        try:
            # Quick size check — skip empty or near-empty files
            size = os.path.getsize(src_path)
            if size < 50:
                skipped += 1
                if skipped <= 10 or skipped % 100 == 0:
                    print(f"  [{i+1}/{total} {pct:.1f}%] SKIP (empty): {sid} [{project}] {dt.strftime('%Y-%m-%d %H:%M')}")
                continue

            output = saver.export_session(sid, src_path)
            if output:
                success += 1
                if success <= 20 or success % 100 == 0:
                    print(f"  [{i+1}/{total} {pct:.1f}%] OK: {output}")
            else:
                skipped += 1
                if skipped <= 10 or skipped % 100 == 0:
                    print(f"  [{i+1}/{total} {pct:.1f}%] SKIP (no content): {sid} [{project}]")

        except Exception as e:
            errors += 1
            if errors <= 10 or errors % 50 == 0:
                print(f"  [{i+1}/{total} {pct:.1f}%] ERROR: {sid} [{project}]: {e}", file=sys.stderr)

    elapsed = time.time() - start_time
    print()
    print(f"=== Done in {elapsed:.1f}s ===")
    print(f"  Success: {success}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors:  {errors}")
    print(f"  Total:   {total}")


if __name__ == "__main__":
    main()
