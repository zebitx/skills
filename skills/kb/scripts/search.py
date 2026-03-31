#!/usr/bin/env python3
"""Full-text search across kb files.

Usage: search.py <kb_dir> <project> <keyword> [--all]

Output lines:
  FILE:<rel_path>|TITLE:<title>|PREVIEW:<preview>
"""
import os, subprocess, sys

kb_dir = sys.argv[1]
project = sys.argv[2]
keyword = sys.argv[3]
search_all = len(sys.argv) > 4 and sys.argv[4] == "--all"

search_dir = kb_dir if search_all else os.path.join(kb_dir, project)

result = subprocess.run(
    ["grep", "-rl", "--include=*.md", "-i", keyword, search_dir],
    capture_output=True, text=True
)

files = [f for f in result.stdout.strip().split("\n") if f]

for fpath in files:
    with open(fpath) as f:
        lines = f.readlines()
    title = lines[0].strip().lstrip("# ") if lines else fpath
    hits = [l.strip() for l in lines if keyword.lower() in l.lower() and not l.startswith("#")]
    preview = hits[0][:80] if hits else ""
    rel = os.path.relpath(fpath, kb_dir)
    print(f"FILE:{rel}|TITLE:{title}|PREVIEW:{preview}")
