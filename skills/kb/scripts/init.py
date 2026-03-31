#!/usr/bin/env python3
"""Initialize project-level kb config. Prints CREATED or EXISTS."""
import os, json, re

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
config_dir = os.path.join(project_root, ".claude", "skills", "kb")
config_file = os.path.join(config_dir, "kb-config.json")

if os.path.exists(config_file):
    print(f"EXISTS:{config_file}")
else:
    os.makedirs(config_dir, exist_ok=True)

    detected = os.popen(
        "git -C . remote get-url origin 2>/dev/null | sed 's/.*\\///' | sed 's/\\.git$//'"
    ).read().strip() or os.path.basename(project_root)
    project_name = re.sub(r'[^a-z0-9-]', '-', detected.lower()).strip('-')

    config = {
        "knowledgeBaseDir": "/path/to/your/knowledge-base",
        "projectName": project_name
    }

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"CREATED:{config_file}")
    print(f"PROJECT:{project_name}")
