# Chat2Anything ![版本](https://img.shields.io/badge/版本-1.0.0-blue)![协议](https://img.shields.io/badge/协议-MIT-green)

## 目录
- [项目简介](#项目简介)
- [主要功能](#主要功能)
- [架构图](#架构图)
- [系统需求](#系统需求)
- [部署步骤](#部署步骤)
  - [Docker Compose 部署](#docker-compose-部署-推荐)
  - [源码部署](#源码部署)
- [使用指南](#使用指南)
- [常见问题](#常见问题)
- [API文档](#api文档)
- [贡献指南](#贡献指南)

## 项目简介
Chat2Anything 是一个强大的检索增强生成(RAG)系统，允许用户通过自然语言与各种数据源进行交互。该项目集成了先进的向量搜索和大语言模型技术，支持多种文档格式导入，为您提供智能、高效的知识检索和问答服务。

## 主要功能
- 🔍 智能文档检索和问答
- 🌐 支持多种LLM提供商(OpenAI, Zhipu, OneAPI等)
- 📊 高效的向量存储和检索系统(Milvus, Elasticsearch)
- 📁 支持多种文档格式导入
- 💬 自然语言交互界面
- 🛠️ 简单易用的Docker部署方案

## 架构图
![RAG_Architecture_Diagram](./docs/images/RAG_Architecture_Diagram.png)

## 系统需求
- Docker 和 Docker Compose
- 至少4GB RAM
- 网络连接(用于API调用)
- Git

## 部署步骤
### Docker Compose 部署 (推荐)
拉取项目
```bash
git clone https://github.com/CosmicResearchCenter/chat2anything.git
```
进入docker目录
```bash
cd chat2anything/docker
```

配置.env文件
```bash
cp .env_copy .env
vim .env
```

### 环境变量配置说明
必须配置的信息是EMBEDDING和LLM的API信息，其他的可以默认保持不变。以下是主要配置项说明：

```txt
# 基本配置
SECRET_KEY=chat2anything_secret_key      # 应用密钥
BACKEND_PORT=9988                        # 后端服务端口
WEB_POET=12345                          # 前端端口
WEB_HOST=127.0.0.1                       # 前端服务主机地址

# 数据库配置
MYSQL_IP=chat2anything_db                # MySQL服务名称
MYSQL_PORT=3306                          # MySQL端口
MYSQL_BASE=chat2anything_db              # 数据库名
MYSQL_USER=chat2anything_user            # 数据库用户
MYSQL_PASSWORD=chat2anything_password    # 数据库密码

# 向量嵌入配置
EMBEEDING_BASE_URL=https://aihubmix.com/v1  # 向量服务地址
EMBEEDING_API_KEY=                        # 向量服务API密钥
EMBEDDING_MODEL_PROVIDER=OPENAI           # 向量模型提供商

# LLM配置
LLM_PROVIDER=OPENAI                       # LLM提供商
SPPLITTER_MODEL=0                         # 拆分模型参数

# 搜索引擎配置
ES_BASE_URL=chat2anything_es              # Elasticsearch服务名
ES_BASE_PORT=9200                         # Elasticsearch端口

# 向量数据库配置
MILVUS_HOST=chat2anything_milvus          # Milvus服务名
MILVUS_PORT=19530                         # Milvus端口

# OpenAI配置
OPENAI_API_KEY=                           # OpenAI API密钥(必填)
OPENAI_BASE_URL=https://aihubmix.com/v1   # OpenAI API地址
OPENAI_MODEL=gpt-4o-mini                  # 使用的模型名称
OPENAI_EMBEDDING_MODEL=text-embedding-3-small  # 向量模型名称
```

系统还支持其他LLM提供商，如OneAPI、智谱AI、SparkAI等，详细配置请参考.env_copy文件。

修改完成后，运行即可
```bash
sudo docker-compose up -d
```

### 源码部署
#### 环境要求
- Python 3.8+ (推荐Python 3.10)
- Node.js 16+ 和 npm 8+
- MySQL 8.0+
- Elasticsearch 8.x
- Milvus 2.4+
- 至少8GB内存(推荐16GB以上)

#### 前置服务安装
1. **MySQL 安装**

2. **Elasticsearch 安装**

3. **Milvus 安装**

#### 后端部署
进入后端目录
```bash
cd backend
```

创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 Windows下
# venv\Scripts\activate
```

安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

配置.env文件
```bash
cp .env_copy .env
vim .env
```

必要的环境变量配置：
```ini
# 数据库配置
MYSQL_IP=localhost  # 本地部署使用localhost
MYSQL_PORT=3306
MYSQL_BASE=chat2anything_db
MYSQL_USER=root  # 或您创建的用户
MYSQL_PASSWORD=your_password

# ElasticSearch配置
ES_BASE_URL=localhost
ES_BASE_PORT=9200

# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# LLM配置（至少配置一种）
LLM_PROVIDER=OPENAI
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # 或您的代理地址
OPENAI_MODEL=gpt-4o-mini
```

运行后端服务
```bash
python main.py
```

#### 前端部署
进入前端目录
```bash
cd web
```

安装依赖
```bash
npm install
```

配置环境变量
```bash
cp .env_copy .env
```

编辑.env文件配置后端API地址：
```
# 本地开发
VITE_APP_BASE_URL=http://127.0.0.1:9988

# 远程服务器
# VITE_APP_BASE_URL=http://your_server_ip:9988
```

开发模式运行
```bash
npm run dev
```

生产环境构建与部署
```bash
# 构建前端资源
npm run build

# 使用nginx部署(示例配置)
sudo apt install nginx
sudo vim /etc/nginx/sites-available/chat2anything

# nginx配置示例
# server {
#     listen 80;
#     server_name your_domain.com;
#     root /path/to/web/dist;
#     index index.html;
#     location / {
#         try_files $uri $uri/ /index.html;
#     }
#     location /api/ {
#         proxy_pass http://127.0.0.1:9988;
#     }
# }

# 启用站点并重启nginx
sudo ln -s /etc/nginx/sites-available/chat2anything /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 使用指南
1. 启动服务后，访问 `http://127.0.0.1:12345` 打开Web界面
2. 通过界面上传您的知识库文档
3. 开始与您的数据进行对话交流

## 常见问题
**Q: 如何更改默认端口?**
A: 在.env文件中修改BACKEND_PORT和WEB_POET参数。

**Q: 支持哪些文档格式?**
A: 支持PDF、Word、TXT、Markdown等常见文档格式。

**Q: 如何扩展存储容量?**
A: 可以通过修改docker-compose.yml中相关服务的volume配置。

## API文档
详细的API使用说明请参考：[Chat2Anything API 文档](./docs/api.md)

## 贡献指南
欢迎提交Issue和Pull Request来帮助改进项目！
