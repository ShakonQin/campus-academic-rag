// 知识库管理接口（前端本地管理，后端暂无独立知识库API）
// 知识库数据存储在localStorage中

const STORAGE_KEY = 'rag_knowledge_bases'

export function getKnowledgeBases() {
  const data = localStorage.getItem(STORAGE_KEY)
  return data ? JSON.parse(data) : [{ id: 'default', name: '默认知识库', documents: [], createdAt: Date.now() }]
}

export function saveKnowledgeBases(list) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}
