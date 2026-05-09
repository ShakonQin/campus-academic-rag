# 校园学术智能RAG检索系统

专为校园学习科研场景打造的私有化RAG问答系统，将课程PPT、课本PDF、学术论文等学术文档转化为可精准检索的知识库。

## 核心特性

- **多格式文档解析**：支持PDF、PPTX、DOCX、Markdown等校园常见文档格式
- **智能分片策略**：按句分片+滑动窗口，保留学术文档语义完整性
- **多路检索融合**：向量语义检索 + BM25关键词检索 + 元数据过滤
- **多Agent协作**：MoE式架构，场景专属专家Agent
- **抗幻觉机制**：知识校验、引用溯源，确保回答基于知识库
- **完全私有化**：支持离线部署，数据本地存储，适配校园内网环境
- **Web界面**：Vue3前端，支持拖放上传、对话问答、引用溯源

---

## 快速开始

### 前置条件

- Python 3.10+
- Node.js 18+（前端需要）
- 一个 LLM API Key（OpenAI / DeepSeek / 智谱AI 等兼容接口均可）

### 1. 安装后端依赖

```bash
cd campus-academic-rag

# 使用 Poetry（推荐）
poetry install

# 或使用 pip
pip install pdfplumber python-pptx python-docx sentence-transformers chromadb \
  rank-bm25 jieba fastapi uvicorn pydantic openai anthropic loguru python-dotenv \
  python-multipart
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env   # 编辑配置
```

必须填写的项：

```bash
# LLM 配置（必填）
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxxxxxxx
LLM_BASE_URL=https://api.deepseek.com/v1   # 或其他兼容API
LLM_MODEL=deepseek-chat

# 嵌入模型（默认即可，首次运行自动下载）
EMBEDDING_MODEL_NAME=BAAI/bge-base-zh-v1.5
EMBEDDING_DEVICE=cpu
```

### 3. 启动后端服务

```bash
# 初始化项目目录
python3 scripts/init_project.py

# 启动 API 服务（默认 8000 端口）
python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

验证后端启动：

```bash
curl http://localhost:8000/health
# 预期输出：{"status":"ok","version":"1.0.0",...}
```

### 4. 启动前端界面

新开一个终端：

```bash
cd campus-academic-rag/frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

浏览器访问 http://localhost:5173 即可使用。

### 5. 上传文档 & 提问

1. 在前端界面拖放 PDF/PPTX/DOCX 文件上传
2. 等待解析完成（页面会显示进度）
3. 在对话框输入问题，获取基于文档的回答和引用溯源

---

## 详细配置

### LLM API 配置示例

```bash
# DeepSeek（推荐国内用户）
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_API_KEY=your-key
LLM_MODEL=deepseek-chat

# OpenAI 官方
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-xxxxxxxx
LLM_MODEL=gpt-4o

# 智谱AI
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_API_KEY=your-key
LLM_MODEL=glm-4

# 本地部署（Ollama / vLLM）
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=qwen2:7b
```

### 嵌入模型配置

```bash
# 在线模型（首次需下载约500MB）
EMBEDDING_MODEL_NAME=BAAI/bge-base-zh-v1.5

# 本地模型（离线环境）
EMBEDDING_MODEL_PATH=./models/bge-base-zh-v1.5

EMBEDDING_DEVICE=cpu   # 或 cuda（有GPU时）
```

### 检索参数

```bash
RETRIEVAL_TOP_K=10          # 每次检索返回的结果数量
VECTOR_WEIGHT=0.7           # 向量检索权重（0~1）
BM25_WEIGHT=0.3             # 关键词检索权重（0~1）
```

---

## 使用方式

### Web 界面（推荐）

启动前后端后访问 http://localhost:5173：

- **问答对话**：输入问题，获得基于文档的回答，支持引用溯源
- **文档管理**：拖放上传、查看已上传文档列表
- **深色/浅色模式**：界面右上角切换

### API 接口

后端同时提供 REST API，访问 http://localhost:8000/docs 查看交互式文档。

```bash
# 上传文档（文件方式）
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@data/raw_documents/机器学习.pdf" \
  -F "course_name=机器学习"

# 上传文档（路径方式，文件需在服务器上）
curl -X POST http://localhost:8000/documents \
  -H "Content-Type: application/json" \
  -d '{"doc_path": "data/raw_documents/机器学习.pdf", "course_name": "机器学习"}'

# 提问
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是梯度下降？", "top_k": 5, "scene_type": "general"}'

# 查看统计
curl http://localhost:8000/stats
```

### 场景类型

| scene_type | 说明 | 示例问题 |
|---|---|---|
| `general` | 通用问答（默认） | "什么是卷积神经网络？" |
| `exam` | 考点梳理 | "请梳理期末考试重点" |
| `homework` | 作业答疑 | "解释反向传播的推导过程" |
| `paper` | 论文解读 | "这篇论文的主要贡献是什么？" |

---

## 项目结构

```
campus-academic-rag/
├── src/                        # 后端源码
│   ├── core/                   # 核心模块
│   │   ├── document_parser/    # 文档解析
│   │   ├── chunker/            # 分片模块
│   │   ├── embedding/          # 嵌入模块
│   │   ├── retriever/          # 检索模块
│   │   ├── agent/              # 多Agent模块
│   │   └── generator/          # 生成模块
│   ├── api/                    # API接口层
│   └── config/                 # 配置
├── frontend/                   # Vue3 前端
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── components/         # 通用组件
│   │   ├── api/                # 接口封装
│   │   ├── store/              # 状态管理
│   │   └── styles/             # 样式
│   ├── package.json
│   └── vite.config.js
├── data/                       # 数据目录
│   ├── raw_documents/          # 原始文档
│   ├── processed_chunks/       # 处理后的分片
│   └── vector_index/           # 向量索引
├── scripts/                    # 工具脚本
├── .env.example                # 环境变量示例
├── pyproject.toml              # Python 依赖
└── README.md
```

---

## 常见问题

**Q: 首次运行很慢？**
首次需下载嵌入模型（约500MB）。网络受限时可手动下载到 `./models/` 并配置 `EMBEDDING_MODEL_PATH`。

**Q: 提示 "LLM调用失败"？**
检查 `.env` 中的 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL` 是否正确。

**Q: 检索结果为空？**
确认已成功上传文档（`curl http://localhost:8000/stats`），尝试更简单的关键词提问。

**Q: 前端无法连接后端？**
确保后端在 8000 端口运行。开发模式下前端通过 Vite proxy 转发请求，检查 `frontend/vite.config.js` 中的代理配置。

**Q: 如何清除已上传的文档？**
```bash
rm -rf data/vector_index/* data/processed_chunks/*
# 重启后端服务
```

---

## 技术栈

| 模块 | 技术 |
|---|---|
| 文档解析 | pdfplumber, python-pptx, python-docx |
| 嵌入模型 | sentence-transformers (BGE系列) |
| 向量数据库 | ChromaDB |
| 关键词检索 | rank-bm25, jieba |
| Web后端 | FastAPI |
| Web前端 | Vue 3 + Vite + Element Plus |
| LLM集成 | OpenAI API (兼容接口) |

---

## 许可证

本项目仅供校园学术研究使用。
