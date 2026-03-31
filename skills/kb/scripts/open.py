#!/usr/bin/env python3
"""Find kb files matching a query.

Usage: open.py <kb_dir> <project> [query]

Output lines:
  MATCH:<filepath>
  PROJECT_NOT_FOUND:<name>
  AVAILABLE:<comma-separated list>
"""
import os, glob as glob_module, sys

kb_dir = sys.argv[1]
default_project = sys.argv[2]
arg = sys.argv[3] if len(sys.argv) > 3 else ""

if '/' in arg:
    parts = arg.split('/', 1)
    project = parts[0]
    query = parts[1]
else:
    project = default_project
    query = arg

project_dir = os.path.join(kb_dir, project)

if not os.path.isdir(project_dir):
    projects = [d for d in os.listdir(kb_dir) if os.path.isdir(os.path.join(kb_dir, d))]
    print(f"PROJECT_NOT_FOUND:{project}")
    print("AVAILABLE:" + ",".join(sorted(projects)))
else:
    if query.endswith(".md"):
        matches = glob_module.glob(f"{project_dir}/{query}")
    elif len(query) == 10 and query[4] == '-' and query[7] == '-':
        matches = glob_module.glob(f"{project_dir}/{query}-*.md")
    elif query:
        matches = glob_module.glob(f"{project_dir}/*{query}*.md")
    else:
        all_files = glob_module.glob(f"{project_dir}/*.md")
        matches = sorted(all_files, key=os.path.getmtime, reverse=True)[:10]

    for f in sorted(matches, key=os.path.getmtime, reverse=True):
        print(f"MATCH:{f}")
