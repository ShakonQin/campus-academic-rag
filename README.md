# 校园学术智能RAG检索系统

专为校园学习科研场景打造的私有化RAG问答系统，将课程PPT、课本PDF、学术论文等学术文档转化为可精准检索的知识库。

## 核心特性

- **多格式文档解析**：支持PDF、PPTX、DOCX、Markdown等校园常见文档格式
- **智能分片策略**：按句分片+滑动窗口，保留学术文档语义完整性
- **多路检索融合**：向量语义检索 + BM25关键词检索 + 元数据过滤
- **多Agent协作**：MoE式架构，场景专属专家Agent
- **抗幻觉机制**：知识校验、引用溯源，确保回答100%基于知识库
- **完全私有化**：支持离线部署，数据本地存储，适配校园内网环境

## 快速开始

### 环境要求

- Python 3.10+
- Poetry

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd campus-academic-rag

# 安装依赖
poetry install

# 复制环境变量配置
cp .env.example .env
# 编辑 .env 填入配置
```

### 运行

```bash
# 启动API服务
poetry run uvicorn src.api.app:app --host 0.0.0.0 --port 8000

# 或使用脚本
python scripts/init_project.py
```

### 文档入库

```bash
# 批量处理文档
python scripts/batch_process.py --input ./data/raw_documents
```

## 项目结构

```
campus-academic-rag/
├── src/                    # 核心源码
│   ├── core/              # 核心功能模块
│   │   ├── document_parser/   # 文档解析
│   │   ├── chunker/           # 分片模块
│   │   ├── embedding/         # 嵌入模块
│   │   ├── retriever/         # 检索模块
│   │   ├── agent/             # 多Agent模块
│   │   └── generator/         # 生成模块
│   ├── api/               # API接口层
│   ├── config/            # 配置文件
│   ├── utils/             # 工具函数
│   └── tests/             # 测试用例
├── data/                  # 数据目录
├── docs/                  # 文档目录
└── scripts/               # 工具脚本
```

## 技术栈

- **文档解析**：pdfplumber, python-pptx, python-docx
- **嵌入模型**：sentence-transformers (BGE系列)
- **向量数据库**：ChromaDB
- **关键词检索**：rank-bm25, jieba
- **Web框架**：FastAPI
- **LLM集成**：OpenAI API, Anthropic API (支持本地模型)

## 性能指标

| 指标 | 合格线 | 优化目标 |
|------|--------|----------|
| 召回率@10 | ≥90% | ≥98% |
| 回答准确率 | ≥95% | ≥99% |
| 幻觉率 | ≤5% | ≤1% |
| 单轮响应延迟 | ≤3s | ≤1s |

## 许可证

本项目仅供校园学术研究使用。

## 联系方式

如有问题或建议，请通过项目Issue反馈。
