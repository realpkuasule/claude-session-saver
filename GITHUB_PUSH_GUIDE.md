# 推送到 GitHub 指南

## 步骤 1: 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 仓库名称: `claude-session-saver`
3. 描述: `Automatically save Claude Code sessions as Markdown files`
4. 选择 Public（公开）
5. **不要**勾选 "Initialize this repository with a README"（我们已经有了）
6. 点击 "Create repository"

## 步骤 2: 推送代码

在本地仓库目录 `/root/claude-session-saver` 中执行：

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/claude-session-saver.git

# 推送代码
git branch -M main
git push -u origin main
```

如果使用 SSH：

```bash
git remote add origin git@github.com:YOUR_USERNAME/claude-session-saver.git
git branch -M main
git push -u origin main
```

## 步骤 3: 验证

访问 `https://github.com/YOUR_USERNAME/claude-session-saver` 确认代码已上传。

## 步骤 4: 添加 Topics（可选）

在 GitHub 仓库页面：
1. 点击右侧的 ⚙️ (Settings) 旁边的齿轮图标
2. 添加 topics:
   - `claude-code`
   - `claude-ai`
   - `session-management`
   - `markdown`
   - `automation`
   - `python`

## 步骤 5: 更新 README 中的链接

推送后，编辑 README.md，将：

```markdown
git clone https://github.com/YOUR_USERNAME/claude-session-saver.git
```

替换为实际的仓库地址。

## 未来在新机器上安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/claude-session-saver.git
cd claude-session-saver

# 运行安装脚本
bash install.sh
```

## 一键命令（推送到 GitHub）

```bash
# 设置远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/claude-session-saver.git

# 推送
git branch -M main
git push -u origin main
```

---

**当前状态**: ✅ Git 仓库已初始化，已创建初始提交
**位置**: `/root/claude-session-saver`
**提交**: `c9d2261 Initial commit: Claude Session Saver v1.0.0`
