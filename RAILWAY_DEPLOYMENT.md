# Railway 部署指南

## 🚀 在 Railway 上部署 Q 股票分析智能体

### 步骤 1: 访问 Railway

1. 打开 https://railway.app
2. 点击 **"Start a New Project"**

### 步骤 2: 连接 GitHub

1. 点击 **"Deploy from GitHub repo"**
2. 授权 Railway 访问你的 GitHub
3. 选择 `qiminghui618-tech/Q` 仓库
4. 点击 **"Deploy"**

### 步骤 3: 配置环境

Railway 会自动识别：
- ✅ `Procfile` - 启动命令
- ✅ `requirements.txt` - Python 依赖
- ✅ `runtime.txt` - Python 版本

**自动配置，无需手动操作！**

### 步骤 4: 等待部署完成

1. Railway 开始构建和部署
2. 查看 **Build Logs** 和 **Deploy Logs**
3. 部署完成后，你会看到公网 URL

### 步骤 5: 访问应用

部署完成后，你会获得类似的 URL：

```
https://your-app-name.railway.app
```

访问：
```
https://your-app-name.railway.app/index.html
```

或查看 API 文档：
```
https://your-app-name.railway.app/docs
```

---

## 🔄 自动部署

**好消息！** 每次你 push 代码到 GitHub 的 `develop` 分支时，Railway 会自动重新部署！

```bash
git add .
git commit -m "Update"
git push origin develop
```

Railway 会自动部署新版本 → 无需手动操作！

---

## 📊 监控应用

在 Railway Dashboard 中，你可以：
- 📈 查看日志
- 📊 监控资源使用
- 🔄 重新启动应用
- ⚙️ 配置环境变量

---

## ⚙️ 环境变量配置

如果需要配置 OpenAI 或其他 API key：

1. 进入 Railway 项目
2. 点击 **Variables**
3. 添加：
   ```
   LLM_PROVIDER=mock
   OPENAI_API_KEY=your_key_here
   ```

---

## 🎯 完整 URL 地址

部署后你会获得：

| 功能 | URL |
|------|-----|
| **Web 仪表板** | `https://your-app.railway.app/index.html` |
| **API 文档** | `https://your-app.railway.app/docs` |
| **获取推荐** | `https://your-app.railway.app/api/v1/recommendation/AAPL` |
| **创建告警** | `https://your-app.railway.app/api/v1/alerts` |

---

## ✅ 部署检查清单

- [x] Procfile 配置
- [x] runtime.txt 指定 Python 版本
- [x] requirements.txt 包含所有依赖
- [x] index.html 放在根目录
- [x] GitHub 仓库已连接 Railway
- [x] 代码已 push 到 develop 分支

**一切就绪！** 开始部署吧！ 🚀

---

## 🆘 故障排除

### 部署失败？

1. **检查 Build Logs** - 看具体错误信息
2. **常见原因**：
   - Python 依赖安装失败 → 检查 requirements.txt
   - Port 配置问题 → Procfile 已正确配置
   - 环境变量缺失 → 添加到 Railway Variables

3. **联系支持** - Railway 有很好的文档和社区支持

---

## 🎉 部署完成！

你现在有了一个**完全自动化的生产级应用**！

每次提交代码时自动部署，无需任何手动操作！

**现在访问你的公网地址开始使用吧！** 🌐
