# Claude Session Saver

自动保存 Claude Code 会话为 Markdown 格式的工具。

## ✨ 功能特性

- 🔄 **自动保存**: 每次 Claude 响应结束时自动导出会话
- 📝 **Markdown 格式**: 易读易搜索的格式
- 🧹 **智能过滤**: 自动过滤系统消息、API 错误、重复内容
- 🛠️ **工具摘要**: 记录 Bash、Read、Write 等工具调用
- 💰 **零 Token 消耗**: 不调用 API，只读取本地文件
- ⚡ **异步执行**: 不影响 Claude 响应速度

## 📋 系统要求

- Python 3.6+
- Claude Code CLI (已安装并可用)
- 操作系统: Linux / macOS / WSL

## 🚀 快速安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/claude-session-saver.git
cd claude-session-saver

# 运行安装脚本
bash install.sh
```

安装脚本会自动：
- ✅ 检查依赖（Python 3、Claude Code）
- ✅ 安装脚本到 `~/claude-session-saver.py`
- ✅ 创建日志目录 `~/claude-session-logs/`
- ✅ 配置 Claude Code Stop hook
- ✅ 备份原有配置

## 📖 使用方法

### 自动保存（推荐）

安装后，正常使用 `claude` 命令即可：

```bash
claude
# 对话会自动保存到 ~/claude-session-logs/
```

### 手动导出

```bash
# 导出指定会话
python3 ~/claude-session-saver.py <session-id>

# 导出最近的会话
python3 ~/claude-session-saver.py
```

### 查看已保存的会话

```bash
# 列出所有会话
ls ~/claude-session-logs/

# 查看某个会话
cat ~/claude-session-logs/<session-id>/conversation.md

# 搜索会话内容
grep -r "关键词" ~/claude-session-logs/
```

## 📁 输出格式

每个会话保存为独立的 Markdown 文件：

```
~/claude-session-logs/
├── <session-id-1>/
│   └── conversation.md
├── <session-id-2>/
│   └── conversation.md
└── README.md
```

Markdown 文件包含：
- 会话元信息（ID、项目、时间）
- 用户和 Assistant 的完整对话
- 工具调用摘要
- 自动过滤的内容：
  - 系统注入的消息（`<system-reminder>` 等）
  - API 错误消息（502 Bad Gateway 等）
  - 重复的用户消息（重试导致）

## 🔧 工作原理

```
Claude 响应结束
    ↓
Stop Hook 触发
    ↓
claude-session-saver.py 执行
    ↓
读取 ~/.claude/projects/<project>/<session-id>.jsonl
    ↓
解析并过滤消息
    ↓
转换为 Markdown
    ↓
保存到 ~/claude-session-logs/<session-id>/conversation.md
```

## 🛠️ 故障排除

### 问题 1: 没有生成日志文件

```bash
# 1. 确认 hook 配置正确
cat ~/.claude/settings.json | grep -A5 "Stop"

# 2. 手动运行导出脚本测试
python3 ~/claude-session-saver.py

# 3. 检查 Claude Code 版本
claude --version
```

### 问题 2: Python 版本过低

```bash
# 检查 Python 版本（需要 3.6+）
python3 --version
```

### 问题 3: 权限问题

```bash
# 确保脚本有执行权限
chmod +x ~/claude-session-saver.py

# 确保日志目录可写
chmod 755 ~/claude-session-logs
```

## 🗑️ 卸载

```bash
# 1. 删除导出脚本
rm ~/claude-session-saver.py

# 2. 删除日志目录（可选）
rm -rf ~/claude-session-logs

# 3. 恢复配置备份
cp ~/.claude/settings.json.backup.* ~/.claude/settings.json
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可

MIT License

## 🔗 相关链接

- [Claude Code 官方文档](https://docs.anthropic.com/claude/docs/claude-code)
- [Claude API 文档](https://docs.anthropic.com/)

---

**版本**: 1.0.0
**更新日期**: 2026-03-13
**兼容**: Claude Code 2.1.71+
