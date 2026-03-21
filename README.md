# 📚 Novel Agent - AI 连载小说写作平台

支持用户自定义技能(Skills)的AI小说写作平台，通过 OpenCode 执行用户部署的写作技能。

## 🏗️ 技术栈

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + Vite + TypeScript + Naive UI |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL |
| File Storage | MinIO (S3兼容) |
| AI Execution | OpenCode |

## 🚀 快速开始

### 1. 启动基础设施 (Docker)

```bash
docker-compose up -d
```

这会启动:
- PostgreSQL (端口 5432)
- MinIO (端口 9000/9001)

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 📁 项目结构

```
novel-agent/
├── frontend/           # Vue 3 前端
│   ├── src/
│   │   ├── api/       # API 客户端
│   │   ├── views/     # 页面组件
│   │   ├── stores/    # Pinia 状态管理
│   │   └── router/    # Vue Router 配置
│   └── package.json
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── api/       # API 路由
│   │   ├── models/    # 数据库模型
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── core/      # 核心配置
│   │   └── services/  # 业务逻辑
│   ├── pyproject.toml
│   └── requirements.txt
├── docker-compose.yml # 基础设施
└── SPEC.md           # 项目规格说明
```

## 🔑 核心功能

### 用户认证
- 注册/登录
- JWT Token 认证

### 项目管理
- 创建/编辑/删除小说项目
- 项目列表展示

### 章节管理
- 章节 CRUD
- 状态跟踪 (草稿/写作中/已完成/已发布)
- 字数统计

### 技能系统 (核心功能)
- 创建自定义写作技能
- 配置技能参数 (JSON)
- 编写技能执行代码
- 通过 OpenCode 执行技能
- 公开/私有技能

### AI 写作助手
- 选择技能执行
- 传入参数
- 将结果应用到正文

## 🌐 云端部署推荐

### 方案 1: Railway + Vercel
- **后端**: Railway (FastAPI + PostgreSQL)
- **前端**: Vercel (Vue)
- **存储**: Railway 附带 PostgreSQL
- **S3**: AWS S3 或 Cloudflare R2

### 方案 2: Fly.io + Cloudflare
- **后端**: Fly.io (Docker)
- **前端**: Cloudflare Pages
- **数据库**: Fly Postgres
- **存储**: Cloudflare R2

### 方案 3: 全 Docker 部署
- 使用 Docker Compose 在任何 VPS 部署

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

## 📝 API 文档

启动后端后访问: http://localhost:8000/docs

## License

MIT
