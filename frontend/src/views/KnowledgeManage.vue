<template>
  <div class="knowledge-page">
    <div class="page-header">
      <h2>知识库管理</h2>
      <div class="header-actions">
        <el-button size="small" @click="showAddBase = true">新建知识库</el-button>
        <el-button size="small" type="primary" @click="triggerUpload">上传文档</el-button>
      </div>
    </div>

    <div class="knowledge-body">
      <!-- 左侧知识库列表 -->
      <div class="kb-sidebar">
        <div
          v-for="kb in knowledgeStore.bases"
          :key="kb.id"
          class="kb-card"
          :class="{ active: kb.id === knowledgeStore.currentId }"
          @click="knowledgeStore.switchBase(kb.id)"
        >
          <div class="kb-card-name">{{ kb.name }}</div>
          <div class="kb-card-meta">{{ kb.documents.length }} 个文档</div>
          <button
            v-if="kb.id !== 'default'"
            class="kb-delete-btn"
            @click.stop="knowledgeStore.removeBase(kb.id)"
            title="删除"
          >×</button>
        </div>
      </div>

      <!-- 右侧文档列表 -->
      <div class="doc-area">
        <div class="doc-area-header">
          <span>{{ knowledgeStore.currentBase?.name }} - 文档列表</span>
        </div>

        <DocumentUpload
          ref="uploadRef"
          :kb-id="knowledgeStore.currentId"
          @uploaded="handleUploaded"
        />

        <div v-if="docs.length === 0" class="doc-empty">
          <div>暂无文档，请上传学术文档到当前知识库</div>
          <div class="doc-formats">支持格式：PDF / PPTX / DOCX / MD / TXT</div>
        </div>

        <div v-else class="doc-grid">
          <DocumentCard
            v-for="doc in docs"
            :key="doc.docId"
            :doc="doc"
            @delete="handleDeleteDoc"
            @preview="handlePreview"
          />
        </div>
      </div>
    </div>

    <!-- 新建知识库弹窗 -->
    <el-dialog v-model="showAddBase" title="新建知识库" width="360px">
      <el-input v-model="newBaseName" placeholder="请输入知识库名称" @keyup.enter="handleAddBase" />
      <template #footer>
        <el-button @click="showAddBase = false">取消</el-button>
        <el-button type="primary" @click="handleAddBase">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useKnowledgeStore } from '@/store/knowledge'
import DocumentUpload from '@/components/document/DocumentUpload.vue'
import DocumentCard from '@/components/document/DocumentCard.vue'

const router = useRouter()
const knowledgeStore = useKnowledgeStore()

const showAddBase = ref(false)
const newBaseName = ref('')
const uploadRef = ref(null)

const docs = computed(() => knowledgeStore.currentBase?.documents || [])

function triggerUpload() {
  uploadRef.value?.triggerInput()
}

function handleUploaded(doc) {
  knowledgeStore.addDocument(knowledgeStore.currentId, doc)
}

function handleDeleteDoc(docId) {
  knowledgeStore.removeDocument(knowledgeStore.currentId, docId)
}

function handlePreview(doc) {
  router.push({ path: '/preview', query: { docId: doc.docId, docName: doc.docName } })
}

function handleAddBase() {
  if (newBaseName.value.trim()) {
    knowledgeStore.addBase(newBaseName.value.trim())
    newBaseName.value = ''
    showAddBase.value = false
  }
}
</script>

<style lang="scss" scoped>
.knowledge-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);

  h2 { font-size: 16px; font-weight: 600; }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.knowledge-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.kb-sidebar {
  width: 220px;
  border-right: 1px solid var(--color-border);
  padding: 12px;
  overflow-y: auto;
  flex-shrink: 0;
}

.kb-card {
  position: relative;
  padding: 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--transition-fast);

  &:hover { background: var(--color-bg-tertiary); }
  &.active { background: var(--color-primary-light); }

  &-name { font-size: 14px; font-weight: 500; }
  &-meta { font-size: 12px; color: var(--color-text-tertiary); margin-top: 4px; }
}

.kb-delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--color-text-tertiary);
  font-size: 14px;
  opacity: 0;
  transition: opacity var(--transition-fast);

  .kb-card:hover & { opacity: 1; }
  &:hover { background: var(--color-danger); color: #fff; }
}

.doc-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 16px 24px;
}

.doc-area-header {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;
}

.doc-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  gap: 8px;
}

.doc-formats {
  font-size: 12px;
  color: var(--color-text-placeholder);
}

.doc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  overflow-y: auto;
}
</style>
