FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Poetry
RUN pip install poetry==1.8.3

# 复制依赖文件
COPY pyproject.toml poetry.lock* ./

# 安装依赖（不安装dev依赖）
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 复制项目代码
COPY . .

# 创建数据目录
RUN mkdir -p data/raw_documents data/processed_chunks data/vector_index logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
