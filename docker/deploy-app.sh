#!/bin/bash

set -e

echo "开始部署后端应用..."


# 检查环境文件
if [ ! -f .env ]; then
    echo "复制环境配置文件..."
    if [ -f .env_copy ]; then
        cp .env_copy .env
    else
        echo "错误: 未找到环境配置文件 .env_copy"
        exit 1
    fi
fi

# 检查网络是否存在
echo "检查Docker网络..."
if ! docker network ls | grep -q chat2network; then
    echo "错误: chat2network网络不存在，请先部署基础服务！"
    exit 1
fi

# 停止现有的后端服务
echo "停止现有的后端服务..."
docker-compose -f docker-compose-app.yml down || true

# 清理未使用的镜像
echo "清理未使用的Docker镜像..."
docker image prune -f

# 等待基础服务就绪
echo "检查基础服务状态..."
for service in chat2anything_db chat2anything_es chat2anything_milvus; do
    if ! docker ps | grep -q $service; then
        echo "警告: $service 服务未运行，请检查基础服务状态"
    fi
done

# 构建并启动后端服务
echo "构建并启动后端服务..."
docker-compose -f docker-compose-app.yml up -d --build

# 等待服务启动
echo "等待后端服务启动..."
sleep 60

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose-app.yml ps


echo "后端应用部署完成！"
