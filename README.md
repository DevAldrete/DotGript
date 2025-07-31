# 🔥 DotGript - The Sexy DevOps CLI That Actually Gets You

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Built with Typer](https://img.shields.io/badge/CLI-Typer-green.svg)](https://typer.tiangolo.com/)
[![Powered by PydanticAI](https://img.shields.io/badge/AI-PydanticAI-purple.svg)](https://ai.pydantic.dev/)

> **"Git workflows so smooth, your team will think you hired a DevOps wizard 🧙‍♂️"**

## 🚀 What is DotGript?

DotGript is the **ultimate DevOps CLI** designed for developers who are tired of Git drama, messy workflows, and spending more time configuring CI/CD than actually coding. It's your personal DevOps assistant that combines **enterprise-grade Git automations** with **AI-powered intelligence** to make your development life effortless.

### 🎯 Built for Sexy DevOps Developers Who Want:
- **Zero-Drama Git Workflows** - Smart automations that follow GitHub Flow, GitFlow, and enterprise best practices
- **AI-Powered Development** - Intelligent assistants with multiple personalities to help with docs, CI/CD, and IaC
- **Complete Git Replacement** - Enhanced Git commands with better UX and team-safe guardrails
- **Beautiful CLI Experience** - Rich terminal UI that doesn't make you cry

## ✨ Core Features

### 🤖 AI-Powered Development Assistant
- **Multiple AI Personalities**: From Geek 🤓 to Sarcastic Cat 😸, choose your vibe
- **Intelligent Code Analysis**: AI understands your project and suggests improvements
- **Documentation Generation**: Auto-generate docs, README files, and code comments
- **CI/CD Creation**: Smart pipeline generation for your tech stack
- **IaC Assistance**: Infrastructure as Code templates and best practices

### 🌊 Smart Git Workflows
- **Intelligent Branch Management**: Automated feature branches with naming conventions
- **Team-Safe Operations**: Built-in guardrails to prevent Git disasters
- **Conventional Commits**: Automated commit message formatting and validation
- **Smart Merging**: Conflict resolution with multiple strategies
- **Release Automation**: Semantic versioning and automated changelog generation

### 🎨 Enhanced Git Commands
- **Rich Terminal Output**: Beautiful, informative displays with syntax highlighting
- **Advanced Logging**: Enhanced git log with filtering, graphs, and statistics
- **Interactive Diffs**: Word-level diffs with context control
- **Smart Status**: Categorized file status with actionable insights
- **Powerful Search**: Author, date, and message filtering across history

### 🔧 Enterprise-Grade Automations
- **Multiple Workflow Support**: GitHub Flow, GitFlow, GitLab Flow, and custom workflows
- **Branch Protection**: Automatic protection for main/develop branches
- **Quality Gates**: Pre-commit hooks and automated testing integration
- **Team Collaboration**: PR/MR automation and review workflows

## 🛠️ Tech Stack

- **[Typer](https://typer.tiangolo.com/)** - Modern CLI framework with automatic help generation
- **[PydanticAI](https://ai.pydantic.dev/)** - Type-safe AI integration with multiple provider support
- **[Rich](https://rich.readthedocs.io/)** - Beautiful terminal output and interactive elements
- **[GitPython](https://gitpython.readthedocs.io/)** - Comprehensive Git repository manipulation
- **[Semver](https://python-semver.readthedocs.io/)** - Semantic versioning support
- **MCPs (Model Context Protocols)** - Extensible AI tool integration

## 🚀 Quick Start

### Installation

```bash
# Install with pip
pip install gript

# Or use uv (recommended)
uv add gript
```

### Basic Usage

```bash
# Initialize DotGript in your project
gript git init

# Create a new feature branch with smart naming
gript branches new "user-authentication" --issue-number 42

# Enhanced git log with filtering
gript git log --author "john@example.com" --since "1 week ago" --graph

# AI-powered assistance
gript ai ask "How do I set up CI/CD for a Python project?" --personality geek

# Smart feature completion
gript branches done feature/user-authentication --squash
```

## 📚 Command Reference

### 🤖 AI Commands (`gript ai`)

```bash
# Ask AI for help with different personalities
gript ai ask "Explain Docker best practices" --personality wizard
gript ai ask "Debug this error" --personality mom
gript ai ask "Optimize this code" --personality hater  # For brutal honesty

# Available personalities:
# geek, nasty, sexy, hater, bro, mom, corporate, sarcastic_cat,
# grandma, motivational_coach, wizard, zen_monk, vampire_roommate, cowboy
```

### 🌊 Smart Branch Management (`gript branches`)

```bash
# Create intelligent feature branches
gript branches new "payment-integration" --from-branch develop --interactive

# Finish features with smart merging
gript branches done feature/payment-integration --squash --delete-branch
```

### 🎯 Enhanced Git Operations (`gript git`)

```bash
# Advanced logging with Rich output
gript git log --max-count 20 --oneline --graph --since "2024-01-01"

# Detailed commit inspection
gript git show HEAD --show-stats

# Smart diff with word-level changes
gript git diff --word-diff --context-lines 5

# Interactive repository status
gript git status
```

## 🔧 Configuration

DotGript automatically creates a `.gript/` directory in your project with intelligent defaults:

```json
{
  "workflow_type": "github_flow",
  "branch_strategy": {
    "main_branch": "main",
    "feature_prefix": "feature/",
    "hotfix_prefix": "hotfix/"
  },
  "enforce_conventional_commits": true,
  "auto_squash_merge": true,
  "semantic_versioning": true,
  "ai_personality": "geek"
}
```

### Environment Variables

```bash
# AI Provider API Keys
export OPENAI_API_KEY="your-openai-key"
export OPENROUTER_API_KEY="your-openrouter-key"

# Git Configuration
export GRIPT_DEFAULT_BRANCH="main"
export GRIPT_WORKFLOW="github_flow"
```

## 🎨 AI Personalities

DotGript's AI comes with distinct personalities to match your mood and team culture:

- **🤓 Geek** - Caffeinated code enthusiast with sci-fi references
- **😈 Nasty** - Playful roasting while providing precise help
- **😘 Sexy** - Charming and flirty assistance (PG-13)
- **😠 Hater** - Brutally honest criticism with perfect solutions
- **💪 Bro** - High-energy tech-bro motivation
- **👵 Mom** - Caring guidance with gentle nagging
- **💼 Corporate** - Professional buzzword-filled responses
- **😸 Sarcastic Cat** - Languid feline wisdom with attitude
- **🧙‍♂️ Wizard** - Ancient coding magic and mystical guidance

## 🏗️ Advanced Features

### Smart Workflow Automation

```bash
# Automatic conventional commit formatting
gript git commit -m "Add user authentication system"
# → feat: add user authentication system

# Intelligent conflict resolution
gript git merge feature/new-api --strategy squash --auto-resolve

# Semantic version bumping
gript releases bump --type minor --auto-changelog
```

### AI-Powered Development

```bash
# Generate CI/CD pipeline
gript ai generate-pipeline --platform github-actions --language python

# Create Infrastructure as Code
gript ai generate-iac --provider aws --service lambda

# Code review assistance
gript ai review --files src/ --focus security
```

### Team Collaboration

```bash
# Smart PR creation
gript git push --create-pr --auto-assign-reviewers

# Branch hygiene
gript branches cleanup --delete-merged --older-than "2 weeks"

# Team workflow validation
gript validate-workflow --check-conventions --verify-tests
```

## 🤝 Integration Examples

### GitHub Actions Integration

```yaml
name: DotGript Workflow
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup DotGript
        run: pip install gript
      - name: Validate Workflow
        run: gript validate-workflow --strict
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: gript-validate
        name: DotGript Validation
        entry: gript validate-commit
        language: system
        stages: [commit-msg]
```

## 🎯 Why DotGript?

### Before DotGript:
```bash
git checkout -b feature/JIRA-123-fix-user-login-bug-from-issue-tracker
git add .
git commit -m "fixed stuff"  # 😱
git push origin feature/JIRA-123-fix-user-login-bug-from-issue-tracker
# Create PR manually, forget to add reviewers, merge conflicts everywhere
```

### After DotGript:
```bash
gript branches new "fix-user-login" --issue-number 123
# Smart commits with conventional format
gript git commit -m "Fix authentication timeout issue"
gript branches done feature/fix-user-login
# ✨ Automatic PR creation, reviewer assignment, clean merge
```

## 🔮 Roadmap

- **🎪 Team Dashboard** - Real-time workflow visualization
- **🤖 Advanced AI Models** - Custom fine-tuned models for code analysis
- **🔌 Plugin System** - Extensible architecture for custom automations
- **📊 Analytics** - Team productivity insights and metrics
- **🌐 Multi-Platform** - GitLab, Bitbucket, and Azure DevOps support
- **🎮 Interactive TUI** - Terminal UI for complex operations

## 🤝 Contributing

We welcome contributions from sexy DevOps developers! 

```bash
# Clone and setup
git clone https://github.com/DevAldrete/DotGript.git
cd DotGript
uv sync

# Run tests
uv run pytest

# Create feature branch
uv run gript branches new "awesome-feature"
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Typer** team for the amazing CLI framework
- **PydanticAI** for making AI integration type-safe and beautiful
- **Rich** for terminal output that doesn't suck
- **GitPython** maintainers for solid Git integration
- All the DevOps engineers who inspired us to build better tools

---

<div align="center">

**Made with ❤️ by DevOps engineers, for DevOps engineers**

[🌟 Star us on GitHub](https://github.com/DevAldrete/DotGript) | [📚 Documentation](https://dotgript.dev) | [💬 Community](https://discord.gg/dotgript)

*"Because life's too short for bad Git workflows"*

</div>
