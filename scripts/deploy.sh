#!/bin/bash
# 校园学术智能RAG检索系统 - 部署脚本

set -e

echo "=========================================="
echo "校园学术智能RAG检索系统 - 部署"
echo "=========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: docker-compose未安装，请先安装docker-compose"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "警告: .env文件不存在，正在从.env.example复制..."
        cp .env.example .env
        echo "请编辑.env文件填入实际配置"
        exit 1
    else
        echo "错误: .env.example文件不存在"
        exit 1
    fi
fi

# 创建必要的目录
mkdir -p data/raw_documents data/processed_chunks data/vector_index logs

# 构建并启动服务
echo "正在构建Docker镜像..."
docker-compose build

echo "正在启动服务..."
docker-compose up -d

echo "=========================================="
echo "部署完成！"
echo "API服务地址: http://localhost:8000"
echo "API文档地址: http://localhost:8000/docs"
echo "=========================================="

# 显示服务状态
docker-compose ps
