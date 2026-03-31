# apifox-client Skill 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 `apifox-client` skill，支持从 Apifox 读取接口定义（fetch）和推送本项目接口到 Apifox（sync）。

**Architecture:** 单一 SKILL.md 文件，包含 init/fetch/sync 三个子命令。配置统一存放在 `.claude/apifox-client/config.json`，通过 `capabilities` 字段控制每个项目支持的操作。fetch 直接调用 Apifox REST API，sync 扫描源码生成 OpenAPI spec 后上传。

**Tech Stack:** Python 3（内联脚本）、Apifox REST API v1、Claude Bash tool

**Spec:** `docs/superpowers/specs/2026-03-31-apifox-client-design.md`

---

### Task 1: 创建 SKILL.md 骨架 + init 子命令

**Files:**
- Create: `skills/apifox-client/SKILL.md`

- [ ] **Step 1: 创建目录并写入 SKILL.md（骨架 + init 部分）**

创建 `skills/apifox-client/SKILL.md`，内容如下：

````markdown
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
````

- [ ] **Step 2: 验证 init 内容**

对照 spec 检查：
- 配置路径为 `.claude/apifox-client/config.json` ✓
- 配置模板包含所有字段 ✓
- gitignore 路径正确 ✓

- [ ] **Step 3: Commit**

```bash
git add skills/apifox-client/SKILL.md
git commit -m "feat(apifox-client): add skill skeleton and init subcommand"
```

---

### Task 2: 实现 fetch 子命令

**Files:**
- Modify: `skills/apifox-client/SKILL.md`

- [ ] **Step 1: 追加 fetch 子命令到 SKILL.md**

在 `init` 章节后追加以下内容：

````markdown
---

## `fetch` — 读取接口定义

### 用法

```
/apifox-client fetch <project> <id或名称> [id或名称...]
```

**示例：**
```
/apifox-client fetch backend 123456
/apifox-client fetch backend 123456 789012
/apifox-client fetch backend "用户登录"
/apifox-client fetch backend 123456 "获取订单列表"
```

### Step 1. 读取配置并校验

```bash
python3 - << 'PYEOF'
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
    caps = ",".join(p.get("capabilities", []))
    print(f"PROJECT:{p['name']}:{p['projectId']}:{caps}")
PYEOF
```

- 若配置不存在，提示先执行 `/apifox-client init`
- 若 token 缺失或为占位值，用 **AskUserQuestion** 询问后写入配置（输出时显示 `AK-****`）
- 若指定的 project 不存在，报错退出
- 若 project `capabilities` 不含 `"read"`，报错：`项目 {name} 未配置 "read" capability，请在 config.json 中添加`

### Step 2. 拉取接口定义

对用户传入的每个标识符判断类型并调用 Apifox API：

```bash
python3 - << 'PYEOF'
import urllib.request, urllib.parse, json, os, sys

token = "..."          # 从配置读取
project_id = 0         # 从配置读取
identifiers = [...]    # 用户传入的 id 或名称列表

BASE = "https://api.apifox.com/v1"
HEADERS = {
    "Authorization": f"Bearer {token}",
    "X-Apifox-Api-Version": "2024-03-28"
}

def api_get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

results = []
for ident in identifiers:
    if str(ident).isdigit():
        # 按 ID 精确获取
        data = api_get(f"{BASE}/projects/{project_id}/http-apis/{ident}")
        api = data.get("data", {})
        if api:
            results.append(api)
        else:
            print(f"NOT_FOUND_ID:{ident}")
    else:
        # 按名称搜索
        encoded = urllib.parse.quote(str(ident))
        data = api_get(f"{BASE}/projects/{project_id}/http-apis?keywords={encoded}")
        items = data.get("data", {}).get("items", [])
        if len(items) == 0:
            print(f"NOT_FOUND_NAME:{ident}")
        elif len(items) == 1:
            results.append(items[0])
        else:
            # 多条命中，输出候选列表
            candidates = [{"id": i["id"], "name": i.get("name",""), "method": i.get("method",""), "path": i.get("path","")} for i in items]
            print(f"MULTIPLE:{ident}:" + json.dumps(candidates, ensure_ascii=False))

print("RESULTS:" + json.dumps(results, ensure_ascii=False))
PYEOF
```

- 若某标识符返回 `MULTIPLE:`，向用户列出候选并询问选择哪个，再按 ID 重新拉取
- 若某标识符 `NOT_FOUND_*`，告知用户该标识符未找到，继续处理其余标识符

### Step 3. 格式化输出

将 `results` 中每条接口按以下格式输出，供用户结合提示词生成代码：

```
已加载 N 个接口定义：

[接口 1] {METHOD} {path}
  名称：{name}
  描述：{description}
  路径参数：{parameters where in=path}
  查询参数：{parameters where in=query}
  请求头：{parameters where in=header}
  请求体：{requestBody schema}
  响应：{responses["200"] schema}

[接口 2] ...
```

- 字段为空时跳过该行
- 请求体和响应 schema 输出 JSON Schema 的 `properties` 摘要（字段名: 类型）
- 输出完成后提示：**"接口定义已加载，请告诉我需要生成什么代码（如 axios、OpenFeign）"**
````

- [ ] **Step 2: 验证 fetch 内容**

检查：
- 按 ID 调用路径：`GET /v1/projects/{projectId}/http-apis/{apiId}` ✓
- 按名称搜索路径：`GET /v1/projects/{projectId}/http-apis?keywords={name}` ✓
- 多条命中时有交互逻辑 ✓
- capabilities 校验存在 ✓
- 输出格式完整 ✓

- [ ] **Step 3: Commit**

```bash
git add skills/apifox-client/SKILL.md
git commit -m "feat(apifox-client): add fetch subcommand"
```

---

### Task 3: 实现 sync 子命令

**Files:**
- Modify: `skills/apifox-client/SKILL.md`

- [ ] **Step 1: 追加 sync 子命令到 SKILL.md**

在 `fetch` 章节后追加以下内容：

````markdown
---

## `sync` — 推送接口到 Apifox

### 用法

```
/apifox-client sync                        # 仅一个 sync 项目时直接使用
/apifox-client sync backend               # 指定 project
/apifox-client sync backend /users /orders # 只同步匹配路径的接口
/apifox-client sync backend UserController # 只同步指定控制器
/apifox-client sync backend /users UserController # 混合
```

### Step 1. 读取配置

```bash
python3 - << 'PYEOF'
import os, json

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
config_file = os.path.join(project_root, ".claude", "apifox-client", "config.json")

if not os.path.exists(config_file):
    print("CONFIG_NOT_FOUND")
else:
    with open(config_file) as f:
        config = json.load(f)
    print(f"TOKEN:{config.get('accessToken', '')}")
    for p in config.get("projects", []):
        caps = ",".join(p.get("capabilities", []))
        print(f"PROJECT:{json.dumps(p)}")
PYEOF
```

- 若配置不存在，提示先执行 `/apifox-client init`
- 若 token 缺失或为占位值，用 **AskUserQuestion** 询问后写入配置（输出时显示 `AK-****`）

### Step 2. 确定 project 和接口范围

解析用户参数：
- **第一个非路径、非控制器参数** = project name
- **以 `/` 开头** = 路由路径过滤器（前缀匹配）
- **大写开头或含 `Controller` / `Handler` / `Router`** = 控制器/文件名过滤器
- 未指定 project 时：若只有一个 sync 项目直接使用，多个则询问
- 若 project `capabilities` 不含 `"sync"`，报错：`项目 {name} 未配置 "sync" capability`

### Step 3. 扫描源码生成 OpenAPI Spec

- 识别框架（Spring Boot、Express、FastAPI、NestJS、Go Gin 等）
- 用 Glob/Grep/Read 找路由/控制器文件（可按控制器名过滤）
- 提取：HTTP 方法、路径、参数、请求体、响应 schema、注释
- 可复用 schema 放入 `components/schemas`
- 路径过滤器不为空时，只保留匹配前缀的路径
- 输出 OpenAPI 3.0 JSON 写入 `/tmp/apifox-client-sync-{name}.json`

### Step 4. 上传到 Apifox

```bash
python3 - << 'PYEOF'
import json, subprocess, os

project_name = "..."    # 从用户参数读取
project_id = 0          # 从配置读取
module_id = None        # 从配置读取
folder_id = None        # 从配置读取
overwrite = "OVERWRITE_EXISTING"  # 从配置读取
token = "..."           # 从配置读取

spec = open(f"/tmp/apifox-client-sync-{project_name}.json").read()

payload = {
    "input": spec,
    "options": {
        "endpointOverwriteBehavior": overwrite,
        "schemaOverwriteBehavior": "OVERWRITE_EXISTING",
        "updateFolderOfChangedEndpoint": False
    }
}
if module_id is not None:
    payload["options"]["moduleId"] = module_id
if folder_id is not None:
    payload["options"]["targetEndpointFolderId"] = folder_id

result = subprocess.run([
    "curl", "-s", "-X", "POST",
    f"https://api.apifox.com/v1/projects/{project_id}/import-openapi",
    "-H", f"Authorization: Bearer {token}",
    "-H", "X-Apifox-Api-Version: 2024-03-28",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload)
], capture_output=True, text=True)

print(result.stdout)
os.remove(f"/tmp/apifox-client-sync-{project_name}.json")
PYEOF
```

### Step 5. 展示结果

```
Sync complete! [project: backend]
  Scope: /users, /orders (filtered)
  Endpoints: 3 created, 5 updated, 0 failed
  Schemas:   2 created, 1 updated, 0 failed
```

有错误时逐条展示 `data.errors`。非 200 时提示检查 token 和 projectId。
````

- [ ] **Step 2: 验证 sync 内容**

检查：
- 配置路径为 `.claude/apifox-client/config.json`（非旧版 `.claude/apifox-sync.json`）✓
- 无 `openApiUrl` 逻辑，固定走扫描源码 ✓
- capabilities 校验存在 ✓
- 临时文件上传后删除 ✓
- `moduleId` 在 payload 中正确传入 ✓

- [ ] **Step 3: Commit**

```bash
git add skills/apifox-client/SKILL.md
git commit -m "feat(apifox-client): add sync subcommand"
```

---

### Task 4: 追加 Common Issues 和 Guardrails，完成 SKILL.md

**Files:**
- Modify: `skills/apifox-client/SKILL.md`

- [ ] **Step 1: 追加 Common Issues 和 Guardrails**

在 sync 章节后追加：

````markdown
---

## Common Issues

| 问题 | 解决 |
|------|------|
| `CONFIG_NOT_FOUND` | 先执行 `/apifox-client init` 创建配置 |
| `401 Unauthorized` | Token 过期，重新生成后更新 `config.json` |
| `404 Not Found` | projectId 错误，检查 Apifox 项目设置 → 基本设置 |
| 接口名称搜索无结果 | 检查名称拼写，或改用接口 ID |
| 搜索命中多条 | skill 会列出候选，指定序号或 ID 选择 |
| sync 后接口未更新 | 检查 `overwriteBehavior` 是否为 `KEEP_EXISTING` |
| Folder ID 找不到 | 右键 Apifox 文件夹 → 复制链接，URL 中的数字即为 ID |

---

## Guardrails

- Token 输出时显示为 `AK-****`，不打印完整值
- 多个项目且未指定时，必须询问用户
- fetch 搜索命中多条时，列出候选让用户确认后再使用
- sync 成功后立即删除临时文件 `/tmp/apifox-client-sync-{name}.json`
- capabilities 不符合时，明确报错并提示如何修改配置
- 已存在同名 project 时，修改配置前需用户确认
````

- [ ] **Step 2: 对照 spec 做完整覆盖检查**

逐项核对 `docs/superpowers/specs/2026-03-31-apifox-client-design.md`：
- 配置文件路径 `.claude/apifox-client/config.json` ✓
- 配置字段完整（accessToken / name / projectId / capabilities / moduleId / folderId / overwriteBehavior）✓
- init：创建模板 + gitignore ✓
- fetch：按 ID / 按名称 / 多条候选交互 / 输出格式 ✓
- sync：扫描源码 / 路径过滤 / 控制器过滤 / 上传 / 结果展示 ✓
- Guardrails：token 掩码 / 多项目询问 / 临时文件清理 ✓

- [ ] **Step 3: Commit**

```bash
git add skills/apifox-client/SKILL.md
git commit -m "feat(apifox-client): add common issues and guardrails, complete SKILL.md"
```

---

### Task 5: 更新 README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 在技能列表中添加 apifox-client**

在 `README.md` 的技能列表表格中，`kb` 行后追加一行：

```markdown
| [apifox-client](skills/apifox-client/SKILL.md) | 从 Apifox 读取接口定义生成请求代码，或将本项目接口推送到 Apifox |
```

同时在"触发技能"表格中追加：

```markdown
| apifox-client | `读取接口定义`、`同步接口到 Apifox`、`/apifox-client fetch`、`/apifox-client sync` |
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add apifox-client to skill list in README"
```
