# AI Agent Skills

一个开源的 Claude Agent Skills 集合，提供可复用的指令集，让 Claude 在专项任务上表现更好。

## 技能列表

| 技能 | 描述 |
|------|------|
| [gitignore](skills/gitignore/SKILL.md) | 生成覆盖 Java、Go、Python、JS/Node.js、macOS、Windows 的 `.gitignore` |

## 如何使用

### 方式一：通过 Claude Code 插件市场安装

```bash
/plugin marketplace add zebitx/skills
```

安装后，在对话中直接描述你的需求，Claude 会自动加载对应技能。

### 方式二：手动配置

将 `skills/` 目录下的技能文件复制到你的 Claude Code 配置目录：

```
~/.claude/skills/<skill-name>/SKILL.md
```

### 方式三：直接引用

在 `CLAUDE.md` 中通过 `@` 语法引用技能文件：

```markdown
@skills/gitignore/SKILL.md
```

## 触发技能

技能会根据你的自然语言描述自动触发，也支持 `/skill-name` 形式调用：

| 技能 | 触发示例 |
|------|---------|
| gitignore | `帮我生成 .gitignore`、`create .gitignore`、`/gitignore` |

## 项目结构

```
skills/
├── README.md               # 本文档
├── CLAUDE.md               # 贡献规范与技能开发指南
├── template/
│   └── SKILL.md            # 新技能模板
├── spec/
│   └── agent-skills-spec.md  # 技能规范说明
└── skills/
    └── <skill-name>/
        ├── SKILL.md        # 技能主文件（必须）
        ├── scripts/        # 辅助脚本（可选）
        ├── examples/       # 示例（可选）
        ├── templates/      # 模板文件（可选）
        └── reference/      # 参考文档（可选）
```

## 参考资料

- [Agent Skills 官方规范](https://agentskills.io/specification)
- [Anthropic Skills 参考仓库](https://github.com/anthropics/skills)

## License

MIT
