# Changelog

## v0.1.0 at 2025-04-03

- Initial release. See [README.md](README.md) for installation instructions.

## v0.2.0 at 2025-04-05

- [Change] Better "meaning" explanation for commit types;
- [Change] Prompt improvements.

## v0.2.1 at 2025-05-05

- [Fix] Parsing month for MySQL usage tracking.

## v0.3.0 at 2025-08-14

- [Changes] Commit command:
  - Add `--mode` option to auto set the commit mode: `manual` or `ai`;
  - Add `--brief` option to type a brief summary of the changes when using `ai` mode;
  - Add `--force` option to ignore all confirmations, including LLM confirmations.

## v0.4.0 at 2025-08-17

- [Add] Add `versioning` command;
- [Add] Add `merge` command.

## v0.5.0 at 2025-08-22

- [Add] Add `.gitmitignore` file to support to exclude files from commit prompt;
- [Add] Add `--no-feat` option to ignore `feat` commit type at commit prompt;
- [Changes] Commit prompt improvements.
