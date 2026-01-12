#!/bin/bash

# Chat2Anything 一键启动脚本
# 支持生产环境和开发环境

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
DOCKER_DIR="$PROJECT_ROOT/docker"

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    print_info "Docker 版本: $(docker --version)"
}

# 检查 Docker Compose 是否安装
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    if command -v docker-compose &> /dev/null; then
        print_info "Docker Compose 版本: $(docker-compose --version)"
    else
        print_info "Docker Compose 版本: $(docker compose version)"
    fi
}

# 获取 Docker Compose 命令
get_docker_compose_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    else
        echo "docker compose"
    fi
}

# 检查 .env 文件
check_env_file() {
    local env_file="$1"
    local example_file="$2"

    if [ ! -f "$env_file" ]; then
        print_warning "未找到 $env_file，正在从模板创建..."
        if [ -f "$example_file" ]; then
            cp "$example_file" "$env_file"
            print_info "已创建 $env_file，请先编辑该文件配置密码等信息"
            print_warning "请先编辑 $env_file 文件，然后重新运行此脚本"
            exit 1
        else
            print_error "未找到模板文件 $example_file"
            exit 1
        fi
    fi
}

# 检查端口占用
check_port() {
    local port=$1
    if netstat -tuln 2>/dev/null | grep -q ":$port " || lsof -i :$port 2>/dev/null | grep -q LISTEN; then
        print_warning "端口 $port 已被占用，可能导致启动失败"
        return 1
    fi
    return 0
}

# 检查必要端口
check_ports() {
    print_info "检查端口占用情况..."

    # 读取 .env 文件中的端口配置
    if [ -f "$DOCKER_DIR/.env" ]; then
        source "$DOCKER_DIR/.env"

        check_port "${WEB_PORT:-9966}"
        check_port "${MYSQL_PORT:-3306}"
        check_port "${ES_BASE_PORT:-9200}"
        check_port "${MILVUS_PORT:-19530}"
    fi
}

# 创建网络
create_network() {
    local dc_cmd=$(get_docker_compose_cmd)
    if ! docker network ls | grep -q "chat2network"; then
        print_info "创建 Docker 网络 chat2network..."
        docker network create chat2network
    fi
}

# 启动生产环境
start_production() {
    print_info "启动生产环境..."

    cd "$DOCKER_DIR"

    # 检查 .env 文件
    check_env_file ".env" ".env.example"

    # 检查端口
    check_ports

    # 创建网络
    create_network

    # 启动服务
    local dc_cmd=$(get_docker_compose_cmd)
    print_info "正在构建和启动所有服务 (这可能需要几分钟)..."

    $dc_cmd -f docker-compose.prod.yml up -d --build

    print_success "生产环境启动完成！"
    print_info "访问地址: http://localhost:${WEB_PORT:-9966}"
    print_info "后端API: http://localhost:${WEB_PORT:-9966}/api/"
    print_info "MySQL端口: ${MYSQL_PORT:-3306}"
    print_info "Elasticsearch端口: ${ES_BASE_PORT:-9200}"
    print_info "Milvus端口: ${MILVUS_PORT:-19530}"

    echo ""
    print_info "查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    print_info "停止服务: docker-compose -f docker-compose.prod.yml down"
}

# 启动开发环境
start_development() {
    print_info "启动开发环境..."

    cd "$DOCKER_DIR"

    # 检查 .env.dev 文件
    check_env_file ".env.dev" ".env.example"

    # 检查端口
    check_ports

    # 创建网络
    create_network

    # 启动服务
    local dc_cmd=$(get_docker_compose_cmd)
    print_info "正在构建和启动开发服务..."

    $dc_cmd -f docker-compose.dev.yml up -d --build

    print_success "开发环境启动完成！"
    print_info "前端开发服务器: http://localhost:3000"
    print_info "后端API: http://localhost:9988"
    print_info "Nginx代理: http://localhost:${WEB_PORT:-9966}"
    print_info "调试端口: 5678 (VS Code 调试)"

    echo ""
    print_info "查看日志: docker-compose -f docker-compose.dev.yml logs -f"
    print_info "停止服务: docker-compose -f docker-compose.dev.yml down"
    print_info "重启服务: docker-compose -f docker-compose.dev.yml restart <service_name>"
}

# 停止所有服务
stop_all() {
    print_info "停止所有服务..."

    cd "$DOCKER_DIR"
    local dc_cmd=$(get_docker_compose_cmd)

    # 停止生产环境
    if [ -f "docker-compose.prod.yml" ]; then
        $dc_cmd -f docker-compose.prod.yml down
    fi

    # 停止开发环境
    if [ -f "docker-compose.dev.yml" ]; then
        $dc_cmd -f docker-compose.dev.yml down
    fi

    print_success "所有服务已停止"
}

# 查看日志
show_logs() {
    local env=$1
    cd "$DOCKER_DIR"
    local dc_cmd=$(get_docker_compose_cmd)

    if [ "$env" = "prod" ]; then
        $dc_cmd -f docker-compose.prod.yml logs -f
    elif [ "$env" = "dev" ]; then
        $dc_cmd -f docker-compose.dev.yml logs -f
    else
        print_error "请指定环境: prod 或 dev"
        exit 1
    fi
}

# 重建服务
rebuild() {
    local env=$1
    local service=$2

    cd "$DOCKER_DIR"
    local dc_cmd=$(get_docker_compose_cmd)

    if [ "$env" = "prod" ]; then
        if [ -z "$service" ]; then
            $dc_cmd -f docker-compose.prod.yml up -d --build
        else
            $dc_cmd -f docker-compose.prod.yml up -d --build "$service"
        fi
    elif [ "$env" = "dev" ]; then
        if [ -z "$service" ]; then
            $dc_cmd -f docker-compose.dev.yml up -d --build
        else
            $dc_cmd -f docker-compose.dev.yml up -d --build "$service"
        fi
    else
        print_error "请指定环境: prod 或 dev"
        exit 1
    fi

    print_success "重建完成"
}

# 显示状态
show_status() {
    cd "$DOCKER_DIR"
    local dc_cmd=$(get_docker_compose_cmd)

    echo -e "${BLUE}=== 生产环境状态 ===${NC}"
    $dc_cmd -f docker-compose.prod.yml ps 2>/dev/null || echo "未运行"

    echo ""
    echo -e "${BLUE}=== 开发环境状态 ===${NC}"
    $dc_cmd -f docker-compose.dev.yml ps 2>/dev/null || echo "未运行"

    echo ""
    echo -e "${BLUE}=== 网络状态 ===${NC}"
    docker network ls | grep chat2network || echo "未找到 chat2network"

    echo ""
    echo -e "${BLUE}=== 磁盘使用 ===${NC}"
    docker system df
}

# 清理数据
cleanup() {
    print_warning "这将删除所有容器、网络和数据卷！"
    read -p "确定要继续吗？(y/N): " confirm

    if [[ $confirm =~ ^[Yy]$ ]]; then
        cd "$DOCKER_DIR"
        local dc_cmd=$(get_docker_compose_cmd)

        print_info "清理生产环境..."
        $dc_cmd -f docker-compose.prod.yml down -v 2>/dev/null || true

        print_info "清理开发环境..."
        $dc_cmd -f docker-compose.dev.yml down -v 2>/dev/null || true

        print_info "清理未使用的镜像..."
        docker image prune -a -f

        print_info "清理未使用的卷..."
        docker volume prune -f

        print_success "清理完成！"
    else
        print_info "已取消清理操作"
    fi
}

# 显示帮助
show_help() {
    echo "Chat2Anything Docker 一键启动脚本"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  prod          启动生产环境"
    echo "  dev           启动开发环境"
    echo "  stop          停止所有服务"
    echo "  logs [prod|dev] 查看日志"
    echo "  rebuild [prod|dev] [service] 重建服务"
    echo "  status        显示服务状态"
    echo "  cleanup       清理所有数据和容器"
    echo "  help          显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 prod              # 启动生产环境"
    echo "  $0 dev               # 启动开发环境"
    echo "  $0 logs prod         # 查看生产环境日志"
    echo "  $0 rebuild dev       # 重建开发环境"
    echo "  $0 status            # 查看所有服务状态"
}

# 主函数
main() {
    local command=$1

    case "$command" in
        prod)
            check_docker
            check_docker_compose
            start_production
            ;;
        dev)
            check_docker
            check_docker_compose
            start_development
            ;;
        stop)
            stop_all
            ;;
        logs)
            if [ -z "$2" ]; then
                print_error "请指定环境: prod 或 dev"
                exit 1
            fi
            show_logs "$2"
            ;;
        rebuild)
            if [ -z "$2" ]; then
                print_error "请指定环境: prod 或 dev"
                exit 1
            fi
            check_docker
            check_docker_compose
            rebuild "$2" "$3"
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 如果没有参数，显示帮助
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

main "$@"
