# 🚀 快速启动指南

## 5 分钟快速开始

### 方式 1: 使用 Shell 脚本 (Linux/macOS)

```bash
cd docker
chmod +x start.sh
./start.sh prod
```

### 方式 2: 使用批处理脚本 (Windows)

```bash
cd docker
start.bat prod
```

### 方式 3: 使用 Makefile (Linux/macOS)

```bash
cd docker
make prod
```

### 方式 4: 直接使用 Docker Compose

```bash
cd docker
cp .env.example .env
# 编辑 .env 文件配置密码
docker compose -f docker-compose.prod.yml up -d --build
```

## 访问应用

启动完成后，访问以下地址：

- **前端**: http://localhost:9966
- **后端API**: http://localhost:9966/api/
- **API文档**: http://localhost:9966/api/docs

## 开发环境

```bash
# Linux/macOS
./start.sh dev

# Windows
start.bat dev
```

开发环境特性：
- ✅ 热重载
- ✅ 调试支持 (端口 5678)
- ✅ 独立前端开发服务器 (端口 3000)

## 常用命令

| 命令 | 说明 |
|------|------|
| `./start.sh prod` | 启动生产环境 |
| `./start.sh dev` | 启动开发环境 |
| `./start.sh stop` | 停止所有服务 |
| `./start.sh logs prod` | 查看生产环境日志 |
| `./start.sh status` | 查看服务状态 |
| `./start.sh help` | 查看所有命令 |

## 配置文件

首次启动会自动创建 `.env` 文件，需要编辑以下配置：

```bash
# 安全配置 (必填)
SECRET_KEY=your_strong_secret_key
ADMIN_KEY=your_admin_key

# 数据库密码 (必填)
MYSQL_PASSWORD=your_mysql_password
```

## 故障排除

### 端口被占用
```bash
# 修改 .env 文件
WEB_PORT=9967
MYSQL_PORT=3307
```

### 启动失败
```bash
# 查看日志
./start.sh logs prod

# 清理后重新启动
./start.sh cleanup
./start.sh prod
```

### 内存不足
降低 docker-compose.yml 中的内存限制，或增加系统内存。

## 下一步

- 详细配置: 查看 [README.md](README.md)
- 故障排除: 查看 README.md 的故障排除章节
- 高级配置: 查看 README.md 的高级配置章节

## 获取帮助

如果遇到问题：
1. 运行 `./start.sh help` 查看帮助
2. 查看 [README.md](README.md) 详细文档
3. 检查日志: `./start.sh logs prod`
