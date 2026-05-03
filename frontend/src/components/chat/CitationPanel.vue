<template>
  <aside class="citation-panel">
    <div class="panel-header">
      <span class="panel-title">引用溯源</span>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    <div class="panel-body">
      <div v-if="!citations.length" class="panel-empty">暂无引用</div>
      <div v-for="cite in citations" :key="cite.citation_id" class="cite-card">
        <div class="cite-header">
          <span class="cite-id">[{{ cite.citation_id }}]</span>
          <span class="cite-doc">{{ cite.doc_name }}</span>
          <span class="cite-page">第{{ cite.page_number }}页</span>
        </div>
        <div v-if="cite.relevance_score" class="cite-score">
          相关度: {{ (cite.relevance_score * 100).toFixed(0) }}%
        </div>
        <div class="cite-actions">
          <button class="cite-action-btn" @click="previewDoc(cite)">查看原文</button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

defineProps({
  citations: { type: Array, default: () => [] },
})

defineEmits(['close'])

const router = useRouter()

function previewDoc(cite) {
  router.push({
    path: '/preview',
    query: { docName: cite.doc_name, page: cite.page_number },
  })
}
</script>

<style lang="scss" scoped>
.citation-panel {
  width: var(--citation-panel-width);
  height: 100%;
  background: var(--color-bg);
  border-left: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
}

.close-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-size: 18px;
  color: var(--color-text-tertiary);
  &:hover { background: var(--color-bg-tertiary); color: var(--color-text); }
}

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.panel-empty {
  text-align: center;
  color: var(--color-text-tertiary);
  padding: 40px 0;
  font-size: 13px;
}

.cite-card {
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
  transition: border-color var(--transition-fast);

  &:hover { border-color: var(--color-primary); }
}

.cite-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  flex-wrap: wrap;
}

.cite-id {
  font-weight: 600;
  color: var(--color-primary);
}

.cite-doc {
  color: var(--color-text);
  font-weight: 500;
}

.cite-page {
  color: var(--color-text-tertiary);
  font-size: 12px;
}

.cite-score {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 6px;
}

.cite-actions {
  margin-top: 8px;
}

.cite-action-btn {
  padding: 4px 12px;
  font-size: 12px;
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);

  &:hover {
    background: var(--color-primary);
    color: #fff;
  }
}
</style>
