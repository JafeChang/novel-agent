# Railway + E2B 部署指南

## 架构

```
┌─────────────────────────────────────────────────────────┐
│  Railway                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Frontend   │  │   Backend   │  │ PostgreSQL  │     │
│  │  (Static)   │  │  (FastAPI)  │  │  Database   │     │
│  └─────────────┘  └──────┬──────┘  └─────────────┘     │
└──────────────────────────┼─────────────────────────────┘
                           │ HTTP API
                           ▼
┌─────────────────────────────────────────────────────────┐
│  E2B Cloud                                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │  AI Agent Sandbox (OpenCode)                     │   │
│  │  - Secure code execution                          │   │
│  │  - Skill execution                               │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 前置准备

1. **Railway 账号** https://railway.app
2. **E2B 账号** https://e2b.dev
3. **GitHub 仓库** 已配置 (JafeChang/novel-agent)

---

## 步骤 1: 部署 Railway

### 1.1 安装 Railway CLI

```bash
npm install -g @railway/cli
```

### 1.2 登录

```bash
railway login
```

### 1.3 创建项目

```bash
cd novel-agent
railway init
```

### 1.4 添加 PostgreSQL

```bash
railway add postgres
```

### 1.5 配置环境变量

在 Railway Dashboard 中设置：

```
SECRET_KEY=your-super-secret-key-at-least-32-chars
S3_ENDPOINT=https://xxx.r2.cloudflarestorage.com  # 可选
S3_ACCESS_KEY=xxx  # 可选
S3_SECRET_KEY=xxx  # 可选
S3_BUCKET=novel-agent  # 可选
E2B_API_KEY=your-e2b-api-key
```

### 1.6 部署

```bash
railway up --detach
```

### 1.7 获取 URL

```bash
railway status
```

---

## 步骤 2: 配置 E2B

### 2.1 安装 E2B CLI

```bash
npm install -g @e2b/cli
```

### 2.2 登录

```bash
e2b auth login
```

### 2.3 创建 AI Agent

在 E2B Dashboard 创建 sandbox template，选择 OpenCode 镜像。

### 2.4 获取 API Key

在 E2B Dashboard 获取 API key，添加到 Railway 环境变量。

---

## 步骤 3: 更新前端 API 地址

```bash
# 在 frontend 目录
VITE_API_URL=https://your-railway-app.railway.app
```

---

## 免费额度

| 服务 | 免费额度 |
|------|---------|
| Railway | $5/月 = 500小时，3个数据库 |
| E2B | 包含在 Starter 计划 |

---

## 快速命令

```bash
# 部署
railway up

# 查看状态
railway status

# 查看日志
railway logs

# 打开 Dashboard
railway open

# 添加环境变量
railway variables set SECRET_KEY=xxx
```
