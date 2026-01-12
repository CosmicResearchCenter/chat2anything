# 多阶段构建：优化镜像大小和构建速度
FROM python:3.12-bullseye AS builder

# 设置镜像源
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖到虚拟环境
RUN pip install --no-cache-dir --user -r requirements.txt -i ${PIP_INDEX_URL}

# 最终阶段
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置镜像源
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

# 设置时区
ENV TZ=Asia/Shanghai

# 更新系统包并安装运行时依赖
RUN echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-backports main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# 复制 Python 依赖
COPY --from=builder /root/.local /root/.local

# 复制项目文件
COPY . .

# 设置环境变量以使用用户安装的包
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 9988

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9988/health', timeout=5)" || exit 1

# 启动应用程序
CMD ["sh", "-c", "python main.py"]