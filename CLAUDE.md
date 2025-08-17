# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gitmit is a Python-based Git repository manager that uses AI (Google Gemini or Ollama) to generate standardized commit messages following GitFlow requirements. The project is built as a standalone CLI tool using PEX packaging.

## Development Commands

### Build and Install
```bash
# Build the PEX executable
python build.py

# The build creates: /tmp/gitmit/gitmit-{version}.pex
# Install to system (requires sudo)
sudo mv /tmp/gitmit/gitmit-{version}.pex /usr/local/bin/gitmit
sudo chmod +x /usr/local/bin/gitmit
```

### Development Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python -m src.gitmit [command]
```

### Code Formatting
The project uses Black formatter for Python code (configured in .vscode/settings.json). Format on save is enabled in VSCode.

## Architecture

### Core Structure
- **src/gitmit/**: Main application package
  - **llms/**: LLM integrations (Google Gemini, Ollama)
  - **services/**: Core services (config, database, git operations)
  - **tools/**: CLI command implementations (commit, init, update)
  - **utils/**: Terminal UI and argument parsing utilities
  - **resources/**: Type definitions and prompts for AI models

### Key Components

1. **GitService** (services/git.py): Wrapper around GitPython for repository operations
2. **Config Service** (services/config.py): Manages configuration from ~/.config/gitmit/config.ini
3. **Database Service** (services/database.py): MySQL connector for tracking token usage
4. **LLM Integration**: Abstract base class with Google and Ollama implementations

### Configuration Management
Configuration file at `~/.config/gitmit/config.ini` contains:
- LLM model settings (commit and optional resume models)
- API keys for Google Gemini
- Ollama server settings
- MySQL database connection for token tracking

## Git Workflow

The project follows GitFlow:
- **main**: Production-ready stable code
- **dev**: Integration branch for features
- **feature/name**: New features (from dev)
- **hotfix/x.x.x**: Urgent fixes (from main)
- **release/x.x.x**: New releases (from dev)

### Commit Message Format
```
:emoji: type(scope): Title

Description
```

Types include: feat, fix, bug, docs, style, refactor, perf, test, build, ci, chore, revert, dependencies, metadata, version, security, critical, review, other

## Dependencies

Key Python packages:
- GitPython==3.1.44 (Git operations)
- google-genai==1.9.0 (Google Gemini AI)
- ollama==0.4.7 (Local LLM support)
- mysql-connector-python==9.2.0 (Token tracking)
- rich==14.0.0 (Terminal UI)
- pex==2.33.7 (Executable packaging)

## Important Notes

- Token usage tracking requires MySQL database configuration
- The project version is maintained in `src/gitmit/__init__.py` as `__VERSION__`
- Build output goes to `/tmp/gitmit/` directory
- Configuration file has 600 permissions (user-only readable)
- Summarization feature (optional) prevents sharing full commit history with external AI