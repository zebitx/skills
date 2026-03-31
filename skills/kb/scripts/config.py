#!/usr/bin/env python3
"""Read kb config and print KB_DIR and PROJECT."""
import os, json, re

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
project_config = os.path.join(project_root, ".claude", "skills", "kb", "kb-config.json")
global_config = os.path.expanduser("~/.claude/skills/kb/kb-config.json")

config = {}
for path in [project_config, global_config]:
    if os.path.exists(path):
        with open(path) as f:
            config = json.load(f)
        break

kb_dir = config.get("knowledgeBaseDir", "/path/to/your/knowledge-base")
project_name = config.get("projectName", "").strip()

if not project_name:
    project_name = os.popen(
        "git -C . remote get-url origin 2>/dev/null | sed 's/.*\\///' | sed 's/\\.git$//'"
    ).read().strip() or os.path.basename(project_root)

project_name = re.sub(r'[^a-z0-9-]', '-', project_name.lower()).strip('-')

print(f"KB_DIR:{kb_dir}")
print(f"PROJECT:{project_name}")
