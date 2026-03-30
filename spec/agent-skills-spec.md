# Agent Skills Specification

Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks.

## Official Specification

See the full specification at: https://agentskills.io/specification

## Quick Reference

### Required Structure

Every skill must have a `SKILL.md` file:

```
skills/<skill-name>/
└── SKILL.md          # Required
```

### SKILL.md Format

```markdown
---
name: skill-name          # kebab-case, must be unique
description: When and why to trigger this skill. Be specific and "pushy".
---

# Skill instructions here
```

### Optional Directories

```
skills/<skill-name>/
├── SKILL.md
├── scripts/          # Helper scripts (Python, shell, etc.)
├── examples/         # Example inputs/outputs
├── templates/        # Reusable templates
└── reference/        # Reference docs, guides, specs
```

## Authoring Guidelines

- **Length**: Keep `SKILL.md` under 500 lines
- **Style**: Imperative form ("Do X" not "You should do X")
- **Why**: Explain reasoning behind instructions so Claude can adapt in edge cases
- **Description**: Make it specific and "pushy" — vague descriptions cause undertriggering
- **Testing**: Validate by running with/without the skill and comparing output quality
