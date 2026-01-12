@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Chat2Anything 一键启动脚本 (Windows)
REM 支持生产环境和开发环境

REM 颜色定义
set "COLOR_RED=0c"
set "COLOR_GREEN=0a"
set "COLOR_YELLOW=0e"
set "COLOR_BLUE=0b"
set "COLOR_WHITE=07"

REM 获取脚本所在目录
set "DOCKER_DIR=%~dp0"
set "PROJECT_ROOT=%DOCKER_DIR:~0,-1%"
for %%I in ("%PROJECT_ROOT%") do set "PROJECT_ROOT=%%~dpI"

REM 打印带颜色的信息
:print_info
    echo %COLOR_BLUE%[INFO]%COLOR_WHITE% %~1
    goto :eof

:print_success
    echo %COLOR_GREEN%[SUCCESS]%COLOR_WHITE% %~1
    goto :eof

:print_warning
    echo %COLOR_YELLOW%[WARNING]%COLOR_WHITE% %~1
    goto :eof

:print_error
    echo %COLOR_RED%[ERROR]%COLOR_WHITE% %~1
    goto :eof

REM 检查 Docker 是否安装
:check_docker
    docker --version >nul 2>&1
    if !errorlevel! neq 0 (
        call :print_error "Docker 未安装，请先安装 Docker Desktop"
        exit /b 1
    )
    for /f "tokens=3" %%A in ('docker --version') do set "DOCKER_VER=%%A"
    call :print_info "Docker 版本: !DOCKER_VER!"
    goto :eof

REM 检查 Docker Compose 是否安装
:check_docker_compose
    docker compose version >nul 2>&1
    if !errorlevel! neq 0 (
        call :print_error "Docker Compose 未安装，请先安装 Docker Desktop"
        exit /b 1
    )
    for /f "tokens=4" %%A in ('docker compose version') do set "DC_VER=%%A"
    call :print_info "Docker Compose 版本: !DC_VER!"
    goto :eof

REM 检查 .env 文件
:check_env_file
    set "env_file=%~1"
    set "example_file=%~2"

    if not exist "!env_file!" (
        call :print_warning "未找到 !env_file!，正在从模板创建..."
        if exist "!example_file!" (
            copy "!example_file!" "!env_file!" >nul
            call :print_info "已创建 !env_file!，请先编辑该文件配置密码等信息"
            call :print_warning "请先编辑 !env_file! 文件，然后重新运行此脚本"
            pause
            exit /b 1
        ) else (
            call :print_error "未找到模板文件 !example_file!"
            exit /b 1
        )
    )
    goto :eof

REM 检查端口占用
:check_port
    set "port=%~1"
    netstat -ano | findstr ":!port! " >nul 2>&1
    if !errorlevel! equ 0 (
        call :print_warning "端口 !port! 已被占用，可能导致启动失败"
    )
    goto :eof

REM 检查必要端口
:check_ports
    call :print_info "检查端口占用情况..."

    if exist "%DOCKER_DIR%\.env" (
        for /f "tokens=1,2* delims==" %%A in (%DOCKER_DIR%\.env) do (
            if "%%A"=="WEB_PORT" set "WEB_PORT=%%B"
            if "%%A"=="MYSQL_PORT" set "MYSQL_PORT=%%B"
            if "%%A"=="ES_BASE_PORT" set "ES_BASE_PORT=%%B"
            if "%%A"=="MILVUS_PORT" set "MILVUS_PORT=%%B"
        )

        if not defined WEB_PORT set "WEB_PORT=9966"
        if not defined MYSQL_PORT set "MYSQL_PORT=3306"
        if not defined ES_BASE_PORT set "ES_BASE_PORT=9200"
        if not defined MILVUS_PORT set "MILVUS_PORT=19530"

        call :check_port !WEB_PORT!
        call :check_port !MYSQL_PORT!
        call :check_port !ES_BASE_PORT!
        call :check_port !MILVUS_PORT!
    )
    goto :eof

REM 创建网络
:create_network
    docker network ls | findstr "chat2network" >nul 2>&1
    if !errorlevel! neq 0 (
        call :print_info "创建 Docker 网络 chat2network..."
        docker network create chat2network >nul 2>&1
    )
    goto :eof

REM 启动生产环境
:start_production
    call :print_info "启动生产环境..."

    cd /d "%DOCKER_DIR%"

    call :check_env_file ".env" ".env.example"
    call :check_ports
    call :create_network

    call :print_info "正在构建和启动所有服务 (这可能需要几分钟)..."
    docker compose -f docker-compose.prod.yml up -d --build

    if !errorlevel! equ 0 (
        call :print_success "生产环境启动完成！"
        echo.
        call :print_info "访问地址: http://localhost:!WEB_PORT!"
        call :print_info "后端API: http://localhost:!WEB_PORT!/api/"
        call :print_info "MySQL端口: !MYSQL_PORT!"
        call :print_info "Elasticsearch端口: !ES_BASE_PORT!"
        call :print_info "Milvus端口: !MILVUS_PORT!"
        echo.
        call :print_info "查看日志: docker compose -f docker-compose.prod.yml logs -f"
        call :print_info "停止服务: docker compose -f docker-compose.prod.yml down"
    ) else (
        call :print_error "启动失败，请检查日志"
        exit /b 1
    )
    goto :eof

REM 启动开发环境
:start_development
    call :print_info "启动开发环境..."

    cd /d "%DOCKER_DIR%"

    call :check_env_file ".env.dev" ".env.example"
    call :check_ports
    call :create_network

    call :print_info "正在构建和启动开发服务..."
    docker compose -f docker-compose.dev.yml up -d --build

    if !errorlevel! equ 0 (
        call :print_success "开发环境启动完成！"
        echo.
        call :print_info "前端开发服务器: http://localhost:3000"
        call :print_info "后端API: http://localhost:9988"
        call :print_info "Nginx代理: http://localhost:!WEB_PORT!"
        call :print_info "调试端口: 5678 (VS Code 调试)"
        echo.
        call :print_info "查看日志: docker compose -f docker-compose.dev.yml logs -f"
        call :print_info "停止服务: docker compose -f docker-compose.dev.yml down"
        call :print_info "重启服务: docker compose -f docker-compose.dev.yml restart <service_name>"
    ) else (
        call :print_error "启动失败，请检查日志"
        exit /b 1
    )
    goto :eof

REM 停止所有服务
:stop_all
    call :print_info "停止所有服务..."

    cd /d "%DOCKER_DIR%"

    if exist "docker-compose.prod.yml" (
        docker compose -f docker-compose.prod.yml down >nul 2>&1
    )

    if exist "docker-compose.dev.yml" (
        docker compose -f docker-compose.dev.yml down >nul 2>&1
    )

    call :print_success "所有服务已停止"
    goto :eof

REM 查看日志
:show_logs
    set "env=%~1"

    cd /d "%DOCKER_DIR%"

    if "!env!"=="prod" (
        docker compose -f docker-compose.prod.yml logs -f
    ) else if "!env!"=="dev" (
        docker compose -f docker-compose.dev.yml logs -f
    ) else (
        call :print_error "请指定环境: prod 或 dev"
        exit /b 1
    )
    goto :eof

REM 重建服务
:rebuild
    set "env=%~1"
    set "service=%~2"

    cd /d "%DOCKER_DIR%"

    if "!env!"=="prod" (
        if "!service!"=="" (
            docker compose -f docker-compose.prod.yml up -d --build
        ) else (
            docker compose -f docker-compose.prod.yml up -d --build "!service!"
        )
    ) else if "!env!"=="dev" (
        if "!service!"=="" (
            docker compose -f docker-compose.dev.yml up -d --build
        ) else (
            docker compose -f docker-compose.dev.yml up -d --build "!service!"
        )
    ) else (
        call :print_error "请指定环境: prod 或 dev"
        exit /b 1
    )

    if !errorlevel! equ 0 (
        call :print_success "重建完成"
    ) else (
        call :print_error "重建失败"
        exit /b 1
    )
    goto :eof

REM 显示状态
:show_status
    cd /d "%DOCKER_DIR%"

    echo %COLOR_BLUE%=== 生产环境状态 ===%COLOR_WHITE%
    docker compose -f docker-compose.prod.yml ps 2>nul || echo 未运行

    echo.
    echo %COLOR_BLUE%=== 开发环境状态 ===%COLOR_WHITE%
    docker compose -f docker-compose.dev.yml ps 2>nul || echo 未运行

    echo.
    echo %COLOR_BLUE%=== 网络状态 ===%COLOR_WHITE%
    docker network ls | findstr "chat2network" || echo 未找到 chat2network

    echo.
    echo %COLOR_BLUE%=== 磁盘使用 ===%COLOR_WHITE%
    docker system df
    goto :eof

REM 清理数据
:cleanup
    call :print_warning "这将删除所有容器、网络和数据卷！"
    set /p "confirm=确定要继续吗？(y/N): "

    if /i "!confirm!"=="y" (
        cd /d "%DOCKER_DIR%"

        call :print_info "清理生产环境..."
        docker compose -f docker-compose.prod.yml down -v 2>nul

        call :print_info "清理开发环境..."
        docker compose -f docker-compose.dev.yml down -v 2>nul

        call :print_info "清理未使用的镜像..."
        docker image prune -a -f

        call :print_info "清理未使用的卷..."
        docker volume prune -f

        call :print_success "清理完成！"
    ) else (
        call :print_info "已取消清理操作"
    )
    goto :eof

REM 显示帮助
:show_help
    echo Chat2Anything Docker 一键启动脚本
    echo.
    echo 用法: %~nx0 [命令] [参数]
    echo.
    echo 命令:
    echo   prod          启动生产环境
    echo   dev           启动开发环境
    echo   stop          停止所有服务
    echo   logs [prod^|dev] 查看日志
    echo   rebuild [prod^|dev] [service] 重建服务
    echo   status        显示服务状态
    echo   cleanup       清理所有数据和容器
    echo   help          显示此帮助信息
    echo.
    echo 示例:
    echo   %~nx0 prod              # 启动生产环境
    echo   %~nx0 dev               # 启动开发环境
    echo   %~nx0 logs prod         # 查看生产环境日志
    echo   %~nx0 rebuild dev       # 重建开发环境
    echo   %~nx0 status            # 查看所有服务状态
    goto :eof

REM 主函数
set "command=%~1"

if "%command%"=="" (
    call :show_help
    exit /b 0
)

if "%command%"=="prod" (
    call :check_docker
    call :check_docker_compose
    call :start_production
) else if "%command%"=="dev" (
    call :check_docker
    call :check_docker_compose
    call :start_development
) else if "%command%"=="stop" (
    call :stop_all
) else if "%command%"=="logs" (
    if "%~2"=="" (
        call :print_error "请指定环境: prod 或 dev"
        exit /b 1
    )
    call :show_logs "%~2"
) else if "%command%"=="rebuild" (
    if "%~2"=="" (
        call :print_error "请指定环境: prod 或 dev"
        exit /b 1
    )
    call :check_docker
    call :check_docker_compose
    call :rebuild "%~2" "%~3"
) else if "%command%"=="status" (
    call :show_status
) else if "%command%"=="cleanup" (
    call :cleanup
) else if "%command%"=="help" (
    call :show_help
) else (
    call :print_error "未知命令: %command%"
    echo.
    call :show_help
    exit /b 1
)
