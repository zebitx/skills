---
name: kb
description: Use when the user wants to record, open, search, or manage a knowledge base of feature implementations and project changes. Triggers on "/kb record", "/kb open", "/kb search", "/kb init", phrases like "记录到知识库", "save to knowledge base", "读取知识库", "搜索知识库", "log this change", "记录这次实现".
---

# Knowledge Base (kb)

按项目和日期管理开发知识库，支持记录和读取。

## Overview

```
{kb-dir}/
  {project-name}/
    {YYYY-MM-DD}-{功能slug}.md   # 每个功能/变动独立一个文件
```

---

## Subcommands

| 命令 | 说明 |
|------|------|
| `/kb init` | 在当前项目创建 `.claude/kb-config.json` |
| `/kb record` | 将当前会话的功能实现或变动记录到知识库 |
| `/kb open [filename]` | 将知识库中的文件读入当前会话，支持跨项目 |
| `/kb search <keyword>` | 全文搜索知识库内容，支持跨项目 |

**收到 `/kb` 命令时，先读取第一个参数判断子命令，再执行对应流程。**

---

## Config Files（优先级从高到低）

1. **项目级**：`{project-root}/.claude/kb-config.json` — `init` 创建，优先使用
2. **全局**：`~/.claude/kb-config.json` — 全局默认

```json
{
  "knowledgeBaseDir": "/path/to/your/knowledge-base",
  "projectName": ""
}
```

`projectName` 为空时自动检测。

### 读取配置（所有子命令共用）

```bash
python3 - << 'PYEOF'
import os, json

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
project_config = os.path.join(project_root, ".claude", "kb-config.json")
global_config = os.path.expanduser("~/.claude/kb-config.json")

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

import re
project_name = re.sub(r'[^a-z0-9-]', '-', project_name.lower()).strip('-')

print(f"KB_DIR:{kb_dir}")
print(f"PROJECT:{project_name}")
PYEOF
```

---

## `init` — 初始化项目级配置

1. 检测项目根目录（有 `.git` 的最近祖先目录，或当前目录）
2. 若 `.claude/kb-config.json` 已存在，告知用户文件已存在，**直接跳过，不覆盖**
3. 创建配置文件：

```bash
python3 - << 'PYEOF'
import os, json

project_root = os.popen("git rev-parse --show-toplevel 2>/dev/null || pwd").read().strip()
config_dir = os.path.join(project_root, ".claude")
config_file = os.path.join(config_dir, "kb-config.json")

os.makedirs(config_dir, exist_ok=True)

import re
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

print(f"已创建: {config_file}")
print(f"projectName 自动检测为: {project_name}，如需修改请直接编辑文件")
PYEOF
```

4. 告知用户文件路径，提示可直接编辑 `knowledgeBaseDir` 和 `projectName`。

---

## `record` — 记录功能实现或项目变动

### 1. 读取配置（见上方共用代码）

### 2. 收集记录内容

如果对话已含足够上下文，直接提取；否则询问（合并为一个问题）：

- **标题**：简短名称，用于生成文件名 slug
- **类型**：`feature` / `bugfix` / `refactor` / `decision` / `setup` / `other`
- **描述**：做了什么，为什么
- **关键变动**：主要文件/函数/配置（可从对话自动整理）
- **技术决策**（可选）：选型理由、权衡
- **注意事项**（可选）：坑点、待办、链接
- **附件**（可选）：需要保存到附件目录的内容，支持：
  - 本地文件路径（复制到附件目录）
  - `接口文档` / `api-docs`（从对话或 openApiUrl 生成接口文档保存为 md）
  - `openapi`（保存 OpenAPI JSON 原始 spec）
  - 内容描述（Claude 生成对应文件保存）

### 3. 生成 slug

- 中文 → 英文意译（"用户登录" → `user-login`）
- 英文 → 小写 + 连字符（"fix login redirect" → `fix-login-redirect`）
- 无法确定时询问用户

### 4. 处理附件

如果用户提供了附件，先处理附件再写主文件。

附件目录：`{kb-dir}/{project}/{date_str}-{slug}/`（与主文件同名）

**附件类型处理：**

| 用户指定 | 处理方式 |
|---------|---------|
| 本地文件路径 | 复制到附件目录，保持原文件名 |
| `接口文档` / `api-docs` | 从对话上下文整理接口列表，生成 `api-docs.md`（包含接口名、路径、方法、参数、返回值） |
| `openapi` | 从 `.claude/apifox-sync.json` 的 `openApiUrl` 拉取 JSON，保存为 `openapi.json` |
| 内容描述 | Claude 生成对应内容，以合适文件名保存 |

```bash
python3 - << 'PYEOF'
import os, shutil

kb_dir = "..."
project = "..."
date_str = "..."
slug = "..."
attachment_files = []  # 已处理好、待保存的 (filename, content_or_src_path) 列表

attach_dir = os.path.join(kb_dir, project, f"{date_str}-{slug}")
os.makedirs(attach_dir, exist_ok=True)

for item in attachment_files:
    fname, src = item
    dst = os.path.join(attach_dir, fname)
    if os.path.isfile(src):
        shutil.copy2(src, dst)
    else:
        with open(dst, "w", encoding="utf-8") as f:
            f.write(src)  # src 为内容字符串
    print(f"附件: {fname}")
PYEOF
```

### 5. 写入主文件

```bash
python3 - << 'PYEOF'
import os, datetime

kb_dir = "..."
project = "..."
slug = "..."
title = "..."
entry_type = "..."
description = "..."
changes = "..."
decisions = "..."
notes = "..."
attachments = []  # [(filename, description), ...] 已保存的附件列表

now = datetime.datetime.now()
date_str = now.strftime("%Y-%m-%d")
datetime_str = now.strftime("%Y-%m-%d %H:%M")

target_dir = os.path.join(kb_dir, project)
os.makedirs(target_dir, exist_ok=True)

filename = f"{date_str}-{slug}.md"
target_file = os.path.join(target_dir, filename)

# 文件名冲突时加数字后缀
counter = 2
base_slug = slug
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
content = "\n\n".join(sections) + "\n"

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print(f"已记录到: {target_file}")
if attachments:
    print(f"附件目录: {date_str}-{slug}/")
PYEOF
```

---

## `open` — 读取知识库文件到会话

### 用法

```
/kb open 2026-03-09-user-login.md          # 精确文件名（当前项目）
/kb open user-login                         # 模糊匹配 slug（当前项目）
/kb open 2026-03-09                         # 列出当天所有文件（当前项目）
/kb open other-project/user-login           # 跨项目：{project}/{slug}
/kb open other-project/2026-03-09          # 跨项目：{project}/{date}
/kb open                                    # 列出当前项目最近文件
```

### 流程

1. 读取配置，确定 `kb_dir` 和默认 `project`
2. 解析参数，判断是否跨项目：
   - 参数含 `/` 且第一段不是日期格式 → 跨项目，`{project}/{query}` 拆分
   - 否则 → 当前项目
3. 执行查找：

```bash
python3 - << 'PYEOF'
import os, glob as glob_module

kb_dir = "..."
default_project = "..."
arg = "..."  # 用户传入参数，可能为空

# 跨项目：参数含 / 且首段非日期
if '/' in arg:
    parts = arg.split('/', 1)
    project = parts[0]
    query = parts[1]
else:
    project = default_project
    query = arg

project_dir = os.path.join(kb_dir, project)

if not os.path.isdir(project_dir):
    # 项目不存在，列出所有可用项目
    projects = [d for d in os.listdir(kb_dir) if os.path.isdir(os.path.join(kb_dir, d))]
    print(f"PROJECT_NOT_FOUND:{project}")
    print("AVAILABLE:" + ",".join(sorted(projects)))
else:
    # 精确文件名
    if query.endswith(".md"):
        matches = glob_module.glob(f"{project_dir}/{query}")
    # 日期前缀（YYYY-MM-DD）
    elif len(query) == 10 and query[4] == '-' and query[7] == '-':
        matches = glob_module.glob(f"{project_dir}/{query}-*.md")
    # slug 模糊匹配
    elif query:
        matches = glob_module.glob(f"{project_dir}/*{query}*.md")
    # 无参数：最近 10 个文件
    else:
        all_files = glob_module.glob(f"{project_dir}/*.md")
        matches = sorted(all_files, key=os.path.getmtime, reverse=True)[:10]

    matches = sorted(matches, key=os.path.getmtime, reverse=True)
    for f in matches:
        print(f"MATCH:{f}")
PYEOF
```

4. **单个匹配**：用 Read 工具读取内容，展示给用户
5. **多个匹配**：列出列表，让用户选择后读取
6. **无匹配**：
   - 当前项目无匹配 → 提示，并询问是否搜索其他项目
   - 项目名不存在 → 列出所有可用项目名供参考

---

## `search` — 全文搜索知识库

### 用法

```
/kb search jwt                        # 当前项目全文搜索
/kb search other-project/redis        # 跨项目搜索
/kb search jwt --all                  # 搜索所有项目
```

### 流程

1. 读取配置，确定 `kb_dir` 和默认 `project`
2. 解析参数：含 `/` 且首段非关键词 → 跨项目；`--all` → 搜索全部项目
3. 执行搜索：

```bash
python3 - << 'PYEOF'
import os, subprocess, json

kb_dir = "..."
project = "..."   # 当前项目，或跨项目指定的项目，或 None（--all）
keyword = "..."

if project:
    search_dir = os.path.join(kb_dir, project)
else:
    search_dir = kb_dir  # --all：搜索整个知识库

result = subprocess.run(
    ["grep", "-rl", "--include=*.md", "-i", keyword, search_dir],
    capture_output=True, text=True
)

files = [f for f in result.stdout.strip().split("\n") if f]

# 提取每个文件的标题行和匹配行
for fpath in files:
    with open(fpath) as f:
        lines = f.readlines()
    title = lines[0].strip().lstrip("# ") if lines else fpath
    hits = [l.strip() for l in lines if keyword.lower() in l.lower() and not l.startswith("#")]
    preview = hits[0][:80] if hits else ""
    rel = os.path.relpath(fpath, kb_dir)
    print(f"FILE:{rel}|TITLE:{title}|PREVIEW:{preview}")
PYEOF
```

4. 展示结果：

```
搜索 "jwt" 共找到 3 个文件：

  1. my-project/2026-03-01-jwt-auth.md
     用户认证重构 [refactor]
     "... 使用 jwt 替换 session，过期时间设为 7 天 ..."

  2. my-project/2026-02-10-login-sso.md
     SSO 登录接入 [feature]
     "... jwt token 验证逻辑在 AuthFilter 中 ..."
```

5. 询问用户是否打开某个文件，选择后用 Read 工具读入会话

---

## Quick Reference

| 场景 | 命令 |
|------|------|
| 首次在项目使用 | `/kb init` |
| 记录当前功能实现 | `/kb record` |
| 记录并附带接口文档 | `/kb record`（收集内容时指定附件：接口文档） |
| 记录并复制本地文件 | `/kb record`（附件指定本地文件路径） |
| 打开指定文件 | `/kb open 2026-03-09-user-login.md` |
| 模糊查找 | `/kb open user-login` |
| 查看某天的记录 | `/kb open 2026-03-09` |
| 查看最近记录 | `/kb open` |
| 跨项目打开 | `/kb open other-project/user-login` |
| 查看其他项目某天 | `/kb open other-project/2026-03-09` |
| 全文搜索当前项目 | `/kb search jwt` |
| 跨项目搜索 | `/kb search other-project/redis` |
| 搜索所有项目 | `/kb search jwt --all` |

## Common Mistakes

| 问题 | 解决 |
|------|------|
| slug 与已有文件冲突 | 自动加数字后缀（`-2.md`） |
| 路径含空格 | 用 Python 操作文件，避免 bash heredoc |
| open 找不到文件 | 检查 project 名是否与目录名一致，`/kb open` 列出可用项目 |
| 跨项目项目名不确定 | `/kb open` 无参数会提示所有可用项目名 |
