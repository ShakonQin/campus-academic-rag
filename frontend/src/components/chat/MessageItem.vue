<template>
  <div class="message" :class="[`message--${message.role}`]">
    <div class="message-avatar">
      <span>{{ message.role === 'user' ? '👤' : '🤖' }}</span>
    </div>
    <div class="message-body">
      <div class="message-meta">
        <span class="message-role">{{ message.role === 'user' ? '我' : '学术助手' }}</span>
        <span v-if="message.confidence" class="message-confidence">
          置信度 {{ (message.confidence * 100).toFixed(0) }}%
        </span>
      </div>
      <div class="message-content" v-html="renderedContent"></div>
      <div v-if="message.citations?.length" class="message-citations">
        <button
          v-for="cite in message.citations"
          :key="cite.citation_id"
          class="cite-tag"
          @click="$emit('citeClick', message.citations)"
        >
          [{{ cite.citation_id }}] {{ cite.doc_name }}, 第{{ cite.page_number }}页
        </button>
      </div>
      <div class="message-actions">
        <button class="action-btn" @click="copyContent" title="复制">📋</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/markdown'
import { renderFormulas } from '@/utils/katex'
import { ElMessage } from 'element-plus'

const props = defineProps({
  message: { type: Object, required: true },
})

defineEmits(['citeClick'])

const renderedContent = computed(() => {
  if (!props.message.content) return ''
  let html = renderMarkdown(props.message.content)
  html = renderFormulas(html)
  return html
})

function copyContent() {
  navigator.clipboard.writeText(props.message.content).then(() => {
    ElMessage.success('已复制')
  })
}
</script>

<style lang="scss" scoped>
.message {
  display: flex;
  gap: 12px;
  padding: 16px 0;

  &--user {
    flex-direction: row-reverse;
    .message-body { align-items: flex-end; }
    .message-content {
      background: var(--color-primary);
      color: #fff;
      border-radius: var(--radius-lg) var(--radius-sm) var(--radius-lg) var(--radius-lg);
    }
    .message-meta { flex-direction: row-reverse; }
    .message-actions { justify-content: flex-end; }
  }

  &--assistant {
    .message-content {
      background: var(--color-bg-secondary);
      border-radius: var(--radius-sm) var(--radius-lg) var(--radius-lg) var(--radius-lg);
    }
  }
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message-body {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.message-confidence {
  padding: 1px 6px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: 10px;
  font-size: 11px;
}

.message-content {
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;

  :deep(pre) {
    margin: 8px 0;
    border-radius: var(--radius-md);
    overflow-x: auto;
  }

  :deep(code) {
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 13px;
  }

  :deep(p) {
    margin: 6px 0;
  }

  :deep(ul), :deep(ol) {
    padding-left: 20px;
  }
}

.message-citations {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cite-tag {
  padding: 3px 10px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--radius-sm);
  font-size: 12px;
  transition: background var(--transition-fast);

  &:hover { background: var(--color-primary); color: #fff; }
}

.message-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.message:hover .message-actions { opacity: 1; }

.action-btn {
  padding: 4px;
  font-size: 14px;
  border-radius: var(--radius-sm);
  &:hover { background: var(--color-bg-tertiary); }
}
</style>
