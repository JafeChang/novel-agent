# 📚 Novel Agent - AI 连载小说写作平台

支持用户自定义技能(Skills)的AI小说写作平台。通过 OpenCode 执行用户部署的写作技能，支持多用户、章节管理、S3文件存储。

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ 核心功能

- 🤖 **AI 写作助手** - 选择技能，一键生成小说内容
- 🎯 **自定义技能系统** - 用户可创建、分享、复制写作技能
- 📖 **项目管理** - 创建小说项目，管理多个章节
- ✍️ **章节编辑器** - 流畅的写作体验，支持模板插入
- 💾 **S3 文件存储** - 图片、附件等文件存储
- 🔐 **用户认证** - JWT 安全的用户系统

## 🏗️ 技术栈

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Vite + TypeScript + Naive UI |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL |
| File Storage | MinIO (S3兼容) |
| AI Execution | OpenCode |

## 🚀 快速开始

### 一键启动 (推荐)

```bash
# 克隆项目
git clone <repository-url>
cd novel-agent

# 启动所有服务
chmod +x start.sh
./start.sh
```

### 手动启动

#### 1. 启动基础设施 (Docker)

```bash
docker-compose up -d
```

这会启动:
- **PostgreSQL** (端口 5432) - 数据库
- **MinIO** (端口 9000/9001) - S3兼容存储

#### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| MinIO 控制台 | http://localhost:9001 |

**默认账号:** 注册后即可使用

**MinIO 账号:** minioadmin / minioadmin

## 📁 项目结构

```
novel-agent/
├── frontend/                  # Vue 3 前端
│   ├── src/
│   │   ├── api/              # API 客户端
│   │   ├── views/            # 页面组件
│   │   ├── stores/           # Pinia 状态管理
│   │   └── router/           # Vue Router 配置
│   └── package.json
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── api/              # API 路由
│   │   ├── models/           # 数据库模型
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── core/             # 核心配置
│   │   └── services/         # 业务逻辑 (S3, OpenCode)
│   └── requirements.txt
├── scripts/                    # 辅助脚本
├── docker-compose.yml         # 基础设施编排
├── Dockerfile                 # 后端构建文件
├── start.sh                   # 一键启动脚本
└── README.md
```

## 🎯 技能系统

技能是 Novel Agent 的核心功能。用户可以创建自定义的 AI 写作技能。

### 技能结构

```json
{
  "name": "小说章节写作助手",
  "description": "根据情节提示生成小说章节",
  "config": {
    "style": "现实主义",
    "mood": "悬疑"
  },
  "code": "技能执行代码，支持 Markdown 格式..."
}
```

### 示例技能

创建技能后，在章节编辑器中选择技能，输入参数，点击"执行"即可生成内容。

## 🔌 API 接口

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/me` - 获取当前用户

### 项目
- `GET /api/projects` - 项目列表
- `POST /api/projects` - 创建项目
- `GET /api/projects/{id}` - 获取项目
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

### 章节
- `GET /api/projects/{id}/chapters` - 章节列表
- `POST /api/projects/{id}/chapters` - 创建章节
- `GET /api/chapters/{id}` - 获取章节
- `PUT /api/chapters/{id}` - 更新章节
- `DELETE /api/chapters/{id}` - 删除章节

### 技能
- `GET /api/skills` - 技能列表
- `POST /api/skills` - 创建技能
- `POST /api/skills/{id}/execute` - 执行技能
- `PUT /api/skills/{id}` - 更新技能
- `DELETE /api/skills/{id}` - 删除技能

### 文件
- `POST /api/files/upload` - 上传文件
- `GET /api/files/{key}` - 下载文件
- `DELETE /api/files/{key}` - 删除文件

## 🌐 云端部署

### 方案 1: Railway + Vercel (推荐)

**后端部署 (Railway)**
1. 创建 Railway 账号
2. 连接 GitHub 仓库
3. 设置环境变量:
   - `DATABASE_URL`: PostgreSQL 连接串
   - `SECRET_KEY`: 随机密钥
   - `S3_*`: S3 配置
4. 部署

**前端部署 (Vercel)**
1. 创建 Vercel 项目
2. 设置构建命令: `pnpm install && pnpm run build`
3. 设置环境变量: `VITE_API_URL` = 后端地址

**数据库:** Railway PostgreSQL
**存储:** AWS S3 或 Cloudflare R2

### 方案 2: Fly.io + Cloudflare

**后端:** Fly.io (Docker 部署)
**前端:** Cloudflare Pages
**数据库:** Fly Postgres
**存储:** Cloudflare R2

### 方案 3: 完整 Docker 部署

在任何 VPS 上使用 docker-compose 部署:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 环境变量

### Backend (.env)

```env
DATABASE_URL=postgresql://novel:novel@localhost:5432/novel_agent
SECRET_KEY=your-secret-key-change-in-production
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=novel-agent
OPENCODE_API_URL=http://localhost:8080
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## 📝 开发指南

### 前端开发

```bash
cd frontend
pnpm install
pnpm dev     # 开发模式
pnpm build   # 生产构建
```

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 数据库迁移

```bash
cd backend
alembic upgrade head
```

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件
