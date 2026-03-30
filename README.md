# AI Agent Skills

A collection of skills for Claude Code and Claude AI — reusable instruction sets that load dynamically to improve Claude's performance on specialized tasks.

## What Are Skills?

Skills are folders containing a `SKILL.md` file with YAML frontmatter and markdown instructions. Claude loads them on demand to handle specific workflows better than it would with general instructions alone.

## Skills

| Skill | Description |
|-------|-------------|
| [gitignore](skills/gitignore/SKILL.md) | Generate a comprehensive `.gitignore` covering Java, Go, Python, JS/Node.js, macOS, Windows, Linux, and common IDEs |

## Usage

### Claude Code

Install via the plugin marketplace or reference this repo directly:

```
/plugin marketplace add <your-github-username>/skills
```

Or add skills manually to your Claude Code configuration.

### Structure

Each skill lives in its own directory under `skills/`:

```
skills/
└── my-skill/
    ├── SKILL.md          # Required: instructions + frontmatter
    ├── scripts/          # Optional: helper scripts
    ├── examples/         # Optional: input/output examples
    ├── templates/        # Optional: reusable templates
    └── reference/        # Optional: reference docs
```

## Creating a New Skill

Copy the template:

```bash
cp -r template skills/my-skill
```

Edit `skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: Clear description of when and why to use this skill.
---

# My Skill

Instructions here...
```

See [spec/agent-skills-spec.md](spec/agent-skills-spec.md) for the full authoring guide.

## Reference

- [Official Skills Specification](https://agentskills.io/specification)
- [Anthropic Skills Reference](https://github.com/anthropics/skills)

## License

MIT
