<template>
  <div class="preview-page">
    <div class="preview-header">
      <button class="back-btn" @click="$router.back()">← 返回</button>
      <span class="preview-title">{{ docName || '原文预览' }}</span>
      <div class="preview-controls">
        <button @click="zoomOut" title="缩小">−</button>
        <span>{{ Math.round(scale * 100) }}%</span>
        <button @click="zoomIn" title="放大">+</button>
        <button @click="fitWidth" title="适合宽度">↔</button>
      </div>
    </div>
    <div class="preview-body">
      <div v-if="!docName" class="preview-empty">
        <div>请从知识库管理页面选择文档进行预览</div>
      </div>
      <div v-else class="preview-content" :style="{ transform: `scale(${scale})`, transformOrigin: 'top center' }">
        <div class="pdf-placeholder">
          <div class="placeholder-icon">📄</div>
          <div class="placeholder-text">文档预览：{{ docName }}</div>
          <div class="placeholder-hint">PDF.js 预览组件将在集成阶段加载实际文档</div>
          <div v-if="highlightPage" class="highlight-info">
            引用定位：第 {{ highlightPage }} 页
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const docName = ref('')
const highlightPage = ref(null)
const scale = ref(1)

onMounted(() => {
  docName.value = route.query.docName || ''
  highlightPage.value = route.query.page ? Number(route.query.page) : null
})

function zoomIn() { scale.value = Math.min(scale.value + 0.1, 3) }
function zoomOut() { scale.value = Math.max(scale.value - 0.1, 0.3) }
function fitWidth() { scale.value = 1 }
</script>

<style lang="scss" scoped>
.preview-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 24px;
  border-bottom: 1px solid var(--color-border);
}

.back-btn {
  color: var(--color-primary);
  font-size: 14px;
  &:hover { text-decoration: underline; }
}

.preview-title {
  flex: 1;
  font-weight: 500;
  font-size: 14px;
}

.preview-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;

  button {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    font-size: 14px;
    &:hover { border-color: var(--color-primary); color: var(--color-primary); }
  }
}

.preview-body {
  flex: 1;
  overflow: auto;
  background: var(--color-bg-tertiary);
  padding: 24px;
}

.preview-empty {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

.pdf-placeholder {
  max-width: 700px;
  margin: 0 auto;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 2px 8px var(--color-shadow);
}

.placeholder-icon { font-size: 64px; margin-bottom: 16px; }
.placeholder-text { font-size: 16px; font-weight: 500; margin-bottom: 8px; }
.placeholder-hint { font-size: 13px; color: var(--color-text-tertiary); }
.highlight-info {
  margin-top: 16px;
  padding: 8px 16px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-radius: var(--radius-md);
  font-size: 13px;
  display: inline-block;
}
</style>
