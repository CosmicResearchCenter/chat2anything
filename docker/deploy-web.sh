#!/bin/bash

set -e

echo "开始部署前端应用..."


# 检查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "错误: .env 文件不存在，请先创建配置文件"
    exit 1
fi

# 创建网络
echo "创建Docker网络..."
docker network create chat2network 2>/dev/null || echo "网络已存在"

# 停止并移除旧的前端容器
echo "停止旧的前端容器..."
docker-compose -f docker-compose-web.yml down || true

# 构建并启动前端服务
echo "构建前端镜像..."
docker-compose -f docker-compose-web.yml build --no-cache

echo "启动前端服务..."
docker-compose -f docker-compose-web.yml up -d

# 等待服务启动
echo "等待前端服务启动..."
sleep 15

# 检查服务状态
echo "检查服务状态..."
if docker-compose -f docker-compose-web.yml ps | grep -q "Up"; then
    echo "✅ 前端部署成功！"
    docker-compose -f docker-compose-web.yml ps
else
    echo "❌ 前端部署失败！"
    docker-compose -f docker-compose-web.yml logs
    exit 1
fi

echo "前端部署完成！"
