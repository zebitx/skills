# 技能开发指南

本文档面向贡献者，说明如何在本仓库创建和维护 Agent Skills。

## 什么是 Skill？

Skill 是一个包含 `SKILL.md` 的目录，文件内写有 YAML frontmatter 和 Markdown 指令。Claude 在运行时按需加载，用于提升特定任务的表现。

**Skill 适合用于：**
- 可复用的工作流程或操作规范
- 需要固定格式输出的任务（如生成配置文件）
- 跨项目通用的技术规范

**不适合放入 Skill：**
- 项目特定的约定（放入项目的 `CLAUDE.md`）
- 一次性的解决方案
- 可以用脚本/工具直接自动化的内容

---

## 目录结构规范

每个技能独占一个目录，放在 `skills/` 下：

```
skills/
└── my-skill/
    ├── SKILL.md          # 必须，技能主文件
    ├── scripts/          # 可选，辅助脚本
    ├── examples/         # 可选，输入/输出示例
    ├── templates/        # 可选，可复用模板
    └── reference/        # 可选，参考文档
```

---

## SKILL.md 格式

每个 `SKILL.md` 必须包含 YAML frontmatter：

```markdown
---
name: skill-name
description: Use when [触发条件]. Triggers on [触发词/短语].
---

# 技能标题

## 功能说明
简短描述这个技能做什么。

## 使用步骤
...
```

### frontmatter 字段说明

| 字段 | 要求 | 说明 |
|------|------|------|
| `name` | 必须 | kebab-case，仅含字母、数字、连字符 |
| `description` | 必须 | 以 "Use when..." 开头，描述触发条件，不超过 500 字符 |

### description 写法要点

- **只描述触发条件**，不要描述技能的执行流程
- 包含具体的触发词、场景和症状
- 写得"有力"一点，模糊的描述会导致技能无法被触发

```yaml
# 不好：描述了执行流程
description: Use when generating .gitignore - creates file with sections for each language

# 好：只描述触发条件
description: Use when asked to create or generate a .gitignore file. Triggers on "create .gitignore", "/gitignore".
```

---

## 编写规范

### 内容规范

- **长度**：`SKILL.md` 不超过 500 行
- **语气**：使用祈使句（"创建文件" 而不是 "你应该创建文件"）
- **说明原因**：解释规则背后的原因，让 Claude 能在边界情况下自行判断
- **一个好例子胜过多个平庸例子**

### 关键词覆盖

在文件中使用 Claude 可能搜索的词汇：
- 错误信息、症状描述
- 工具名称、命令名称
- 同义词（如 timeout/hang/freeze）

### 辅助文件使用原则

仅在以下情况创建辅助文件：

| 场景 | 做法 |
|------|------|
| 代码片段 < 50 行 | 直接内联在 `SKILL.md` |
| 可复用的脚本/工具 | 放入 `scripts/` |
| 参考文档 > 100 行 | 放入 `reference/` |
| 示例输入/输出 | 放入 `examples/` |

---

## 新建技能流程

**1. 复制模板**

```bash
cp -r template skills/my-skill
```

**2. 编辑 `SKILL.md`**

填写 frontmatter，编写指令内容。

**3. 更新 README**

在 README.md 的技能列表中添加一行。

**4. 提交**

```bash
git add skills/my-skill README.md
git commit -m "feat: add my-skill skill"
```

---

## Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>: <description>
```

| type | 用途 |
|------|------|
| `feat` | 新增技能 |
| `fix` | 修复技能内容错误 |
| `docs` | 更新文档 |
| `refactor` | 重构技能结构，不改变行为 |
| `chore` | 项目配置、模板等维护性改动 |

示例：
```
feat: add gitignore skill
fix: gitignore - add missing Go vendor directory
docs: update README usage section
```

---

## 参考资料

- [Agent Skills 官方规范](https://agentskills.io/specification)
- [技能规范说明](spec/agent-skills-spec.md)
- [Anthropic Skills 参考仓库](https://github.com/anthropics/skills)
