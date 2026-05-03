<template>
  <div class="chat-toolbar">
    <div class="toolbar-left">
      <span class="toolbar-title">{{ chatStore.currentSession?.title || '新对话' }}</span>
    </div>
    <div class="toolbar-right">
      <button class="toolbar-btn" @click="handleExport" title="导出为Markdown">📤</button>
      <button class="toolbar-btn" @click="handleClear" title="清空对话">🗑️</button>
    </div>
  </div>
</template>

<script setup>
import { ElMessageBox, ElMessage } from 'element-plus'
import { useChatStore } from '@/store/chat'
import { exportChatAsMarkdown, downloadText } from '@/utils/common'

const chatStore = useChatStore()

function handleExport() {
  if (!chatStore.currentMessages.length) {
    ElMessage.warning('当前没有对话内容')
    return
  }
  const md = exportChatAsMarkdown(chatStore.currentMessages)
  downloadText('对话导出.md', md)
  ElMessage.success('已导出')
}

async function handleClear() {
  if (!chatStore.currentMessages.length) return
  try {
    await ElMessageBox.confirm('确定清空当前对话？', '确认')
    chatStore.clearCurrentSession()
  } catch {}
}
</script>

<style lang="scss" scoped>
.chat-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 24px;
  border-bottom: 1px solid var(--color-border);
  min-height: var(--header-height);
}

.toolbar-title {
  font-size: 14px;
  font-weight: 500;
}

.toolbar-right {
  display: flex;
  gap: 4px;
}

.toolbar-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  font-size: 14px;
  &:hover { background: var(--color-bg-tertiary); }
}
</style>
