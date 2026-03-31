---
name: kb
description: 'Use when the user wants to record, open, search, or manage a knowledge base of feature implementations and project changes. Triggers on "/kb record", "/kb open", "/kb search", "/kb init", phrases like "记录到知识库", "save to knowledge base", "读取知识库", "搜索知识库", "log this change", "记录这次实现".'
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
| `/kb init` | 在当前项目创建 `.claude/skills/kb/kb-config.json` |
| `/kb record` | 将当前会话的功能实现或变动记录到知识库 |
| `/kb open [filename]` | 将知识库中的文件读入当前会话，支持跨项目 |
| `/kb search <keyword>` | 全文搜索知识库内容，支持跨项目 |

**收到 `/kb` 命令时，先读取第一个参数判断子命令，再执行对应流程。**

---

## Config Files（优先级从高到低）

1. **项目级**：`{project-root}/.claude/skills/kb/kb-config.json` — `init` 创建，优先使用
2. **全局**：`~/.claude/skills/kb/kb-config.json` — 全局默认

```json
{
  "knowledgeBaseDir": "/path/to/your/knowledge-base",
  "projectName": ""
}
```

`projectName` 为空时自动检测。

---

## Skill Dir Resolution（所有子命令共用）

执行任何脚本前，先找到技能安装目录：

```bash
KB_SKILL_DIR=$(python3 -c "
import os
for p in ['.claude/skills/kb', os.path.expanduser('~/.claude/skills/kb')]:
    if os.path.isdir(p): print(os.path.abspath(p)); break
")
```

---

## 读取配置（所有子命令共用）

```bash
output=$(python3 "$KB_SKILL_DIR/scripts/config.py")
KB_DIR=$(echo "$output" | grep '^KB_DIR:' | cut -d: -f2-)
PROJECT=$(echo "$output" | grep '^PROJECT:' | cut -d: -f2-)
```

---

## `init` — 初始化项目级配置

```bash
python3 "$KB_SKILL_DIR/scripts/init.py"
```

输出 `CREATED:<path>` 或 `EXISTS:<path>`。

- 输出 `CREATED`：告知用户文件路径，提示可直接编辑 `knowledgeBaseDir` 和 `projectName`
- 输出 `EXISTS`：告知用户文件已存在，跳过，不覆盖

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

### 4. 处理附件（如有）

| 用户指定 | 处理方式 |
|---------|---------|
| 本地文件路径 | 复制到附件目录，保持原文件名 |
| `接口文档` / `api-docs` | 从对话上下文整理接口列表，生成 `api-docs.md` |
| `openapi` | 从 `.claude/apifox-sync.json` 的 `openApiUrl` 拉取 JSON，保存为 `openapi.json` |
| 内容描述 | Claude 生成对应内容，以合适文件名保存 |

```bash
python3 "$KB_SKILL_DIR/scripts/copy_attachments.py" << 'EOF'
{
  "kb_dir": "<KB_DIR>",
  "project": "<PROJECT>",
  "date_str": "<YYYY-MM-DD>",
  "slug": "<slug>",
  "attachments": [["filename.md", "/src/path/or/content"]]
}
EOF
```

### 5. 写入主文件

```bash
python3 "$KB_SKILL_DIR/scripts/write_record.py" << 'EOF'
{
  "kb_dir": "<KB_DIR>",
  "project": "<PROJECT>",
  "slug": "<slug>",
  "title": "<标题>",
  "entry_type": "<feature|bugfix|refactor|decision|setup|other>",
  "description": "<描述>",
  "changes": "<关键变动>",
  "decisions": "<技术决策>",
  "notes": "<注意事项>",
  "attachments": [["filename.md", "附件描述"]]
}
EOF
```

输出 `CREATED:<filepath>`，告知用户记录已保存的路径。

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

1. 读取配置，确定 `KB_DIR` 和默认 `PROJECT`
2. 执行查找：

```bash
python3 "$KB_SKILL_DIR/scripts/open.py" "$KB_DIR" "$PROJECT" "<arg>"
```

3. **单个匹配**：用 Read 工具读取内容，展示给用户
4. **多个匹配**：列出列表，让用户选择后读取
5. **无匹配**：
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

1. 读取配置，确定 `KB_DIR` 和默认 `PROJECT`
2. 解析参数：含 `/` 且首段非关键词 → 跨项目；`--all` → 搜索全部项目
3. 执行搜索：

```bash
# 当前项目
python3 "$KB_SKILL_DIR/scripts/search.py" "$KB_DIR" "$PROJECT" "<keyword>"

# 跨项目
python3 "$KB_SKILL_DIR/scripts/search.py" "$KB_DIR" "<other-project>" "<keyword>"

# 所有项目
python3 "$KB_SKILL_DIR/scripts/search.py" "$KB_DIR" "$PROJECT" "<keyword>" --all
```

4. 展示结果：

```
搜索 "jwt" 共找到 3 个文件：

  1. my-project/2026-03-01-jwt-auth.md
     用户认证重构 [refactor]
     "... 使用 jwt 替换 session，过期时间设为 7 天 ..."
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
| 全文搜索当前项目 | `/kb search jwt` |
| 跨项目搜索 | `/kb search other-project/redis` |
| 搜索所有项目 | `/kb search jwt --all` |

## Common Mistakes

| 问题 | 解决 |
|------|------|
| slug 与已有文件冲突 | `write_record.py` 自动加数字后缀（`-2.md`） |
| 路径含空格 | 脚本用 Python 操作文件，无此问题 |
| open 找不到文件 | 检查 project 名是否与目录名一致，`/kb open` 列出可用项目 |
| 跨项目项目名不确定 | `/kb open` 无参数会提示所有可用项目名 |
