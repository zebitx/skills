#!/usr/bin/env python3
"""Write a kb record file. Reads JSON from stdin.

Input JSON fields:
  kb_dir, project, slug, title, entry_type, description,
  changes (optional), decisions (optional), notes (optional),
  attachments (optional): [[filename, description], ...]

Output lines:
  CREATED:<filepath>
  ATTACH_DIR:<dirname>   (only if attachments present)
"""
import os, json, sys, datetime

data = json.load(sys.stdin)

kb_dir = data["kb_dir"]
project = data["project"]
slug = data["slug"]
title = data["title"]
entry_type = data["entry_type"]
description = data["description"]
changes = data.get("changes", "")
decisions = data.get("decisions", "")
notes = data.get("notes", "")
attachments = data.get("attachments", [])

now = datetime.datetime.now()
date_str = now.strftime("%Y-%m-%d")
datetime_str = now.strftime("%Y-%m-%d %H:%M")

target_dir = os.path.join(kb_dir, project)
os.makedirs(target_dir, exist_ok=True)

# Handle filename conflicts
base_slug = slug
counter = 2
target_file = os.path.join(target_dir, f"{date_str}-{slug}.md")
while os.path.exists(target_file):
    slug = f"{base_slug}-{counter}"
    target_file = os.path.join(target_dir, f"{date_str}-{slug}.md")
    counter += 1

sections = [f"# {title} [{entry_type}]\n"]
sections.append(f"**项目**: {project}")
sections.append(f"**日期**: {datetime_str}")
sections.append(f"**路径**: `{project}/{date_str}-{slug}.md`\n")
sections.append(f"## 描述\n\n{description}")
if changes.strip():
    sections.append(f"## 关键变动\n\n{changes}")
if decisions.strip():
    sections.append(f"## 技术决策\n\n{decisions}")
if notes.strip():
    sections.append(f"## 注意事项\n\n{notes}")
if attachments:
    attach_lines = "\n".join(
        f"- [{desc}](./{date_str}-{slug}/{fname})" for fname, desc in attachments
    )
    sections.append(f"## 附件\n\n{attach_lines}")

with open(target_file, "w", encoding="utf-8") as f:
    f.write("\n\n".join(sections) + "\n")

print(f"CREATED:{target_file}")
if attachments:
    print(f"ATTACH_DIR:{date_str}-{slug}/")
