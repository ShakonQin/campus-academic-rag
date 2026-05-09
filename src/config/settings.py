"""全局配置模块 - 校园学术智能RAG检索系统"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


class AppSettings(BaseSettings):
    """应用基础配置"""

    # 应用信息
    app_name: str = Field(default="campus-academic-rag", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    app_debug: bool = Field(default=False, description="调试模式")

    # 服务配置
    app_host: str = Field(default="0.0.0.0", description="服务地址")
    app_port: int = Field(default=8000, description="服务端口")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: str = Field(default="logs/app.log", description="日志文件路径")


class EmbeddingSettings(BaseSettings):
    """嵌入模型配置"""

    # 提供商: "local" (sentence-transformers) 或 "api" (OpenAI兼容API)
    embedding_provider: str = Field(default="api", description="嵌入提供商: local/api")

    # API模式配置（embedding_provider=api时使用）
    embedding_api_key: Optional[str] = Field(default=None, description="Embedding API密钥")
    embedding_api_base_url: str = Field(
        default="https://api.openai.com/v1", description="Embedding API基础URL"
    )
    embedding_api_model: str = Field(
        default="text-embedding-3-small", description="API Embedding模型名称"
    )

    # 本地模型配置（embedding_provider=local时使用）
    embedding_model_path: Optional[str] = Field(
        default=None, description="本地模型路径"
    )
    embedding_model_name: str = Field(
        default="BAAI/bge-base-zh-v1.5", description="模型名称"
    )
    embedding_device: str = Field(default="cpu", description="运行设备")
    embedding_dimension: int = Field(default=768, description="向量维度")


class VectorDBSettings(BaseSettings):
    """向量数据库配置"""

    vector_db_path: str = Field(
        default="./data/vector_index", description="向量数据库路径"
    )
    vector_db_collection: str = Field(
        default="campus_academic", description="集合名称"
    )


class LLMSettings(BaseSettings):
    """大语言模型配置"""

    # LLM提供商配置
    llm_provider: str = Field(default="openai", description="LLM提供商")
    llm_api_key: Optional[str] = Field(default=None, description="API密钥")
    llm_base_url: str = Field(
        default="https://api.openai.com/v1", description="API基础URL"
    )
    llm_model: str = Field(default="gpt-4o", description="模型名称")
    llm_max_tokens: int = Field(default=4096, description="最大token数")
    llm_temperature: float = Field(default=0.1, description="温度参数")

    # Anthropic配置
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API密钥")
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229", description="Anthropic模型"
    )


class RetrievalSettings(BaseSettings):
    """检索配置"""

    retrieval_top_k: int = Field(default=10, description="Top-K召回数量")
    retrieval_similarity_threshold: float = Field(
        default=0.5, description="相似度阈值"
    )
    bm25_weight: float = Field(default=0.3, description="BM25权重")
    vector_weight: float = Field(default=0.7, description="向量检索权重")


class ChunkSettings(BaseSettings):
    """分片配置"""

    chunk_sentences_per_chunk: int = Field(
        default=3, description="每个分片的句子数"
    )
    chunk_overlap_sentences: int = Field(
        default=1, description="重叠句子数"
    )
    chunk_max_length: int = Field(default=512, description="分片最大长度")


class OCRSettings(BaseSettings):
    """OCR配置"""

    tesseract_cmd: str = Field(
        default="/usr/bin/tesseract", description="Tesseract命令路径"
    )
    tesseract_lang: str = Field(
        default="chi_sim+eng", description="OCR语言"
    )


class ComplianceSettings(BaseSettings):
    """合规性配置"""

    compliance_check_enabled: bool = Field(
        default=True, description="启用合规检查"
    )
    academic_integrity_check: bool = Field(
        default=True, description="启用学术诚信审核"
    )


class Settings(BaseSettings):
    """全局配置聚合"""

    app: AppSettings = AppSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    vector_db: VectorDBSettings = VectorDBSettings()
    llm: LLMSettings = LLMSettings()
    retrieval: RetrievalSettings = RetrievalSettings()
    chunk: ChunkSettings = ChunkSettings()
    ocr: OCRSettings = OCRSettings()
    compliance: ComplianceSettings = ComplianceSettings()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


# 全局配置实例
settings = Settings()
