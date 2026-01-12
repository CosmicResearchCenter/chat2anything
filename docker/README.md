# Chat2Anything Docker 部署指南

## 📋 目录

- [快速开始](#快速开始)
- [环境要求](#环境要求)
- [生产环境部署](#生产环境部署)
- [开发环境部署](#开发环境部署)
- [常用命令](#常用命令)
- [配置说明](#配置说明)
- [故障排除](#故障排除)
- [高级配置](#高级配置)

## 🚀 快速开始

### 1. 环境准备

确保已安装：
- Docker (>= 20.10)
- Docker Compose (>= 2.0)

### 2. 一键启动

#### 生产环境
```bash
# Linux/macOS
cd docker
./start.sh prod

# Windows
cd docker
start.bat prod
```

#### 开发环境
```bash
# Linux/macOS
cd docker
./start.sh dev

# Windows
cd docker
start.bat dev
```

### 3. 访问应用

- **前端**: http://localhost:9966
- **后端API**: http://localhost:9966/api/
- **MySQL**: localhost:3306
- **Elasticsearch**: http://localhost:9200
- **Milvus**: localhost:19530

## 📦 环境要求

### 硬件要求

**生产环境**:
- CPU: 4核+
- 内存: 8GB+
- 磁盘: 50GB+

**开发环境**:
- CPU: 2核+
- 内存: 4GB+
- 磁盘: 20GB+

### 软件要求

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (用于克隆代码)

## 🏗️ 生产环境部署

### 步骤 1: 克隆项目
```bash
git clone <your-repo-url> Chat2Anything
cd Chat2Anything/docker
```

### 步骤 2: 配置环境变量
```bash
# 复制模板文件
cp .env.example .env

# 编辑配置文件
vim .env
```

需要修改的关键配置：
```bash
SECRET_KEY=your_strong_secret_key_here
ADMIN_KEY=your_admin_key_here
MYSQL_PASSWORD=your_mysql_password
```

### 步骤 3: 启动服务
```bash
# Linux/macOS
./start.sh prod

# Windows
start.bat prod
```

### 步骤 4: 查看状态
```bash
# 查看所有容器状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
```

## 💻 开发环境部署

### 步骤 1: 配置开发环境
```bash
cd docker
cp .env.example .env.dev
vim .env.dev
```

### 步骤 2: 启动开发环境
```bash
# Linux/macOS
./start.sh dev

# Windows
start.bat dev
```

### 步骤 3: 开发调试

**后端开发**:
- API 地址: http://localhost:9988
- 调试端口: 5678 (VS Code 调试)
- 热重载: 自动

**前端开发**:
- 开发服务器: http://localhost:3000
- 热重载: 自动

### 步骤 4: 调试配置

创建 VS Code 调试配置 `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Debug",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/backend",
                    "remoteRoot": "/app"
                }
            ]
        }
    ]
}
```

## 📖 常用命令

### 使用 Shell 脚本 (Linux/macOS)

```bash
cd docker

# 启动生产环境
./start.sh prod

# 启动开发环境
./start.sh dev

# 停止所有服务
./start.sh stop

# 查看日志
./start.sh logs prod
./start.sh logs dev

# 重建服务
./start.sh rebuild prod
./start.sh rebuild dev backend

# 查看状态
./start.sh status

# 清理所有数据
./start.sh cleanup

# 显示帮助
./start.sh help
```

### 使用批处理脚本 (Windows)

```bash
cd docker

# 启动生产环境
start.bat prod

# 启动开发环境
start.bat dev

# 停止所有服务
start.bat stop

# 查看日志
start.bat logs prod
start.bat logs dev

# 重建服务
start.bat rebuild prod
start.bat rebuild dev backend

# 查看状态
start.bat status

# 清理所有数据
start.bat cleanup

# 显示帮助
start.bat help
```

### 使用 Makefile (Linux/macOS)

```bash
cd docker

# 启动生产环境
make prod

# 启动开发环境
make dev

# 停止所有服务
make stop

# 查看日志
make logs-prod
make logs-dev

# 重建服务
make rebuild-prod
make rebuild-dev

# 查看状态
make status

# 清理所有数据
make cleanup

# 初始化配置
make setup

# 查看帮助
make help
```

### 直接使用 Docker Compose

```bash
cd docker

# 生产环境
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml ps

# 开发环境
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml logs -f
docker compose -f docker-compose.dev.yml ps
```

## ⚙️ 配置说明

### 环境变量文件

#### .env (生产环境)
```bash
# 安全配置
SECRET_KEY=your_secret_key
ADMIN_KEY=your_admin_key

# Web 配置
WEB_PORT=9966

# MySQL 配置
MYSQL_IP=chat2anything_db
MYSQL_PORT=3306
MYSQL_BASE=chat2anything_db
MYSQL_USER=chat2anything_user
MYSQL_PASSWORD=your_password

# Elasticsearch 配置
ES_BASE_URL=chat2anything_es
ES_BASE_PORT=9200

# Milvus 配置
MILVUS_HOST=chat2anything_milvus
MILVUS_PORT=19530

# 业务配置
SPPLITTER_MODEL=0
```

#### .env.dev (开发环境)
```bash
# 可以使用不同的端口避免冲突
WEB_PORT=9967
MYSQL_PORT=3307
ES_BASE_PORT=9201
MILVUS_PORT=19531

# 其他配置与生产环境相同
```

### 服务端口映射

| 服务 | 容器端口 | 主机端口 (生产) | 主机端口 (开发) | 说明 |
|------|---------|----------------|----------------|------|
| Nginx | 80 | 9966 | 9967 | Web 访问入口 |
| 后端 API | 9988 | 9988 | 9988 | FastAPI 服务 |
| 后端调试 | 5678 | - | 5678 | VS Code 调试 |
| MySQL | 3306 | 3306 | 3307 | 数据库 |
| Elasticsearch | 9200 | 9200 | 9201 | 搜索引擎 |
| Milvus | 19530 | 19530 | 19531 | 向量数据库 |
| Minio | 9000/9001 | 9000/9001 | - | 对象存储 |

## 🔧 故障排除

### 问题 1: 端口冲突

**症状**: 容器启动失败，端口已被占用

**解决**:
```bash
# 检查端口占用
netstat -ano | findstr :9966  # Windows
lsof -i :9966                 # Linux/macOS

# 修改 .env 文件中的端口
WEB_PORT=9967
```

### 问题 2: 内存不足

**症状**: Elasticsearch 或 Milvus 启动失败

**解决**:
```bash
# 降低内存配置
# 在 docker-compose.prod.yml 中修改
ES_JAVA_OPTS=-Xms256m -Xmx256m
```

### 问题 3: 数据库连接失败

**症状**: 后端无法连接 MySQL

**解决**:
```bash
# 1. 检查数据库容器状态
docker compose -f docker-compose.prod.yml ps

# 2. 查看数据库日志
docker compose -f docker-compose.prod.yml logs mysql

# 3. 等待数据库初始化完成
# 首次启动可能需要 30-60 秒
```

### 问题 4: 构建失败

**症状**: Docker build 失败

**解决**:
```bash
# 清理缓存并重建
docker system prune -a --volumes

# 重新构建
docker compose -f docker-compose.prod.yml build --no-cache
```

### 问题 5: 权限问题 (Linux)

**症状**: 无法写入数据卷

**解决**:
```bash
# 修改数据目录权限
sudo chown -R 1000:1000 ./mysql_data ./es_data
```

### 问题 6: 磁盘空间不足

**症状**: 启动失败，提示磁盘空间不足

**解决**:
```bash
# 清理未使用的镜像和容器
docker system prune -a -f --volumes

# 查看磁盘使用
docker system df
```

## 🔍 日志查看

### 查看所有服务日志
```bash
# 生产环境
docker compose -f docker-compose.prod.yml logs -f

# 开发环境
docker compose -f docker-compose.dev.yml logs -f

# 查看特定服务
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f mysql
```

### 查看实时日志
```bash
# 跟踪最新日志
docker compose -f docker-compose.prod.yml logs -f --tail=100
```

## 🛠️ 高级配置

### 1. 自定义镜像源

在 Dockerfile 中添加：
```dockerfile
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG NPM_REGISTRY=https://registry.npmmirror.com
```

### 2. 数据备份

创建备份脚本 `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="./backup/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份 MySQL
docker exec chat2anything_db mysqldump -u chat2anything_user -p'password' chat2anything_db > $BACKUP_DIR/mysql.sql

# 备份配置
cp .env $BACKUP_DIR/
cp docker-compose.prod.yml $BACKUP_DIR/

echo "备份完成: $BACKUP_DIR"
```

### 3. SSL/TLS 配置

在 nginx.conf 中添加 SSL 配置：
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ...
}
```

将证书文件放入 `./docker/ssl/` 目录。

### 4. 资源限制

在 docker-compose.yml 中配置：
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### 5. 环境隔离

使用不同的网络和卷：
```bash
# 开发环境
docker compose -f docker-compose.dev.yml --project-name chat2anything-dev up

# 生产环境
docker compose -f docker-compose.prod.yml --project-name chat2anything-prod up
```

## 📊 监控与维护

### 查看资源使用
```bash
# 实时监控
docker stats

# 查看容器详细信息
docker inspect <container_name>

# 查看网络连接
docker network inspect chat2network
```

### 定期维护
```bash
# 清理日志
docker logs --tail=1000 <container> > log.txt

# 更新镜像
docker compose -f docker-compose.prod.yml pull

# 重启服务
docker compose -f docker-compose.prod.yml restart
```

## 📝 部署清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] 端口 80, 443, 3306, 9200, 19530 可用
- [ ] 至少 8GB 内存可用
- [ ] 至少 50GB 磁盘空间
- [ ] .env 文件已配置
- [ ] 防火墙已配置
- [ ] 数据备份策略已制定
- [ ] 监控已配置
- [ ] 日志轮转已配置

## 🆘 获取帮助

如果遇到问题：
1. 查看 [故障排除](#故障排除) 部分
2. 检查日志: `docker compose -f docker-compose.prod.yml logs`
3. 查看 Docker 状态: `docker system info`
4. 提交 Issue 到项目仓库

## 📄 许可证

本项目使用 MIT 许可证。
