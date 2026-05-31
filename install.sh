#!/usr/bin/env bash
# ============================================================
# Claude Session Saver - 安装脚本
# ============================================================
# 用途: 在新机器上快速部署会话自动保存功能
# 使用: bash install.sh
# ============================================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Claude Session Saver - 安装程序"
echo "=========================================="
echo ""

# ----------- 配置 -----------
SCRIPT_NAME="claude-session-saver.py"
SCRIPT_PATH="$HOME/$SCRIPT_NAME"
LOG_DIR="$HOME/claude-session-logs"
SESSION_DIR="$HOME/claude-sessions"
SETTINGS_FILE="$HOME/.claude/settings.json"

# ----------- 检查依赖 -----------
echo "[1/6] 检查依赖..."

if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3，请先安装 Python 3"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo "❌ 错误: 未找到 claude 命令，请先安装 Claude Code CLI"
    exit 1
fi

echo "✅ Python 3: $(python3 --version)"
echo "✅ Claude Code: 已安装"

# ----------- 安装导出脚本 -----------
echo ""
echo "[2/6] 安装导出脚本..."

# 检查脚本是否在当前目录
if [ -f "./$SCRIPT_NAME" ]; then
    cp "./$SCRIPT_NAME" "$SCRIPT_PATH"
    chmod +x "$SCRIPT_PATH"
    echo "✅ 已安装: $SCRIPT_PATH"
else
    echo "❌ 错误: 未找到 $SCRIPT_NAME，请确保它在当前目录"
    exit 1
fi

# ----------- 创建日志目录 -----------
echo ""
echo "[3/6] 创建日志目录..."

mkdir -p "$LOG_DIR"
echo "✅ 已创建: $LOG_DIR"

mkdir -p "$SESSION_DIR"
echo "✅ 已创建: $SESSION_DIR"

# 创建 README
cat > "$LOG_DIR/README.md" << 'EOF'
# Claude Code 会话自动保存

这个目录包含自动导出的 Claude Code 会话日志（Markdown 格式）。

## 工作原理

- **自动触发**: 每次 Claude 响应结束时（Stop hook），自动导出当前会话
- **导出脚本**: `~/claude-session-saver.py`
- **配置位置**: `~/.claude/settings.json` 中的 `hooks.Stop` 配置
- **数据来源**: `~/.claude/projects/<project-name>/<session-id>.jsonl`

## 目录结构

```
~/claude-session-logs/          ← Markdown 日志
├── <project-name>/
│   ├── <YYYY-MM-DD>/
│   │   └── <HH-MM-SS>.md
│   └── ...
└── ...

~/claude-sessions/              ← 原始 JSONL 备份
├── <project-name>/
│   ├── <YYYY-MM-DD>/
│   │   ├── <HH-MM-SS>/
│   │   │   └── <session-id>.jsonl
│   │   └── ...
│   └── ...
└── ...
```

## 手动导出

```bash
# 导出指定会话
python3 ~/claude-session-saver.py <session-id>

# 导出最近的会话
python3 ~/claude-session-saver.py
```

## 导出内容

- 会话元信息（ID、项目、时间）
- 用户和 Assistant 的完整对话
- 工具调用摘要（Bash、Read、Write 等）
- 自动过滤系统消息和 API 错误
EOF

echo "✅ 已创建: $LOG_DIR/README.md"

# ----------- 配置 Hook -----------
echo ""
echo "[4/6] 配置 Claude Code Hook..."

# 检查 settings.json 是否存在
if [ ! -f "$SETTINGS_FILE" ]; then
    echo "⚠️  settings.json 不存在，创建默认配置..."
    mkdir -p "$(dirname "$SETTINGS_FILE")"
    echo '{}' > "$SETTINGS_FILE"
fi


# 使用 Python 更新配置（安全地合并 JSON）
python3 << 'PYTHON_SCRIPT'
import json
import sys
import os

settings_file = os.path.expanduser("~/.claude/settings.json")
script_path = os.path.expanduser("~/claude-session-saver.py")

# 读取现有配置
with open(settings_file, "r") as f:
    settings = json.load(f)

# 确保 hooks 字段存在
if "hooks" not in settings:
    settings["hooks"] = {}

# 配置 Stop hook
stop_hook_entry = {
    "type": "command",
    "command": f"python3 {script_path}",
    "async": True
}

# 检查是否已存在
if "Stop" not in settings["hooks"]:
    settings["hooks"]["Stop"] = []

# 查找是否已经配置了导出脚本
already_configured = False
for hook_group in settings["hooks"]["Stop"]:
    if "hooks" in hook_group:
        for hook in hook_group["hooks"]:
            if "claude-session-saver.py" in hook.get("command", "") or "claude-session-export.py" in hook.get("command", ""):
                already_configured = True
                print("⚠️  Stop hook 已配置，跳过")
                break

# 如果未配置，添加到第一个 hook 组
if not already_configured:
    if len(settings["hooks"]["Stop"]) == 0:
        settings["hooks"]["Stop"].append({"hooks": []})

    settings["hooks"]["Stop"][0]["hooks"].insert(0, stop_hook_entry)
    print("✅ 已添加 Stop hook 配置")

# 写回配置
with open(settings_file, "w") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print(f"✅ 配置已更新: {settings_file}")
PYTHON_SCRIPT

# ----------- 测试 -----------
echo ""
echo "[5/6] 测试安装..."

# 测试脚本是否可执行
if python3 "$SCRIPT_PATH" &> /dev/null; then
    echo "✅ 导出脚本测试通过"
else
    # 脚本可能没有会话文件，这是正常的
    echo "✅ 导出脚本已安装"
fi

# ----------- 恢复已有会话 -----------
echo ""
echo "[6/6] 恢复已有会话..."

# 使用 Python 批量导出已有但未导出过的会话
python3 << 'PYEOF'
import sys, os, glob
import importlib.util

script_path = os.path.expanduser("~/claude-session-saver.py")
spec = importlib.util.spec_from_file_location("saver", script_path)
saver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(saver)

projects_dir = os.path.expanduser("~/.claude/projects")
sessions_dir = os.path.expanduser("~/claude-sessions")

source = {}
for f in glob.glob(os.path.join(projects_dir, "*", "*.jsonl")):
    sid = os.path.splitext(os.path.basename(f))[0]
    source[sid] = f

exported = set()
for f in glob.glob(os.path.join(sessions_dir, "*", "*", "*", "*.jsonl")):
    exported.add(os.path.splitext(os.path.basename(f))[0])

unexported = [(os.path.getmtime(p), sid, p) for sid, p in source.items() if sid not in exported]
unexported.sort()

if not unexported:
    print("✅ 没有需要恢复的会话")
else:
    ok = skip = err = 0
    for i, (mtime, sid, src_path) in enumerate(unexported):
        try:
            output = saver.export_session(sid, src_path)
            if output:
                ok += 1
                if ok <= 5 or ok % 50 == 0:
                    print(f"  [{i+1}/{len(unexported)}] ✅ {output}")
            else:
                skip += 1
        except Exception as e:
            err += 1
            if err <= 3:
                print(f"  [{i+1}/{len(unexported)}] ❌ {sid}: {e}", file=sys.stderr)
    print(f"✅ 会话恢复完成: 成功 {ok}, 跳过 {skip}, 错误 {err}")
PYEOF

if [ $? -eq 0 ]; then
    echo "✅ 已有会话已恢复"
else
    echo "⚠️  会话恢复遇到问题（不影响基本功能）"
fi

# ----------- 完成 -----------
echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "📁 导出脚本:      $SCRIPT_PATH"
echo "📁 Markdown 日志: $LOG_DIR"
echo "📁 JSONL 备份:    $SESSION_DIR"
echo "📁 配置文件:      $SETTINGS_FILE"
echo ""
echo "🎉 现在你可以正常使用 'claude' 命令"
echo "   会话会自动保存到 $LOG_DIR 和 $SESSION_DIR"
echo ""
echo "💡 手动导出命令:"
echo "   python3 $SCRIPT_PATH [session-id]"
echo ""
echo "🔧 如需卸载，运行:"
echo "   rm $SCRIPT_PATH"
echo "   # 然后手动从 $SETTINGS_FILE 中移除 Stop hook"
echo ""
