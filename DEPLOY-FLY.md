# Fly.io 部署指南

## 前置准备

1. **Fly.io 账号** https://fly.io
2. **flyctl CLI** 
   ```bash
   # macOS
   brew install flyctl
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

3. **登录**
   ```bash
   flyctl auth login
   ```

## 快速部署

### 1. 创建应用

```bash
cd novel-agent
flyctl launch --no-deploy
```

这会创建应用并生成 `fly.toml`，但暂不部署。

### 2. 创建 PostgreSQL 数据库

```bash
flyctl postgres create --name novel-agent-db
```

绑定到你的应用：
```bash
flyctl postgres attach --app novel-agent novel-agent-db
```

### 3. 创建 S3 兼容存储 (或使用现有)

**方案A: Fly.io Volumes (推荐)**
```bash
flyctl volumes create novel_data --app novel-agent
```

**方案B: 使用 Cloudflare R2 / AWS S3**

在 `.env` 中配置：
```
S3_ENDPOINT=https://xxx.r2.cloudflarestorage.com
S3_ACCESS_KEY=your-key
S3_SECRET_KEY=your-secret
S3_BUCKET=novel-agent
```

### 4. 配置环境变量

```bash
# 设置密钥
flyctl secrets set SECRET_KEY=your-super-secret-key-at-least-32-chars

# 如果使用 R2/S3
flyctl secrets set S3_ENDPOINT=https://xxx.r2.cloudflarestorage.com
flyctl secrets set S3_ACCESS_KEY=your-key
flyctl secrets set S3_SECRET_KEY=your-secret
flyctl secrets set S3_BUCKET=novel-agent
```

### 5. 部署

```bash
flyctl deploy
```

### 6. 访问

```bash
flyctl ips list --app novel-agent
```

获取 IP 后访问 `http://<IP>:8080`

## 自定义域名 (可选)

```bash
flyctl certs add your-domain.com
flyctl certs show your-domain.com
# 按提示配置 DNS 记录
```

## 常见命令

```bash
# 查看日志
flyctl logs

# SSH 进入容器
flyctl ssh enter

# 扩展/缩减
flyctl scale count 2  # 2 个实例

# 停止应用
flyctl scale count 0

# 重启
flyctl restart
```

## 免费额度

| 资源 | 免费额度 |
|------|---------|
| VM | 3个共享实例 |
| Volume | 3GB |
| Postgres | 1个共享实例 |
| 带宽 | 160GB/月 |

足够个人使用！🐱

## 故障排除

```bash
# 查看部署状态
flyctl status

# 查看最近事件
flyctl events

# 进入容器调试
flyctl ssh console

# 检查健康检查
flyctl checks list
```
