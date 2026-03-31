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
PYEOF
```

- 若输出 `CONFIG_EXISTS:`，告知用户配置文件已存在，跳过初始化

4. 将配置文件加入 `.gitignore`：

```bash
python3 - << 'PYEOF'
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
PYEOF
```

5. 提示用户填写 `accessToken`、`projectId`、`moduleId`，并说明 capabilities 的含义。

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
- 若 token 缺失或仍为占位值（`AK-your-token-here`），用 **AskUserQuestion** 询问后写入配置（输出时显示 `AK-****`）
- 若指定的 project 不存在于配置中，报错退出
- 若 project `capabilities` 不含 `"read"`，报错：`项目 {name} 未配置 "read" capability，请在 config.json 中添加`

解析 Step 1 输出的 `TOKEN:` 行和 `PROJECT:` 行，获取 `token` 和 `project_id`，将其与用户传入的标识符列表一起代入 Step 2 脚本中再执行。

### Step 2. 拉取接口定义

对用户传入的每个标识符判断类型并调用 Apifox API：

```bash
python3 - << 'PYEOF'
import urllib.request, urllib.error, urllib.parse, json, os, sys

token = "..."          # 从配置读取，替换为实际值
project_id = 0         # 从配置读取，替换为实际值
identifiers = [...]    # 用户传入的 id 或名称列表，替换为实际值

BASE = "https://api.apifox.com/v1"
HEADERS = {
    "Authorization": f"Bearer {token}",
    "X-Apifox-Api-Version": "2024-03-28"
}

def api_get(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP_ERROR:{e.code}:{url}")
        return None

results = []
for ident in identifiers:
    if str(ident).isdigit():
        # 按 ID 精确获取
        data = api_get(f"{BASE}/projects/{project_id}/http-apis/{ident}")
        if data is None: continue
        api = data.get("data", {})
        if api:
            results.append(api)
        else:
            print(f"NOT_FOUND_ID:{ident}")
    else:
        # 按名称搜索
        encoded = urllib.parse.quote(str(ident))
        data = api_get(f"{BASE}/projects/{project_id}/http-apis?keywords={encoded}")
        if data is None: continue
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

- 若某标识符返回 `MULTIPLE:`，向用户列出候选（id、name、method、path），询问选择哪个；获得用户回复后，将该标识符替换为选定的数字 ID，重新执行 Step 2（仅针对该标识符），然后将结果合并到 `results` 中再继续 Step 3
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
        print(f"PROJECT:{json.dumps(p)}")
PYEOF
```

- 若配置不存在，提示先执行 `/apifox-client init`
- 若 token 缺失或仍为占位值（`AK-your-token-here`），用 **AskUserQuestion** 询问后写入配置（输出时显示 `AK-****`）

解析 Step 1 输出的 `TOKEN:` 行获取 token，解析 `PROJECT:` 行（JSON 格式）获取各项目配置（name、projectId、capabilities、moduleId、folderId、overwriteBehavior），在 Step 2 中据此校验 project 和 capabilities，在 Step 4 中代入实际值。

### Step 2. 确定 project 和接口范围

解析用户参数：
- **第一个非路径、非控制器参数** = project name
- **以 `/` 开头** = 路由路径过滤器（前缀匹配）
- **大写开头或含 `Controller` / `Handler` / `Router`** = 控制器/文件名过滤器
- 未指定 project 时：若只有一个 `capabilities` 含 `"sync"` 的项目直接使用，多个则用 **AskUserQuestion** 询问
- 若 project `capabilities` 不含 `"sync"`，报错：`项目 {name} 未配置 "sync" capability，请在 config.json 中添加`

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

project_name = "..."    # 从用户参数读取，替换为实际值
project_id = 0          # 从配置读取，替换为实际值
module_id = None        # 从配置读取，替换为实际值
folder_id = None        # 从配置读取，替换为实际值
overwrite = "OVERWRITE_EXISTING"  # 从配置读取，替换为实际值
token = "..."           # 从配置读取，替换为实际值

spec_file = f"/tmp/apifox-client-sync-{project_name}.json"
if not os.path.exists(spec_file):
    print(f"SPEC_NOT_FOUND:{spec_file} Step 3 未生成 spec 文件，请检查源码扫描步骤")
    import sys; sys.exit(0)
spec = open(spec_file).read()

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

response_text = result.stdout
print(response_text)

try:
    resp = json.loads(response_text)
    if resp.get("success") is False or "error" in resp:
        print(f"SYNC_ERROR:{spec_file} 保留临时文件供排查")
    else:
        os.remove(spec_file)
except (json.JSONDecodeError, Exception):
    # Non-JSON response (e.g. network error), keep the file
    print(f"SYNC_ERROR:{spec_file} 无法解析响应，保留临时文件供排查")
PYEOF
```

在执行前，将脚本中的占位符替换为从配置和用户参数中读取的实际值。

### Step 5. 展示结果

```
Sync complete! [project: backend]
  Scope: /users, /orders (filtered)
  Endpoints: 3 created, 5 updated, 0 failed
  Schemas:   2 created, 1 updated, 0 failed
```

有错误时逐条展示 `data.errors`。非 200 响应时提示检查 token 和 projectId。

---

## Common Issues

| 问题 | 解决 |
|------|------|
| `CONFIG_NOT_FOUND` | 先执行 `/apifox-client init` 创建配置 |
| `401 Unauthorized` / `HTTP_ERROR:401` | Token 过期，重新生成后更新 `config.json` |
| `404 Not Found` / `HTTP_ERROR:404` | projectId 错误，检查 Apifox 项目设置 → 基本设置 |
| 接口名称搜索无结果 (`NOT_FOUND_NAME:`) | 检查名称拼写，或改用接口 ID |
| 搜索命中多条 (`MULTIPLE:`) | skill 会列出候选，指定序号或 ID 选择 |
| sync 后接口未更新 | 检查 `overwriteBehavior` 是否为 `KEEP_EXISTING` |
| Folder ID 找不到 | 右键 Apifox 文件夹 → 复制链接，URL 中的数字即为 ID |
| `SPEC_NOT_FOUND:` | Step 3 源码扫描未生成 spec 文件，检查框架识别和路由提取是否成功 |
| `SYNC_ERROR:` | 上传失败，临时文件已保留，检查 token 和 projectId 后重试 |

---

## Guardrails

- Token 输出时显示为 `AK-****`，不打印完整值
- 多个项目且未指定时，必须用 **AskUserQuestion** 询问用户
- fetch 搜索命中多条时，列出候选让用户确认后再使用
- sync 仅在上传成功后删除临时文件 `/tmp/apifox-client-sync-{name}.json`
- capabilities 不符合时，明确报错并提示如何修改配置
- 已存在同名 project 修改配置前需用户确认
- `moduleId` 为 null 且 capabilities 含 `"sync"` 时，init 后提示用户必须填写真实的 moduleId 才能使用 sync
