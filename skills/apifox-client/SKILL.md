---
name: apifox-client
description: Use when the user wants to fetch API interface definitions from Apifox to generate request code, or sync project interfaces to Apifox. Triggers on "/apifox-client init", "/apifox-client fetch", "/apifox-client sync", "读取接口定义", "获取接口文档", "同步接口到 Apifox".
---

# apifox-client

双向 Apifox 工具：**fetch** 读取接口定义供代码生成，**sync** 将本项目接口推送到 Apifox。

---

## Subcommands

| 命令 | 说明 |
|------|------|
| `/apifox-client init` | 在 `.claude/apifox-client/config.json` 创建项目配置 |
| `/apifox-client fetch <project> <id或名称> [...]` | 从 Apifox 读取接口定义 |
| `/apifox-client sync [project] [接口范围]` | 扫描源码并推送接口到 Apifox |

---

## Config File: `.claude/apifox-client/config.json`

位于项目根目录的 `.claude/apifox-client/` 下，**应加入 `.gitignore`**。

```json
{
  "accessToken": "AK-your-token-here",
  "projects": [
    {
      "name": "backend",
      "projectId": 123456,
      "capabilities": ["read", "sync"],
      "moduleId": 78901,
      "folderId": null,
      "overwriteBehavior": "OVERWRITE_EXISTING"
    }
  ]
}
```

**字段说明：**

| 字段 | 说明 | 必填条件 |
|------|------|----------|
| `accessToken` | Apifox → 头像 → 账号设置 → API 访问令牌 | 必填 |
| `name` | 项目标签，命令中用于指定目标 | 必填 |
| `projectId` | Apifox 项目 ID（项目设置 → 基本设置） | 必填 |
| `capabilities` | 支持的操作：`"read"`、`"sync"` | 必填 |
| `moduleId` | 模块 ID | `"sync"` 时必填 |
| `folderId` | 文件夹 ID，null = 根目录 | 可选 |
| `overwriteBehavior` | `OVERWRITE_EXISTING` \| `AUTO_MERGE` \| `KEEP_EXISTING` \| `CREATE_NEW` | sync 时可选，默认 `OVERWRITE_EXISTING` |

---

## `init` — 初始化项目配置

1. 检测项目根目录（有 `.git` 的最近祖先目录，或当前目录）
2. 若 `.claude/apifox-client/config.json` 已存在，告知用户，**直接跳过，不覆盖**
3. 写入配置模板：

```bash
python3 - << 'PYEOF'
import os, json

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
config_dir = os.path.join(project_root, ".claude", "apifox-client")
config_file = os.path.join(config_dir, "config.json")

os.makedirs(config_dir, exist_ok=True)

config = {
    "accessToken": "AK-your-token-here",
    "projects": [
        {
            "name": "my-project",
            "projectId": 0,
            "capabilities": ["read", "sync"],
            "moduleId": 0,
            "folderId": None,
            "overwriteBehavior": "OVERWRITE_EXISTING"
        }
    ]
}

with open(config_file, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"CONFIG_CREATED:{config_file}")
PYEOF
```

4. 将配置文件加入 `.gitignore`：

```bash
grep -q "apifox-client/config.json" .gitignore 2>/dev/null || echo ".claude/apifox-client/config.json" >> .gitignore
```

5. 提示用户填写 `accessToken`、`projectId`、`moduleId`，并说明 capabilities 的含义。
