#!/bin/bash

# Chat2Anything Docker 管理脚本
# 提供更细粒度的控制

set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(dirname "$SCRIPT_DIR")

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 服务定义
SERVICES=("mysql" "elasticsearch" "etcd" "minio" "standalone" "chat2anything_backend" "chat2anything_front" "nginx")

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

get_dc_cmd() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    else
        echo "docker compose"
    fi
}

show_usage() {
    echo "Chat2Anything Docker 管理工具"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  start [prod|dev] [service...]  启动服务 (默认启动全部)"
    echo "  stop [prod|dev] [service...]   停止服务 (默认停止全部)"
    echo "  restart [prod|dev] [service]   重启服务"
    echo "  logs [prod|dev] [service]      查看日志"
    echo "  ps [prod|dev]                  查看状态"
    echo "  build [prod|dev] [service]     重建镜像"
    echo "  exec [prod|dev] [service]      进入容器"
    echo "  pull [prod|dev]                拉取镜像"
    echo "  clean                          清理数据"
    echo ""
    echo "示例:"
    echo "  $0 start prod                  # 启动生产环境"
    echo "  $0 start dev backend           # 启动开发环境的后端"
    echo "  $0 logs prod mysql             # 查看生产环境 MySQL 日志"
    echo "  $0 exec dev backend            # 进入开发环境后端容器"
}

start_services() {
    local env=$1
    shift
    local services=("$@")

    cd "$SCRIPT_DIR"
    local dc_cmd=$(get_dc_cmd)
    local compose_file="docker-compose.${env}.yml"

    if [ ! -f "$compose_file" ]; then
        log_error "未找到配置文件: $compose_file"
        exit 1
    fi

    if [ ${#services[@]} -eq 0 ]; then
        log_info "启动 $env 环境所有服务..."
        $dc_cmd -f "$compose_file" up -d
    else
        log_info "启动 $env 环境服务: ${services[*]}"
        $dc_cmd -f "$compose_file" up -d "${services[@]}"
    fi

    log_success "启动完成"
}

stop_services() {
    local env=$1
    shift
    local services=("$@")

    cd "$SCRIPT_DIR"
    local dc_cmd=$(get_dc_cmd)
    local compose_file="docker-compose.${env}.yml"

    if [ ! -f "$compose_file" ]; then
        log_error "未找到配置文件: $compose_file"
        exit 1
    fi

    if [ ${#services[@]} -eq 0 ]; then
        log_info "停止 $env 环境所有服务..."
        $dc_cmd -f "$compose_file" down
    else
        log_info "停止 $env 环境服务: ${services[*]}"
        $dc_cmd -f "$compose_file" stop "${services[@]}"
    fi

    log_success "停止完成"
}

restart_service() {
    local env=$1
    local service=$2

    cd "$SCRIPT_DIR"
    local dc_cmd=$(get_dc_cmd)
    local compose_file="docker-compose.${env}.yml"

    if [ ! -f "$compose_file" ]; then
        log_error "未找到配置文件: $compose_file"
        exit 1
    fi

    if [ -z "$service" ]; then
        log_error "请指定要重启的服务名称"
        exit 1
    fi

    log_info "重启 $env 环境服务: $service"
    $dc_cmd -f "$compose_file" restart "$service"
    log_success "重启完成"
}

show_logs() {
    local env=$1
    local service=$2

    cd "$SCRIPT_DIR"
    local dc_cmd=$(get_dc_cmd)
    local compose_file="docker-compose.${env}.yml"

    if [ ! -f "$compose_file" ]; then
        log_error "未找到配置文件: $compose_file"
        exit 1
    fi

    if [ -z "$service" ]; then
        $dc_cmd -f "$compose_file" logs -f
    else
        $dc_cmd -f "$compose_file" logs -f "$service"
    fi
}

show_status() {
    local env=$1

    cd "$SCRIPT_DIR"
    local dc_cmd=$(get_dc_cmd)

    if [ -z "$env" ]; then
        echo "=== 生产环境 ==="
        $dc_cmd -f docker-compose.prod.yml ps 2>/dev/null || echo "未运行"
        echo ""
        echo "=== 开发环境 ==="
        $dc_cmd -f docker-compose.dev.yml ps 2>/dev/null || echo "未运行"
    else
        local compose_file="docker-compose.${env}.yml"
        if [ ! -f "$compose_file" ]; then
            log_error "未找到配置文件: $compose_file"
            exit 1
        fi
        $dc_cmd -f "$compose_file" ps
    fi
}

build_services() {
    local env=$1
    local service=$2

    cd "$SCRIPT_DIR"
    local dc_cmd=$(get_dc_cmd)
    local compose_file="docker-compose.${env}.yml"

    if [ ! -f "$compose_file" ]; then
        log_error "未找到配置文件: $compose_file"
        exit 1
    fi

    if [ -z "$service" ]; then
        log_info "重建 $env 环境所有服务..."
        $dc_cmd -f "$compose_file" up -d --build
    else
        log_info "重建 $env 环境服务: $service"
        $dc_cmd -f "$compose_file" up -d --build "$service"
    fi

    log_success "重建完成"
}

exec_service() {
    local env=$1
    local service=$2

    cd "$SCRIPT_DIR"
    local dc_cmd=$(get_dc_cmd)
    local compose_file="docker-compose.${env}.yml"

    if [ ! -f "$compose_file" ]; then
        log_error "未找到配置文件: $compose_file"
        exit 1
    fi

    if [ -z "$service" ]; then
        log_error "请指定要进入的容器名称"
        exit 1
    fi

    # 确定容器名称
    local container_name
    case "$service" in
        backend|chat2anything_backend)
            container_name="chat2anything_${env}_backend" 2>/dev/null || container_name="chat2anything_backend_${env}" ;;
        frontend|chat2anything_front)
            container_name="chat2anything_${env}_frontend" 2>/dev/null || container_name="chat2anything_front_${env}" ;;
        mysql)
            container_name="chat2anything_${env}_db" ;;
        elasticsearch|es)
            container_name="chat2anything_${env}_es" ;;
        *)
            container_name="$service" ;;
    esac

    # 尝试进入容器
    if docker exec -it "$container_name" bash 2>/dev/null || docker exec -it "$container_name" sh 2>/dev/null; then
        log_success "已进入容器: $container_name"
    else
        log_error "无法进入容器: $container_name"
        log_info "可用容器:"
        $dc_cmd -f "$compose_file" ps --format "table {{.Names}}\t{{.Status}}"
    fi
}

pull_images() {
    local env=$1

    cd "$SCRIPT_DIR"
    local dc_cmd=$(get_dc_cmd)
    local compose_file="docker-compose.${env}.yml"

    if [ ! -f "$compose_file" ]; then
        log_error "未找到配置文件: $compose_file"
        exit 1
    fi

    log_info "拉取 $env 环境镜像..."
    $dc_cmd -f "$compose_file" pull
    log_success "镜像拉取完成"
}

clean_all() {
    log_warning "这将删除所有容器、网络和数据卷！"
    read -p "确定要继续吗？(y/N): " confirm

    if [[ $confirm =~ ^[Yy]$ ]]; then
        cd "$SCRIPT_DIR"
        local dc_cmd=$(get_dc_cmd)

        log_info "清理生产环境..."
        $dc_cmd -f docker-compose.prod.yml down -v 2>/dev/null || true

        log_info "清理开发环境..."
        $dc_cmd -f docker-compose.dev.yml down -v 2>/dev/null || true

        log_info "清理未使用的镜像..."
        docker image prune -a -f

        log_info "清理未使用的卷..."
        docker volume prune -f

        log_info "清理未使用的网络..."
        docker network prune -f

        log_success "清理完成！"
    else
        log_info "已取消清理操作"
    fi
}

# 主逻辑
case "$1" in
    start)
        if [ -z "$2" ]; then
            log_error "请指定环境: prod 或 dev"
            exit 1
        fi
        shift 2
        start_services "$@" ;;
    stop)
        if [ -z "$2" ]; then
            log_error "请指定环境: prod 或 dev"
            exit 1
        fi
        shift 2
        stop_services "$@" ;;
    restart)
        if [ -z "$2" ]; then
            log_error "请指定环境: prod 或 dev"
            exit 1
        fi
        shift 2
        restart_service "$@" ;;
    logs)
        if [ -z "$2" ]; then
            log_error "请指定环境: prod 或 dev"
            exit 1
        fi
        shift 2
        show_logs "$@" ;;
    ps|status)
        shift
        show_status "$@" ;;
    build)
        if [ -z "$2" ]; then
            log_error "请指定环境: prod 或 dev"
            exit 1
        fi
        shift 2
        build_services "$@" ;;
    exec)
        if [ -z "$2" ]; then
            log_error "请指定环境: prod 或 dev"
            exit 1
        fi
        shift 2
        exec_service "$@" ;;
    pull)
        if [ -z "$2" ]; then
            log_error "请指定环境: prod 或 dev"
            exit 1
        fi
        shift
        pull_images "$@" ;;
    clean)
        clean_all ;;
    help|--help|-h)
        show_usage ;;
    *)
        if [ -z "$1" ]; then
            show_usage
        else
            log_error "未知命令: $1"
            echo ""
            show_usage
            exit 1
        fi ;;
esac
