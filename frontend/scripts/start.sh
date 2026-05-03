#!/bin/bash
# 一键启动前后端服务

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "========================================="
echo " 校园学术智能RAG检索系统 - 一键启动"
echo "========================================="

# 构建前端（如果需要）
if [ ! -d "$FRONTEND_DIR/dist" ]; then
    echo "[1/3] 构建前端..."
    cd "$FRONTEND_DIR"
    npm install
    npm run build
else
    echo "[1/3] 前端已构建，跳过（如需重新构建，删除 frontend/dist 目录）"
fi

# 启动后端（前端静态文件由后端托管）
echo "[2/3] 启动后端服务..."
cd "$PROJECT_ROOT"

# 将前端dist目录链接到后端静态文件目录
export FRONTEND_DIST="$FRONTEND_DIR/dist"

echo "[3/3] 启动完成，访问 http://localhost:8000"
echo "========================================="

python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
