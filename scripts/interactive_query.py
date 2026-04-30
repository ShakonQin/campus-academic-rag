"""交互式查询脚本"""

import requests
import json
import sys

API_BASE = "http://localhost:8000"


def check_health():
    """检查服务状态"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def upload_document(doc_path, course_name="", chapter=""):
    """上传文档"""
    response = requests.post(f"{API_BASE}/documents", json={
        "doc_path": doc_path,
        "course_name": course_name,
        "chapter": chapter,
    })
    return response.json()


def query(question, scene_type="general", top_k=5):
    """提问"""
    response = requests.post(f"{API_BASE}/query", json={
        "query": question,
        "scene_type": scene_type,
        "top_k": top_k,
    })
    return response.json()


def main():
    print("=" * 60)
    print("校园学术智能RAG检索系统 - 交互式查询")
    print("=" * 60)

    # 检查服务状态
    print("\n检查服务状态...")
    if not check_health():
        print("错误: API服务未启动！")
        print("请先运行: python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    print("服务状态: 正常")

    # 上传文档
    print("\n" + "-" * 60)
    print("[步骤1] 上传文档")
    print("-" * 60)
    print("请输入文档路径（支持PDF/PPTX/DOCX/MD/TXT）")
    print("输入 skip 跳过，输入 done 完成上传")

    documents = []
    while True:
        doc_path = input("\n文档路径> ").strip()

        if doc_path.lower() == "skip" or doc_path.lower() == "done":
            break

        if not doc_path:
            continue

        course = input("课程名称（可选，直接回车跳过）: ").strip()
        chapter = input("章节名称（可选，直接回车跳过）: ").strip()

        print(f"\n正在上传: {doc_path}...")
        result = upload_document(doc_path, course_name=course, chapter=chapter)

        if result.get("success"):
            print(f"上传成功！")
            print(f"  - 文档: {result.get('doc_name')}")
            print(f"  - 分片数: {result.get('chunks_count')}")
            documents.append(result.get("doc_name"))
        else:
            print(f"上传失败: {result.get('detail', '未知错误')}")

        more = input("\n继续上传？(y/n): ").strip().lower()
        if more != "y":
            break

    if documents:
        print(f"\n已上传 {len(documents)} 个文档")

    # 开始提问
    print("\n" + "-" * 60)
    print("[步骤2] 开始提问")
    print("-" * 60)
    print("输入问题进行查询，支持的命令：")
    print("  - quit/exit/q: 退出程序")
    print("  - upload: 上传新文档")
    print("  - stats: 查看系统统计")
    print("-" * 60)

    history = []

    while True:
        question = input("\n请输入问题: ").strip()

        # 处理命令
        if question.lower() in ["quit", "exit", "q"]:
            print("再见！")
            break

        if question.lower() == "upload":
            doc_path = input("文档路径> ").strip()
            if doc_path:
                course = input("课程名称: ").strip()
                result = upload_document(doc_path, course_name=course)
                print(f"结果: {result.get('message', '失败')}")
            continue

        if question.lower() == "stats":
            response = requests.get(f"{API_BASE}/stats")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            continue

        if not question:
            continue

        # 执行查询
        print("\n正在查询...")
        try:
            result = query(question)

            # 显示回答
            print("\n" + "=" * 60)
            print("[回答]")
            print("=" * 60)
            print(result.get("answer", "未获取到回答"))

            # 显示引用
            if result.get("citations"):
                print("\n" + "-" * 60)
                print("[引用来源]")
                print("-" * 60)
                for cite in result["citations"]:
                    print(f"  [{cite.get('citation_id')}] {cite.get('doc_name')}, 第{cite.get('page_number')}页")

            # 显示置信度
            confidence = result.get("confidence", 0)
            print(f"\n[置信度] {confidence:.1%}")

            # 更新历史
            history.append({"query": question, "answer": result.get("answer", "")})

        except Exception as e:
            print(f"查询失败: {e}")


if __name__ == "__main__":
    main()
