# Chat2Anything Docker 管理 Makefile
# 适用于 Linux/macOS �境

.PHONY: help prod dev stop logs rebuild status cleanup setup

# 颜色定义
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
NC=\033[0m # No Color

# 项目信息
PROJECT_NAME = Chat2Anything
DOCKER_DIR = $(shell pwd)

# 默认目标
help:
	@echo "$(BLUE)$(PROJECT_NAME) Docker 管理工具$(NC)"
	@echo ""
	@echo "用法: make [目标]"
	@echo ""
	@echo "可用目标:"
	@echo "  $(GREEN)prod$(NC)          启动生产环境"
	@echo "  $(GREEN)dev$(NC)           启动开发环境"
	@echo "  $(GREEN)stop$(NC)          停止所有服务"
	@echo "  $(GREEN)logs-prod$(NC)     查看生产环境日志"
	@echo "  $(GREEN)logs-dev$(NC)      查看开发环境日志"
	@echo "  $(GREEN)rebuild-prod$(NC)  重建生产环境"
	@echo "  $(GREEN)rebuild-dev$(NC)   重建开发环境"
	@echo "  $(GREEN)status$(NC)        显示服务状态"
	@echo "  $(GREEN)cleanup$(NC)       清理所有数据"
	@echo "  $(GREEN)setup$(NC)         初始化环境配置"
	@echo ""
	@echo "示例:"
	@echo "  make prod              # 启动生产环境"
	@echo "  make dev               # 启动开发环境"
	@echo "  make logs-prod         # 查看生产环境日志"
	@echo "  make status            # 查看所有服务状态"

# 检查环境
check-env:
	@command -v docker >/dev/null 2>&1 || (echo "$(RED)Docker 未安装$(NC)" && exit 1)
	@command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1 || (echo "$(RED)Docker Compose 未安装$(NC)" && exit 1)
	@echo "$(GREEN)✓ Docker 环境检查通过$(NC)"

# 检查 .env 文件
check-dotenv:
	@if [ ! -f ".env" ]; then \
		echo "$(YELLOW)警告: .env 文件不存在，正在从模板创建...$(NC)"; \
		if [ -f ".env.example" ]; then \
			cp .env.example .env; \
			echo "$(GREEN)已创建 .env 文件，请先编辑配置$(NC)"; \
			exit 1; \
		else \
			echo "$(RED)错误: .env.example 文件不存在$(NC)"; \
			exit 1; \
		fi; \
	fi

# 检查 .env.dev 文件
check-dotenv-dev:
	@if [ ! -f ".env.dev" ]; then \
		echo "$(YELLOW)警告: .env.dev 文件不存在，正在从模板创建...$(NC)"; \
		if [ -f ".env.example" ]; then \
			cp .env.example .env.dev; \
			echo "$(GREEN)已创建 .env.dev 文件，请先编辑配置$(NC)"; \
			exit 1; \
		else \
			echo "$(RED)错误: .env.example 文件不存在$(NC)"; \
			exit 1; \
		fi; \
	fi

# 创建网络
create-network:
	@docker network ls | grep -q "chat2network" || docker network create chat2network

# 启动生产环境
prod: check-env check-dotenv create-network
	@echo "$(BLUE)启动生产环境...$(NC)"
	docker compose -f docker-compose.prod.yml up -d --build
	@echo ""
	@echo "$(GREEN)✓ 生产环境启动完成！$(NC)"
	@echo "访问地址: http://localhost:$$(grep WEB_PORT .env | cut -d= -f2 || echo 9966)"
	@echo "后端API: http://localhost:$$(grep WEB_PORT .env | cut -d= -f2 || echo 9966)/api/"
	@echo ""
	@echo "查看日志: make logs-prod"
	@echo "停止服务: make stop"

# 启动开发环境
dev: check-env check-dotenv-dev create-network
	@echo "$(BLUE)启动开发环境...$(NC)"
	docker compose -f docker-compose.dev.yml up -d --build
	@echo ""
	@echo "$(GREEN)✓ 开发环境启动完成！$(NC)"
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:9988"
	@echo "Nginx: http://localhost:$$(grep WEB_PORT .env.dev | cut -d= -f2 || echo 9966)"
	@echo ""
	@echo "查看日志: make logs-dev"
	@echo "停止服务: make stop"

# 停止所有服务
stop:
	@echo "$(BLUE)停止所有服务...$(NC)"
	@docker compose -f docker-compose.prod.yml down 2>/dev/null || true
	@docker compose -f docker-compose.dev.yml down 2>/dev/null || true
	@echo "$(GREEN)✓ 所有服务已停止$(NC)"

# 查看生产环境日志
logs-prod:
	docker compose -f docker-compose.prod.yml logs -f

# 查看开发环境日志
logs-dev:
	docker compose -f docker-compose.dev.yml logs -f

# 重建生产环境
rebuild-prod: check-env check-dotenv
	@echo "$(BLUE)重建生产环境...$(NC)"
	docker compose -f docker-compose.prod.yml up -d --build
	@echo "$(GREEN)✓ 生产环境重建完成$(NC)"

# 重建开发环境
rebuild-dev: check-env check-dotenv-dev
	@echo "$(BLUE)重建开发环境...$(NC)"
	docker compose -f docker-compose.dev.yml up -d --build
	@echo "$(GREEN)✓ 开发环境重建完成$(NC)"

# 重建指定服务
rebuild-service-%: check-env
	@echo "$(BLUE)重建服务: $*$(NC)"
	@if [ -f ".env" ]; then \
		docker compose -f docker-compose.prod.yml up -d --build $*; \
	else \
		echo "$(RED)未找到 .env 文件$(NC)"; \
		exit 1; \
	fi

# 显示状态
status:
	@echo "$(BLUE)=== 生产环境状态 ===$(NC)"
	@docker compose -f docker-compose.prod.yml ps 2>/dev/null || echo "未运行"
	@echo ""
	@echo "$(BLUE)=== 开发环境状态 ===$(NC)"
	@docker compose -f docker-compose.dev.yml ps 2>/dev/null || echo "未运行"
	@echo ""
	@echo "$(BLUE)=== 网络状态 ===$(NC)"
	@docker network ls | grep chat2network || echo "未找到 chat2network"
	@echo ""
	@echo "$(BLUE)=== 磁盘使用 ===$(NC)"
	@docker system df

# 清理所有数据
cleanup:
	@echo "$(RED)警告: 这将删除所有容器、网络和数据卷！$(NC)"
	@read -p "确定要继续吗？(y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)清理生产环境...$(NC)"; \
		docker compose -f docker-compose.prod.yml down -v 2>/dev/null || true; \
		echo "$(BLUE)清理开发环境...$(NC)"; \
		docker compose -f docker-compose.dev.yml down -v 2>/dev/null || true; \
		echo "$(BLUE)清理未使用的镜像...$(NC)"; \
		docker image prune -a -f; \
		echo "$(BLUE)清理未使用的卷...$(NC)"; \
		docker volume prune -f; \
		echo "$(GREEN)✓ 清理完成！$(NC)"; \
	else \
		echo "$(YELLOW)已取消清理操作$(NC)"; \
	fi

# 初始化配置
setup:
	@echo "$(BLUE)初始化配置...$(NC)"
	@if [ ! -f ".env" ]; then \
		echo "创建 .env"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ 已创建 .env，请编辑配置$(NC)"; \
	else \
		echo "$(YELLOW).env 已存在，跳过创建$(NC)"; \
	fi
	@if [ ! -f ".env.dev" ]; then \
		echo "创建 .env.dev"; \
		cp .env.example .env.dev; \
		echo "$(GREEN)✓ 已创建 .env.dev，请编辑配置$(NC)"; \
	else \
		echo "$(YELLOW).env.dev 已存在，跳过创建$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)初始化完成！$(NC)"
	@echo "请编辑 .env 和 .env.dev 文件配置密码等信息"

# 查看容器资源使用
resources:
	@echo "$(BLUE)=== 容器资源使用情况 ===$(NC)"
	@docker stats --no-stream --format "table {{.Container}}\t{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# 查看所有镜像
images:
	@echo "$(BLUE)=== Docker 镜像列表 ===$(NC)"
	@docker images | grep chat2anything || echo "未找到相关镜像"

# 查看所有卷
volumes:
	@echo "$(BLUE)=== Docker 卷列表 ===$(NC)"
	@docker volume ls | grep -E "chat2anything|milvus|mysql|es" || echo "未找到相关卷"

# 备份数据
backup:
	@echo "$(BLUE)备份数据...$(NC)"
	@mkdir -p backup
	@echo "备份功能需要根据实际需求实现"
	@echo "$(GREEN)备份目录已创建: backup/$(NC)"

# 更新镜像
update: check-env
	@echo "$(BLUE)更新镜像...$(NC)"
	@docker compose -f docker-compose.prod.yml pull
	@docker compose -f docker-compose.dev.yml pull
	@echo "$(GREEN)镜像更新完成$(NC)"
