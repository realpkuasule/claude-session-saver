#!/usr/bin/env python3
"""
claude-session-saver.py
=======================
将 Claude Code 的会话 JSONL 文件转换为可读的 Markdown 格式。
用法:
  1. 作为 Stop hook 自动调用（从 stdin 读取 hook JSON，提取 session_id）
  2. 手动调用: python3 claude-session-saver.py [session_id]

输出目录: ~/claude-session-logs/<session_id>/conversation.md
"""

import json
import os
import re
import sys
import glob
from pathlib import Path
from datetime import datetime

# ----------- 配置 -----------
LOG_ROOT = os.path.expanduser("~/claude-session-logs")
CLAUDE_PROJECTS_DIR = os.path.expanduser("~/.claude/projects")


def find_session_file(session_id: str) -> str | None:
    """在所有项目目录中查找指定 session_id 的 JSONL 文件。"""
    pattern = os.path.join(CLAUDE_PROJECTS_DIR, "*", f"{session_id}.jsonl")
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    return None


def find_latest_session_file() -> tuple[str | None, str | None]:
    """找到最近修改的会话 JSONL 文件，返回 (文件路径, session_id)。"""
    pattern = os.path.join(CLAUDE_PROJECTS_DIR, "*", "*.jsonl")
    all_files = glob.glob(pattern)
    if not all_files:
        return None, None

    # 按修改时间排序，取最新的
    latest = max(all_files, key=os.path.getmtime)
    session_id = Path(latest).stem
    return latest, session_id


def get_session_id_from_stdin() -> str | None:
    """尝试从 hook 的 stdin JSON 中提取 session_id。"""
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read().strip()
            if data:
                hook_input = json.loads(data)
                # Stop hook 可能在不同字段中包含 session_id
                sid = (
                    hook_input.get("session_id")
                    or hook_input.get("sessionId")
                    or hook_input.get("session", {}).get("id")
                )
                return sid
    except (json.JSONDecodeError, AttributeError, KeyError):
        pass
    return None


def parse_session_jsonl(filepath: str) -> list[dict]:
    """解析会话 JSONL 文件，提取有意义的消息条目。"""
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            rec_type = record.get("type")

            # 只处理 user 和 assistant 消息
            if rec_type not in ("user", "assistant"):
                continue

            message = record.get("message", {})
            role = message.get("role", "")
            timestamp = record.get("timestamp", "")
            is_meta = record.get("isMeta", False)
            content = message.get("content", "")

            # 跳过元消息（系统注入的 caveat 等）
            if is_meta:
                continue

            # 提取文本内容
            text_parts = []
            tool_uses = []

            if isinstance(content, str):
                # 跳过系统注入的消息
                if content.startswith("<local-command"):
                    continue
                if content.startswith("<command-name>/"):
                    continue
                # 跳过 system-reminder 标签包裹的消息
                if content.strip().startswith("<system-reminder>"):
                    continue
                # 清理内容中的 system-reminder 标签
                cleaned = re.sub(
                    r"<system-reminder>.*?</system-reminder>",
                    "",
                    content,
                    flags=re.DOTALL,
                ).strip()
                if not cleaned:
                    continue
                text_parts.append(cleaned)
            elif isinstance(content, list):
                is_tool_result = False
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        if text:
                            text_parts.append(text)
                    elif item.get("type") == "tool_use":
                        tool_name = item.get("name", "unknown")
                        tool_input = item.get("input", {})
                        tool_uses.append({
                            "name": tool_name,
                            "input": tool_input,
                        })
                    elif item.get("type") == "tool_result":
                        is_tool_result = True
                if is_tool_result and not text_parts:
                    continue  # 纯工具结果消息，跳过

            # 如果既没有文本也没有工具调用，跳过
            if not text_parts and not tool_uses:
                continue

            # 过滤 API 错误消息（如 502 Bad Gateway）
            combined_text = "\n\n".join(text_parts)
            if role == "assistant" and re.match(
                r"^API Error: \d{3}\b", combined_text
            ):
                continue

            entry = {
                "role": role,
                "timestamp": timestamp,
                "text": combined_text,
                "tool_uses": tool_uses,
            }
            entries.append(entry)

    return entries


def format_timestamp(ts) -> str:
    """将时间戳转换为可读格式。"""
    if not ts:
        return ""
    try:
        if isinstance(ts, str):
            # ISO format
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        elif isinstance(ts, (int, float)):
            # Unix timestamp in milliseconds
            dt = datetime.fromtimestamp(ts / 1000)
        else:
            return ""
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return ""


def merge_consecutive_entries(entries: list[dict]) -> list[dict]:
    """合并连续的同角色消息（Claude 可能分多条发送）。"""
    if not entries:
        return []

    merged = [entries[0].copy()]
    for entry in entries[1:]:
        last = merged[-1]
        if entry["role"] == last["role"]:
            # 如果是完全相同的用户消息（重试导致），跳过
            if entry["role"] == "user" and entry["text"] == last["text"]:
                continue
            # 合并文本
            if entry["text"]:
                if last["text"]:
                    last["text"] += "\n\n" + entry["text"]
                else:
                    last["text"] = entry["text"]
            # 合并工具调用
            last["tool_uses"].extend(entry["tool_uses"])
        else:
            merged.append(entry.copy())

    return merged


def entries_to_markdown(entries: list[dict], session_id: str, session_file: str) -> str:
    """将解析后的消息条目转换为 Markdown 格式。"""
    # 获取会话的项目名
    project_dir = Path(session_file).parent.name
    # 获取会话时间范围
    first_ts = entries[0]["timestamp"] if entries else ""
    last_ts = entries[-1]["timestamp"] if entries else ""

    lines = []
    lines.append("# Claude 会话日志")
    lines.append("")
    lines.append(f"> **会话 ID**: `{session_id}`")
    lines.append(f"> **项目**: `{project_dir}`")
    if first_ts:
        lines.append(f"> **开始时间**: {format_timestamp(first_ts)}")
    if last_ts:
        lines.append(f"> **最后更新**: {format_timestamp(last_ts)}")
    lines.append(f"> **自动导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    for entry in entries:
        lines.append("---")
        lines.append("")

        if entry["role"] == "user":
            lines.append("## User")
        else:
            lines.append("## Assistant")

        lines.append("")

        # 文本内容
        if entry["text"]:
            lines.append(entry["text"])
            lines.append("")

        # 工具调用摘要
        if entry["tool_uses"]:
            for tool in entry["tool_uses"]:
                name = tool["name"]
                inp = tool["input"]
                if name == "Bash":
                    cmd = inp.get("command", "")
                    desc = inp.get("description", "")
                    label = desc if desc else cmd[:80]
                    lines.append(f"> **Tool**: `Bash` - {label}")
                elif name == "Read":
                    lines.append(f"> **Tool**: `Read` - {inp.get('file_path', '?')}")
                elif name == "Write":
                    lines.append(f"> **Tool**: `Write` - {inp.get('file_path', '?')}")
                elif name == "Edit":
                    lines.append(f"> **Tool**: `Edit` - {inp.get('file_path', '?')}")
                elif name in ("Grep", "Glob"):
                    lines.append(f"> **Tool**: `{name}` - {inp.get('pattern', '?')}")
                elif name == "Agent":
                    lines.append(f"> **Tool**: `Agent` - {inp.get('description', '?')}")
                else:
                    lines.append(f"> **Tool**: `{name}`")
            lines.append("")

    return "\n".join(lines)


def export_session(session_id: str, session_file: str) -> str:
    """导出一个会话为 Markdown 文件，返回输出文件路径。"""
    # 解析会话
    entries = parse_session_jsonl(session_file)
    if not entries:
        return ""

    # 合并连续消息
    entries = merge_consecutive_entries(entries)

    # 转为 Markdown
    md_content = entries_to_markdown(entries, session_id, session_file)

    # 写入文件
    session_dir = os.path.join(LOG_ROOT, session_id)
    os.makedirs(session_dir, exist_ok=True)
    output_file = os.path.join(session_dir, "conversation.md")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    return output_file


def main():
    session_id = None
    session_file = None

    # 优先级 1: 命令行参数
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
        session_file = find_session_file(session_id)
        if not session_file:
            print(f"Error: Session file not found for {session_id}", file=sys.stderr)
            sys.exit(1)

    # 优先级 2: 从 stdin (hook input) 获取
    if not session_id:
        session_id = get_session_id_from_stdin()
        if session_id:
            session_file = find_session_file(session_id)

    # 优先级 3: 使用最近修改的会话文件
    if not session_file:
        session_file, session_id = find_latest_session_file()

    if not session_file or not session_id:
        print("Error: No session file found", file=sys.stderr)
        sys.exit(1)

    output = export_session(session_id, session_file)
    if output:
        print(f"Exported: {output}", file=sys.stderr)
    else:
        print(f"No conversation entries found in session {session_id}", file=sys.stderr)


if __name__ == "__main__":
    main()
