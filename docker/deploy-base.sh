#!/bin/bash

set -e

echo "开始部署基础服务..."

# 加载环境变量
source .env

# 创建必要的数据目录
echo "创建数据目录..."
mkdir -p mysql_data es_data milvus/etcd milvus/minio_data milvus/milvus_data

# 设置权限
echo "设置目录权限..."
chmod 777 es_data
chmod 777 milvus/etcd milvus/minio_data milvus/milvus_data

# 停止现有服务
echo "停止现有基础服务..."
docker-compose -f docker-compose-base.yml down || true

# 启动基础服务
echo "启动基础服务..."
docker-compose -f docker-compose-base.yml up -d

# 等待服务启动
echo "等待基础服务启动..."
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose-base.yml ps

echo "基础服务部署完成！"
echo "MySQL: localhost:${MYSQL_PORT:-3306}"
echo "Elasticsearch: localhost:${ES_BASE_PORT:-9200}"
echo "Milvus: localhost:${MILVUS_PORT:-19530}"
echo "MinIO Console: localhost:9001"
