import os, json

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
config_dir = os.path.join(project_root, ".claude", "apifox-client")
config_file = os.path.join(config_dir, "config.json")

if os.path.exists(config_file):
    print(f"CONFIG_EXISTS:{config_file}")
else:
    os.makedirs(config_dir, exist_ok=True)

    config = {
        "accessToken": "AK-your-token-here",
        "projects": [
            {
                "name": "my-project",
                "projectId": 0,
                "capabilities": ["read", "sync"],
                "moduleId": None,
                "folderId": None,
                "overwriteBehavior": "OVERWRITE_EXISTING"
            }
        ]
    }

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"CONFIG_CREATED:{config_file}")
