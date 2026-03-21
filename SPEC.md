# Novel Agent - 连载小说写作平台

## 1. Concept & Vision

一个支持用户自定义技能(Skills)的AI小说写作平台。用户可以部署自己的写作技能，平台调用OpenCode执行。支持多用户、章节管理、S3文件存储。

**核心流程：** 用户创建项目 → 选择/部署技能 → 配置参数 → AI生成章节 → 保存发布

## 2. Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Vue 3 Frontend│────▶│  FastAPI Backend│────▶│   PostgreSQL    │
│   (Vite + TS)   │     │   (Python 3.11) │     │   (用户/项目数据) │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌───────────┐  ┌───────────┐  ┌───────────┐
            │  MinIO S3 │  │ OpenCode  │  │  Skills   │
            │ (文件存储) │  │  Executor │  │  Registry │
            └───────────┘  └───────────┘  └───────────┘
```

## 3. Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Vue 3 + Vite + TypeScript | 组件化开发 |
| UI Library | Naive UI 或 TailwindCSS | 快速搭建 |
| Backend | FastAPI + Python 3.11 | 异步高性能 |
| Database | PostgreSQL | 用户/项目/章节数据 |
| ORM | SQLAlchemy + Alembic | 数据库迁移 |
| File Storage | MinIO (S3兼容) | 本地开发 / 迁移到云S3 |
| AI Execution | OpenCode | 执行用户技能 |
| Auth | JWT | 用户认证 |

## 4. Data Models

### User
- id, email, password_hash, username, created_at

### Project
- id, user_id, name, description, created_at

### Chapter
- id, project_id, title, content, status, created_at

### Skill
- id, user_id, name, description, config (JSON), code, created_at

## 5. API Endpoints

### Auth
- POST /api/auth/register
- POST /api/auth/login
- GET /api/auth/me

### Projects
- GET /api/projects
- POST /api/projects
- GET /api/projects/{id}
- PUT /api/projects/{id}
- DELETE /api/projects/{id}

### Chapters
- GET /api/projects/{id}/chapters
- POST /api/projects/{id}/chapters
- GET /api/chapters/{id}
- PUT /api/chapters/{id}
- DELETE /api/chapters/{id}

### Skills
- GET /api/skills
- POST /api/skills
- PUT /api/skills/{id}
- DELETE /api/skills/{id}
- POST /api/skills/{id}/execute

### Files (S3)
- POST /api/files/upload
- GET /api/files/{key}
- DELETE /api/files/{key}

## 6. Frontend Pages

1. **登录/注册** - Auth forms
2. **Dashboard** - 项目列表
3. **项目详情** - 章节管理
4. **编辑器** - 章节编辑 + AI写作助手
5. **技能市场** - 浏览/部署技能
6. **技能编辑器** - 自定义技能配置

## 7. Deployment Plan

### 开发环境
- Docker Compose: PostgreSQL + MinIO + FastAPI + Vue

### 云服务推荐 (海外)
- **Railway** - 简单部署 FastAPI + PostgreSQL
- **Fly.io** - 免费额度，适合 FastAPI
- **Vercel** - 前端部署
- **Cloudflare R2** - S3兼容存储

### 域名
- 初期使用服务自带域名
- 后期可绑定自定义域名 (Vercel/Railway都支持)

## 8. Development Phases

### Phase 1: 基础框架 ✅
- [ ] 项目脚手架 (Vue + FastAPI)
- [ ] 数据库模型 + 迁移
- [ ] 认证系统 (JWT)

### Phase 2: 核心功能
- [ ] 项目管理 CRUD
- [ ] 章节管理 CRUD
- [ ] 基础编辑器

### Phase 3: AI 集成
- [ ] OpenCode 集成
- [ ] 技能系统
- [ ] AI写作执行

### Phase 4: 文件存储
- [ ] MinIO 集成
- [ ] 文件上传/下载

### Phase 5: 部署
- [ ] Docker Compose (开发)
- [ ] 云服务部署配置
- [ ] 域名绑定
