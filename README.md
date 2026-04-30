# 校园学术智能RAG检索系统

专为校园学习科研场景打造的私有化RAG问答系统，将课程PPT、课本PDF、学术论文等学术文档转化为可精准检索的知识库。

## 核心特性

- **多格式文档解析**：支持PDF、PPTX、DOCX、Markdown等校园常见文档格式
- **智能分片策略**：按句分片+滑动窗口，保留学术文档语义完整性
- **多路检索融合**：向量语义检索 + BM25关键词检索 + 元数据过滤
- **多Agent协作**：MoE式架构，场景专属专家Agent
- **抗幻觉机制**：知识校验、引用溯源，确保回答100%基于知识库
- **完全私有化**：支持离线部署，数据本地存储，适配校园内网环境

---

## 一、环境准备

### 1.1 系统要求

- **操作系统**：Linux / macOS / Windows (WSL2)
- **Python版本**：3.10 或更高版本
- **内存**：建议 8GB 以上（加载嵌入模型需要）
- **磁盘空间**：至少 2GB（模型和依赖）

### 1.2 安装 Python（如未安装）

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# macOS (使用 Homebrew)
brew install python@3.10

# 验证安装
python3 --version
```

### 1.3 安装 Poetry（依赖管理工具）

```bash
# 安装 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 验证安装（需要重新打开终端或执行以下命令）
export PATH="$HOME/.local/bin:$PATH"
poetry --version
```

---

## 二、项目安装与配置

### 2.1 获取项目代码

```bash
# 进入项目目录
cd campus-academic-rag

# 如果是从Git克隆
# git clone <repository-url>
# cd campus-academic-rag
```

### 2.2 安装项目依赖

```bash
# 使用 Poetry 安装依赖（推荐）
poetry install

# 或者使用 pip 安装（如果不使用 Poetry）
pip install pdfplumber python-pptx python-docx sentence-transformers chromadb rank-bm25 jieba fastapi uvicorn pydantic openai loguru python-dotenv
```

### 2.3 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用 vim、VS Code 等编辑器
```

**必须配置的关键项：**

```bash
# ============ LLM配置（必填） ============
# 使用 OpenAI 兼容 API（支持多种服务）
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx  # 替换为你的API Key
LLM_BASE_URL=https://api.openai.com/v1   # 或其他兼容API地址
LLM_MODEL=gpt-4o                          # 或 gpt-3.5-turbo、claude-3-sonnet 等

# ============ 嵌入模型配置 ============
# 方式1：使用在线模型（首次需要下载，约500MB）
EMBEDDING_MODEL_NAME=BAAI/bge-base-zh-v1.5

# 方式2：使用本地模型（离线环境推荐）
# EMBEDDING_MODEL_PATH=./models/bge-base-zh-v1.5

EMBEDDING_DEVICE=cpu  # cpu 或 cuda（如果有GPU）

# ============ 检索配置 ============
RETRIEVAL_TOP_K=10          # 每次检索返回的结果数量
VECTOR_WEIGHT=0.7           # 向量检索权重
BM25_WEIGHT=0.3             # 关键词检索权重
```

**LLM API 配置示例：**

```bash
# OpenAI 官方
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-xxxxxxxx
LLM_MODEL=gpt-4o

# 国内代理/兼容服务（如 DeepSeek、智谱AI 等）
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=your-key
LLM_MODEL=deepseek-chat

# 本地部署（如 Ollama、vLLM 等）
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=qwen2:7b
```

---

## 三、启动系统

### 3.1 初始化项目

```bash
# 运行初始化脚本，检查环境和依赖
python3 scripts/init_project.py
```

输出示例：
```
==================================================
校园学术智能RAG检索系统 - 项目初始化
版本: 1.0.0
==================================================
目录已创建/确认: data/raw_documents
目录已创建/确认: data/processed_chunks
目录已创建/确认: data/vector_index
==================================================
项目初始化完成！
==================================================
```

### 3.2 启动 API 服务

```bash
# 方式1：直接启动
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# 方式2：使用 Poetry
poetry run uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# 方式3：后台运行
nohup python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &
```

### 3.3 验证服务启动

```bash
# 访问健康检查接口
curl http://localhost:8000/health

# 预期输出：
# {"status":"ok","version":"1.0.0","components":{...}}
```

**访问 API 文档：** 浏览器打开 http://localhost:8000/docs 可查看交互式 API 文档。

---

## 四、导入文档（构建知识库）

### 4.1 准备文档

将你的学术文档放入 `data/raw_documents/` 目录：

```bash
# 示例：复制文档到目录
cp ~/Downloads/机器学习.pdf data/raw_documents/
cp ~/Downloads/数据结构课件.pptx data/raw_documents/
cp ~/Downloads/论文_深度学习综述.pdf data/raw_documents/
```

**支持的文档格式：**
- PDF（教材、论文、课件导出）
- PPTX（课程PPT）
- DOCX（Word文档、讲义）
- Markdown（笔记、文档）
- TXT（纯文本）

### 4.2 通过 API 导入文档

```bash
# 导入单个文档
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{
    "doc_path": "data/raw_documents/机器学习.pdf",
    "course_name": "机器学习",
    "chapter": "第一章 绪论",
    "tags": ["机器学习", "人工智能"]
  }'
```

**预期响应：**
```json
{
  "success": true,
  "doc_id": "机器学习",
  "doc_name": "机器学习.pdf",
  "chunks_count": 156,
  "message": "文档处理成功: 机器学习.pdf"
}
```

### 4.3 批量导入文档（脚本方式）

```bash
# 处理目录下所有文档
python3 scripts/batch_process.py --input ./data/raw_documents
```

### 4.4 查看已导入的文档

```bash
# 查看系统统计信息
curl http://localhost:8000/stats
```

---

## 五、提问与查询

### 5.1 通过 API 提问

```bash
# 基本提问
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是梯度下降？",
    "top_k": 5,
    "scene_type": "general"
  }'
```

**预期响应：**
```json
{
  "answer": "梯度下降是一种优化算法，用于最小化损失函数。其核心思想是：\n\n1. **基本原理**：沿着损失函数梯度的反方向更新参数，逐步逼近最优解...\n\n2. **更新公式**：θ = θ - α * ∇J(θ)，其中 α 是学习率...\n\n[来源1: 机器学习.pdf, 第45页]",
  "citations": [
    {
      "citation_id": "cite_1",
      "doc_name": "机器学习.pdf",
      "page_number": 45,
      "relevance_score": 0.92
    }
  ],
  "confidence": 0.87,
  "retrieval_results": [...]
}
```

### 5.2 不同场景的提问

```bash
# 考点梳理场景
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "请梳理机器学习期末考试的重点知识点",
    "scene_type": "exam"
  }'

# 作业答疑场景
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "解释反向传播算法的推导过程",
    "scene_type": "homework"
  }'

# 论文解读场景
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "这篇论文的主要贡献是什么？",
    "scene_type": "paper"
  }'
```

### 5.3 带过滤条件的提问

```bash
# 只在特定课程的文档中检索
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是卷积神经网络？",
    "filter_metadata": {
      "course_name": "深度学习"
    }
  }'

# 只在特定文档类型中检索
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "数据结构的时间复杂度分析",
    "filter_metadata": {
      "doc_type": "pptx"
    }
  }'
```

### 5.4 多轮对话

```bash
# 带历史记录的提问
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "那它的收敛性如何证明？",
    "history": [
      {"query": "什么是梯度下降？", "answer": "梯度下降是..."}
    ]
  }'
```

---

## 六、使用 Python 脚本交互（推荐）

### 6.1 创建交互式查询脚本

```bash
cat > scripts/interactive_query.py << 'EOF'
"""交互式查询脚本"""

import requests
import json

API_BASE = "http://localhost:8000"

def upload_document(doc_path, course_name="", chapter=""):
    """上传文档"""
    response = requests.post(f"{API_BASE}/documents", json={
        "doc_path": doc_path,
        "course_name": course_name,
        "chapter": chapter,
    })
    return response.json()

def query(question, scene_type="general"):
    """提问"""
    response = requests.post(f"{API_BASE}/query", json={
        "query": question,
        "scene_type": scene_type,
        "top_k": 5,
    })
    return response.json()

def main():
    print("=" * 60)
    print("校园学术智能RAG检索系统 - 交互式查询")
    print("=" * 60)
    
    # 上传文档
    print("\n[步骤1] 上传文档")
    print("请输入文档路径（或输入 skip 跳过）：")
    doc_path = input("> ").strip()
    
    if doc_path and doc_path != "skip":
        course = input("课程名称（可选）: ").strip()
        result = upload_document(doc_path, course_name=course)
        print(f"上传结果: {result.get('message', '失败')}")
    
    # 开始提问
    print("\n[步骤2] 开始提问")
    print("输入问题进行查询，输入 quit 退出")
    print("-" * 60)
    
    while True:
        question = input("\n请输入问题: ").strip()
        if question.lower() in ["quit", "exit", "q"]:
            print("再见！")
            break
        
        if not question:
            continue
        
        result = query(question)
        
        print("\n[回答]")
        print(result.get("answer", "未获取到回答"))
        
        if result.get("citations"):
            print("\n[引用来源]")
            for cite in result["citations"]:
                print(f"  - {cite['doc_name']}, 第{cite['page_number']}页")
        
        print(f"\n[置信度] {result.get('confidence', 0):.1%}")

if __name__ == "__main__":
    main()
EOF
```

### 6.2 运行交互式查询

```bash
# 确保API服务已启动
# 终端1：启动服务
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# 终端2：运行交互式查询
python3 scripts/interactive_query.py
```

**使用示例：**
```
============================================================
校园学术智能RAG检索系统 - 交互式查询
============================================================

[步骤1] 上传文档
请输入文档路径（或输入 skip 跳过）：
> data/raw_documents/机器学习.pdf
课程名称（可选): 机器学习
上传结果: 文档处理成功: 机器学习.pdf

[步骤2] 开始提问
输入问题进行查询，输入 quit 退出
------------------------------------------------------------

请输入问题: 什么是梯度下降？

[回答]
梯度下降是一种优化算法，用于最小化损失函数...

[引用来源]
  - 机器学习.pdf, 第45页

[置信度] 87.0%

请输入问题: quit
再见！
```

---

## 七、常见问题

### Q1: 首次运行很慢？

首次运行需要下载嵌入模型（约500MB），请确保网络通畅。如果网络受限，可以：
1. 手动下载模型到 `./models/` 目录
2. 在 `.env` 中配置 `EMBEDDING_MODEL_PATH=./models/bge-base-zh-v1.5`

### Q2: 提示 "LLM调用失败"？

检查 `.env` 中的 LLM 配置：
- `LLM_API_KEY` 是否正确
- `LLM_BASE_URL` 是否可访问
- `LLM_MODEL` 是否有效

### Q3: 检索结果为空？

- 确认已成功上传文档（检查 `/stats` 接口）
- 尝试使用更简单的关键词提问
- 调整 `RETRIEVAL_TOP_K` 增加返回数量

### Q4: 如何清除已上传的文档？

```bash
# 删除向量索引数据
rm -rf data/vector_index/*

# 删除处理后的分片
rm -rf data/processed_chunks/*

# 重启服务
```

---

## 八、项目结构

```
campus-academic-rag/
├── src/                        # 核心源码
│   ├── core/                   # 核心功能模块
│   │   ├── document_parser/    # 文档解析
│   │   ├── chunker/            # 分片模块
│   │   ├── embedding/          # 嵌入模块
│   │   ├── retriever/          # 检索模块
│   │   ├── agent/              # 多Agent模块
│   │   └── generator/          # 生成模块
│   ├── api/                    # API接口层
│   ├── config/                 # 配置文件
│   └── tests/                  # 测试用例
├── data/                       # 数据目录
│   ├── raw_documents/          # 原始文档（放这里）
│   ├── processed_chunks/       # 处理后的分片
│   └── vector_index/           # 向量索引
├── scripts/                    # 工具脚本
├── .env.example                # 环境变量示例
├── pyproject.toml              # 依赖管理
└── README.md                   # 本文档
```

---

## 九、技术栈

- **文档解析**：pdfplumber, python-pptx, python-docx
- **嵌入模型**：sentence-transformers (BGE系列)
- **向量数据库**：ChromaDB
- **关键词检索**：rank-bm25, jieba
- **Web框架**：FastAPI
- **LLM集成**：OpenAI API (支持兼容服务)

---

## 十、许可证

本项目仅供校园学术研究使用。
