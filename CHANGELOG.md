# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
