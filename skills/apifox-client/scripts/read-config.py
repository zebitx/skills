"""Read .claude/apifox-client/config.json and output TOKEN: and PROJECT: lines.

Outputs:
  CONFIG_NOT_FOUND         — config file does not exist
  TOKEN:{accessToken}      — the access token value
  PROJECT:{json}           — one line per project, full JSON object
"""
import os, json, sys

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
config_file = os.path.join(project_root, ".claude", "apifox-client", "config.json")

if not os.path.exists(config_file):
    print("CONFIG_NOT_FOUND")
    sys.exit(0)

with open(config_file) as f:
    config = json.load(f)

print(f"TOKEN:{config.get('accessToken', '')}")
for p in config.get("projects", []):
    print(f"PROJECT:{json.dumps(p)}")
