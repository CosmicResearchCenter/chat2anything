# Stage 1: Build the project
FROM node:18-alpine AS builder

# 设置镜像源
ARG NPM_REGISTRY=https://registry.npmmirror.com
ENV NPM_REGISTRY=${NPM_REGISTRY}

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖 (使用缓存层优化)
RUN npm config set registry ${NPM_REGISTRY} && \
    npm install --prefer-offline --no-audit

# 复制源代码
COPY . .

# 设置环境变量
ARG VITE_APP_BASE_URL=/api
ENV VITE_APP_BASE_URL=${VITE_APP_BASE_URL}

# 构建项目
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# 设置时区
ENV TZ=Asia/Shanghai

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# 删除默认的 Nginx 配置
RUN rm -f /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
