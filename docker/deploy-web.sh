#!/bin/bash

set -e

echo "开始部署Web应用..."


# 检查网络是否存在，如果不存在则创建
echo "检查Docker网络..."
if ! docker network ls | grep -q chat2network; then
    echo "创建Docker网络..."
    docker network create chat2network
fi

# 停止现有的web服务
echo "停止现有的web服务..."
docker-compose -f docker-compose-web.yml down || true

# 清理未使用的镜像
echo "清理未使用的Docker镜像..."
docker image prune -f

# 构建并启动web服务
echo "构建并启动web服务..."
docker-compose -f docker-compose-web.yml up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 30

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose-web.yml ps

echo "Web应用部署完成！"
