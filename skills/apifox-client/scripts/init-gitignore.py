import os

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
gitignore = os.path.join(project_root, ".gitignore")
entry = ".claude/apifox-client/config.json"

existing = open(gitignore).read() if os.path.exists(gitignore) else ""
if entry not in existing:
    with open(gitignore, "a") as f:
        f.write(f"\n{entry}\n")
    print(f"GITIGNORE_UPDATED:{gitignore}")
else:
    print(f"GITIGNORE_ALREADY_SET:{gitignore}")
