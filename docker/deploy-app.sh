#!/bin/bash

set -e

echo "开始部署后端应用..."

# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "错误: .env 文件不存在，请先创建配置文件"
    exit 1
fi

# 创建网络
echo "创建Docker网络..."
docker network create chat2network 2>/dev/null || echo "网络已存在"

# 检查是否有docker compose或docker-compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# 停止并移除旧的后端容器
echo "停止旧的后端容器..."
$COMPOSE_CMD -f docker-compose-app.yml down || true

# 构建并启动后端服务
echo "构建后端镜像..."
$COMPOSE_CMD -f docker-compose-app.yml build --no-cache

echo "启动后端服务..."
$COMPOSE_CMD -f docker-compose-app.yml up -d

# 等待服务启动
echo "等待后端服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
if $COMPOSE_CMD -f docker-compose-app.yml ps | grep -q "Up"; then
    echo "✅ 后端部署成功！"
    $COMPOSE_CMD -f docker-compose-app.yml ps
else
    echo "❌ 后端部署失败！"
    $COMPOSE_CMD -f docker-compose-app.yml logs
    exit 1
fi

echo "后端部署完成！"
