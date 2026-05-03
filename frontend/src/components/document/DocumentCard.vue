<template>
  <div class="doc-card" @click="$emit('preview', doc)">
    <div class="doc-icon">{{ icon }}</div>
    <div class="doc-info">
      <div class="doc-name" :title="doc.docName">{{ doc.docName }}</div>
      <div class="doc-meta">
        <span>{{ doc.type?.toUpperCase() }}</span>
        <span v-if="doc.chunksCount">{{ doc.chunksCount }} 分片</span>
        <span v-if="doc.size">{{ formatSize(doc.size) }}</span>
      </div>
      <div class="doc-time">{{ formatTime(doc.uploadedAt) }}</div>
    </div>
    <button class="doc-delete" @click.stop="$emit('delete', doc.docId)" title="删除">×</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatTime, formatSize } from '@/utils/common'

const props = defineProps({
  doc: { type: Object, required: true },
})

defineEmits(['preview', 'delete'])

const iconMap = {
  pdf: '📕',
  pptx: '📊',
  ppt: '📊',
  docx: '📘',
  doc: '📘',
  md: '📝',
  txt: '📄',
}

const icon = computed(() => iconMap[props.doc.type] || '📄')
</script>

<style lang="scss" scoped>
.doc-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;

  &:hover {
    border-color: var(--color-primary);
    box-shadow: 0 2px 8px var(--color-shadow);

    .doc-delete { opacity: 1; }
  }
}

.doc-icon { font-size: 32px; flex-shrink: 0; }

.doc-info { flex: 1; min-width: 0; }

.doc-name {
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 4px;
}

.doc-time {
  font-size: 11px;
  color: var(--color-text-placeholder);
  margin-top: 4px;
}

.doc-delete {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-size: 16px;
  color: var(--color-text-tertiary);
  opacity: 0;
  transition: opacity var(--transition-fast);

  &:hover {
    background: var(--color-danger);
    color: #fff;
  }
}
</style>
