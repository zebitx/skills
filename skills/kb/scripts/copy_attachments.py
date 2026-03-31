#!/usr/bin/env python3
"""Copy or write attachment files into the kb attachment directory. Reads JSON from stdin.

Input JSON fields:
  kb_dir, project, date_str, slug,
  attachments: [[filename, content_or_src_path], ...]

Output lines:
  ATTACHMENT:<filename>
"""
import os, shutil, json, sys

data = json.load(sys.stdin)

kb_dir = data["kb_dir"]
project = data["project"]
date_str = data["date_str"]
slug = data["slug"]
attachment_files = data["attachments"]

attach_dir = os.path.join(kb_dir, project, f"{date_str}-{slug}")
os.makedirs(attach_dir, exist_ok=True)

for fname, src in attachment_files:
    dst = os.path.join(attach_dir, fname)
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    else:
        with open(dst, "w", encoding="utf-8") as f:
            f.write(src)
    print(f"ATTACHMENT:{fname}")
