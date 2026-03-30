---
name: gitignore
description: Use when the user asks to create or generate a .gitignore file, or asks to initialize a project's git ignore rules. Triggers on "create .gitignore", "generate gitignore", "add gitignore", "init gitignore", "/gitignore". Covers Java, Go, Python, JavaScript/Node.js, macOS, Windows, Linux, and common IDEs/editors.
---

# .gitignore Generator

Generate a comprehensive `.gitignore` file covering multi-language projects.

## Instructions

When triggered, create a `.gitignore` file in the project root with the template below. If the project clearly uses only specific languages, you may omit irrelevant sections — but when in doubt, keep everything.

## Template

Write the following content to `.gitignore`:

```gitignore
# ===========================
# Operating Systems
# ===========================

# macOS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
.AppleDouble
.LSOverride
Icon?
.AppleDB
.AppleDesktop
Network Trash Folder
Temporary Items
.apdisk

# Windows
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db
Desktop.ini
$RECYCLE.BIN/
*.lnk
*.stackdump

# Linux
*~
.fuse_hidden*
.directory
.Trash-*
.nfs*

# ===========================
# IDEs & Editors
# ===========================

# JetBrains (IntelliJ, GoLand, PyCharm, WebStorm, etc.)
.idea/
*.iml
*.iws
*.ipr
out/
.idea_modules/

# VS Code
.vscode/
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
*.code-workspace
.history/

# Eclipse
.classpath
.project
.settings/
.factorypath
bin/
tmp/
*.tmp
*.bak
*.swp
*~.nib

# Vim / Neovim
[._]*.s[a-v][a-z]
!*.svg
[._]*.sw[a-p]
[._]s[a-rt-v][a-z]
[._]ss[a-gi-z]
[._]sw[a-p]
Session.vim
Sessionx.vim
.netrwhist
tags
[._]*.un~

# ===========================
# Java
# ===========================

*.class
*.jar
*.war
*.ear
*.nar
*.rar
*.zip
*.tar.gz
*.tar.bz2
hs_err_pid*
replay_pid*

# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml
buildNumber.properties
.mvn/timing.properties
.mvn/wrapper/maven-wrapper.jar

# Gradle
.gradle/
build/
!gradle/wrapper/gradle-wrapper.jar
!**/src/main/**/build/
!**/src/test/**/build/
gradle-app.setting
.gradletasknamecache

# Spring Boot
HELP.md
.sts4-cache/

# ===========================
# Go
# ===========================

# Binaries
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary
*.test

# Output of go build
/dist/

# Go workspace
go.work
go.work.sum

# Vendor (uncomment if not committing vendor)
# vendor/

# Coverage output
*.out
coverage.html

# ===========================
# Python
# ===========================

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.python-version
.pyenv/
.pdm.toml
.pdm-python
.pdm-build/
__pypackages__/

# Testing
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/
htmlcov/

# Type checkers
.mypy_cache/
.dmypy.json
dmypy.json
.pyre/
.pytype/
cython_debug/

# Jupyter
.ipynb_checkpoints
*/.ipynb_checkpoints/*
profile_default/
ipython_config.py

# uv / pip
.uv/

# ===========================
# JavaScript / Node.js
# ===========================

# Dependencies
node_modules/
jspm_packages/
bower_components/

# Build output
dist/
build/
out/
.next/
.nuxt/
.vuepress/dist
.serverless/
.fusebox/
.dynamodb/
.tern-port

# Cache
.npm
.eslintcache
.stylelintcache
.cache
.parcel-cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/
.temp/
.docusaurus

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*
report.[0-9]*.[0-9]*.[0-9]*.[0-9]*.json

# Runtime
pids/
*.pid
*.seed
*.pid.lock
lib-cov/
coverage/
.nyc_output/

# Lock files (choose one to keep, ignore others if needed)
# yarn.lock
# package-lock.json
# pnpm-lock.yaml

# TypeScript
*.tsbuildinfo

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# ===========================
# Secrets & Credentials
# ===========================

.env*
!.env.example
!.env.template
*.pem
*.key
*.p12
*.pfx
secrets/
credentials/
config/secrets.*

# ===========================
# Misc
# ===========================

# Temporary files
*.tmp
*.temp
*.swp
*.swo

# Compiled source
*.com
*.class
*.dll
*.exe
*.o
*.so

# Archives
*.7z
*.dmg
*.gz
*.iso
*.jar
*.rar
*.tar
*.zip
```

## After Creating

Tell the user:
- Which sections are included
- That `.env.example` / `.env.template` are intentionally **not** ignored (safe to commit as templates)
- Suggest they review the lock file section (`yarn.lock`, `package-lock.json`, `pnpm-lock.yaml`) — typically **one** should be committed, not ignored
