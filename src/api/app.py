"""FastAPI主应用"""

import os
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.config.settings import settings
from src.utils.logger import logger


# 请求/响应模型
class QueryRequest(BaseModel):
    """查询请求"""
    query: str
    top_k: int = 10
    scene_type: str = "general"
    filter_metadata: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, str]]] = None


class QueryResponse(BaseModel):
    """查询响应"""
    answer: str
    citations: List[Dict[str, Any]]
    confidence: float
    retrieval_results: List[Dict[str, Any]]
    verification: Optional[Dict[str, Any]] = None


class DocumentRequest(BaseModel):
    """文档上传请求"""
    doc_path: str
    course_name: Optional[str] = None
    chapter: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentResponse(BaseModel):
    """文档处理响应"""
    success: bool
    doc_id: str
    doc_name: str
    chunks_count: int
    message: str


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    version: str
    components: Dict[str, str]


# 全局组件
_components = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("正在初始化系统组件...")

    try:
        # 初始化组件
        from src.core.retriever.retrieval_engine import RetrievalEngine
        from src.core.agent import (
            AgentRouter, ParseAgent, RetrieveAgent,
            GenerateAgent, VerifyAgent, IterateAgent
        )
        from src.core.generator import ResponseGenerator, CitationTracker

        # 创建组件
        retrieval_engine = RetrievalEngine()
        citation_tracker = CitationTracker()
        response_generator = ResponseGenerator(citation_tracker)

        # 创建Agent
        parse_agent = ParseAgent()
        retrieve_agent = RetrieveAgent(retrieval_engine)
        generate_agent = GenerateAgent()
        verify_agent = VerifyAgent()
        iterate_agent = IterateAgent()

        # 创建路由器
        router = AgentRouter()
        router.register_agent(parse_agent)
        router.register_agent(retrieve_agent)
        router.register_agent(generate_agent)
        router.register_agent(verify_agent)
        router.register_agent(iterate_agent)

        # 保存组件
        _components.update({
            "retrieval_engine": retrieval_engine,
            "citation_tracker": citation_tracker,
            "response_generator": response_generator,
            "parse_agent": parse_agent,
            "retrieve_agent": retrieve_agent,
            "generate_agent": generate_agent,
            "verify_agent": verify_agent,
            "iterate_agent": iterate_agent,
            "router": router,
        })

        logger.info("系统组件初始化完成")

    except Exception as e:
        logger.error(f"系统组件初始化失败: {e}")

    yield

    logger.info("系统正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title="校园学术智能RAG检索系统",
    description="专为校园学习科研场景打造的私有化RAG问答系统",
    version=settings.app.app_version,
    lifespan=lifespan,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    components_status = {}
    for name, component in _components.items():
        components_status[name] = "ok" if component else "not_loaded"

    return HealthResponse(
        status="ok",
        version=settings.app.app_version,
        components=components_status,
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """查询接口"""
    try:
        from src.core.agent import AgentContext, AgentType

        # 创建上下文
        context = AgentContext(
            query=request.query,
            metadata={
                "filter": request.filter_metadata,
                "scene_type": request.scene_type,
            },
            history=request.history or [],
        )

        # 执行检索
        retrieve_agent = _components.get("retrieve_agent")
        if not retrieve_agent:
            raise HTTPException(status_code=500, detail="检索Agent未初始化")

        retrieve_response = retrieve_agent.execute(context, top_k=request.top_k)
        if retrieve_response.success:
            context.retrieval_results = retrieve_response.data.get("results", [])

        # 生成回答
        response_generator = _components.get("response_generator")
        if response_generator:
            from src.core.retriever.multi_way_merge import RetrievalResult

            # 转换为RetrievalResult
            retrieval_results = []
            for r in context.retrieval_results:
                result = RetrievalResult(
                    chunk_id=r["chunk_id"],
                    content=r["content"],
                    metadata=r["metadata"],
                    scores={"final": r["score"]},
                    final_score=r["score"],
                    retrieval_channels=r.get("channels", []),
                )
                retrieval_results.append(result)

            generated = response_generator.generate(
                query=request.query,
                retrieval_results=retrieval_results,
                scene_type=request.scene_type,
                history=request.history,
            )
            context.generated_answer = generated.answer

        # 校验回答
        verify_agent = _components.get("verify_agent")
        verification = None
        if verify_agent and context.generated_answer:
            verify_response = verify_agent.execute(context)
            if verify_response.success:
                verification = verify_response.data.get("verification")

        return QueryResponse(
            answer=context.generated_answer,
            citations=[c.to_dict() for c in (generated.citations if response_generator else [])],
            confidence=generated.confidence if response_generator else 0.0,
            retrieval_results=context.retrieval_results,
            verification=verification,
        )

    except Exception as e:
        logger.error(f"查询失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents", response_model=DocumentResponse)
async def upload_document(request: DocumentRequest):
    """文档上传接口"""
    try:
        parse_agent = _components.get("parse_agent")
        retrieval_engine = _components.get("retrieval_engine")

        if not parse_agent or not retrieval_engine:
            raise HTTPException(status_code=500, detail="组件未初始化")

        # 解析并索引文档
        result = parse_agent.parse_and_index(
            doc_path=request.doc_path,
            retrieval_engine=retrieval_engine,
            course_name=request.course_name,
            chapter=request.chapter,
            tags=request.tags,
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "文档处理失败"))

        return DocumentResponse(
            success=True,
            doc_id=result["doc_id"],
            doc_name=result["doc_name"],
            chunks_count=result["chunks_count"],
            message=f"文档处理成功: {result['doc_name']}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document_file(
    file: UploadFile = File(...),
    course_name: str = Form(default=""),
    chapter: str = Form(default=""),
    tags: str = Form(default=""),
):
    """文件上传接口 - 接收multipart文件"""
    tmp_path = None
    try:
        parse_agent = _components.get("parse_agent")
        retrieval_engine = _components.get("retrieval_engine")

        if not parse_agent or not retrieval_engine:
            raise HTTPException(status_code=500, detail="组件未初始化")

        # 保存上传文件到临时目录
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        tmp_path = upload_dir / file.filename
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        logger.info(f"文件已保存: {tmp_path}")

        # 解析tags
        tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

        # 解析并索引文档
        result = parse_agent.parse_and_index(
            doc_path=str(tmp_path),
            retrieval_engine=retrieval_engine,
            course_name=course_name,
            chapter=chapter,
            tags=tag_list,
        )

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "文档处理失败"))

        return DocumentResponse(
            success=True,
            doc_id=result["doc_id"],
            doc_name=result["doc_name"],
            chunks_count=result["chunks_count"],
            message=f"文档处理成功: {result['doc_name']}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档上传处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理临时文件
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


@app.get("/stats")
async def get_stats():
    """获取系统统计"""
    retrieval_engine = _components.get("retrieval_engine")
    iterate_agent = _components.get("iterate_agent")

    stats = {
        "version": settings.app.app_version,
        "components_loaded": len(_components),
    }

    if iterate_agent:
        analysis = iterate_agent._analyze_performance()
        stats["performance"] = analysis.get("metrics", {})

    return stats


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.app:app",
        host=settings.app.app_host,
        port=settings.app.app_port,
        reload=settings.app.app_debug,
    )


# ========== 前端静态文件托管 ==========
def _find_frontend_dist() -> Path | None:
    """查找前端构建产物目录"""
    # 优先使用环境变量
    env_dist = os.environ.get("FRONTEND_DIST")
    if env_dist and Path(env_dist).is_dir():
        return Path(env_dist)
    # 默认查找 frontend/dist
    candidates = [
        Path(__file__).parent.parent.parent / "frontend" / "dist",
        Path("frontend/dist"),
    ]
    for p in candidates:
        if p.is_dir():
            return p.resolve()
    return None


_frontend_dist = _find_frontend_dist()

if _frontend_dist:
    app.mount("/assets", StaticFiles(directory=str(_frontend_dist / "assets")), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        """托管前端SPA，所有非API路由返回index.html"""
        file_path = _frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_frontend_dist / "index.html"))
