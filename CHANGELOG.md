# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2026-05-31

### Fixed
- Fix `npx claude-session-saver` failing to locate companion `.py` files
- Add Node.js wrapper (`cli.js`) as `bin` entry for reliable package directory resolution

## [1.0.1] - 2026-05-31

### Added
- JSONL session backup to `~/claude-sessions/` directory
- Auto session restore step in install.sh (step 6/6)
- `batch_restore.py` utility for bulk exporting unexported sessions

### Changed
- Updated install.sh README with correct directory structure
- Updated Python docstring to reflect actual output paths

### Fixed
- Removed obsolete `~/.claude/settings.json` backup from install.sh

## [1.0.0] - 2026-03-13

### Added
- Initial release
- Automatic session export via Claude Code Stop hook
- Markdown format output with conversation history
- Smart filtering of system messages, API errors, and duplicates
- Tool call summaries (Bash, Read, Write, Edit, Grep, Glob, Agent)
- Support for manual export by session ID
- Automatic detection of latest session
- Installation script with dependency checking
- Configuration backup before modification
- Comprehensive documentation

### Features
- Zero token consumption (reads local JSONL files)
- Async execution (doesn't block Claude responses)
- Automatic deduplication of repeated user messages
- Merging of consecutive messages from same role
- Timestamp formatting for session metadata
- Project-aware session organization

### Documentation
- README with installation and usage instructions
- LICENSE (MIT)
- CHANGELOG
- Inline code documentation
