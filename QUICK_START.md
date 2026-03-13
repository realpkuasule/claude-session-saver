# 快速开始

## 🚀 一键安装

```bash
git clone https://github.com/YOUR_USERNAME/claude-session-saver.git
cd claude-session-saver
bash install.sh
```

## ✅ 验证安装

```bash
# 启动 Claude Code
claude

# 进行一些对话后，检查日志
ls ~/claude-session-logs/
```

## 📖 查看会话

```bash
# 查看最新会话
ls -lt ~/claude-session-logs/*/conversation.md | head -1 | awk '{print $NF}' | xargs cat
```

## 🔧 手动导出

```bash
# 导出最近的会话
python3 ~/claude-session-saver.py

# 导出指定会话
python3 ~/claude-session-saver.py <session-id>
```

## 🗑️ 卸载

```bash
rm ~/claude-session-saver.py
rm -rf ~/claude-session-logs
# 恢复配置备份
cp ~/.claude/settings.json.backup.* ~/.claude/settings.json
```

---

详细文档请查看 [README.md](README.md)
