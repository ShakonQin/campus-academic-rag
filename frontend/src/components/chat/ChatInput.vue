<template>
  <div class="chat-input-wrapper">
    <div class="chat-input">
      <textarea
        ref="inputRef"
        v-model="text"
        :placeholder="disabled ? '正在生成中...' : '输入问题，Enter发送，Shift+Enter换行'"
        :disabled="disabled"
        rows="1"
        @keydown="handleKeydown"
        @input="autoResize"
      ></textarea>
      <button class="send-btn" :disabled="!text.trim() || disabled" @click="handleSend">
        <span v-if="disabled" class="stop-icon">■</span>
        <span v-else>↑</span>
      </button>
    </div>
    <div class="input-hint">
      <span>Enter 发送 · Shift+Enter 换行</span>
      <span v-if="disabled">生成中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['send'])
const text = ref('')
const inputRef = ref(null)

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function handleSend() {
  if (text.value.trim() && !props.disabled) {
    emit('send', text.value.trim())
    text.value = ''
    nextTick(() => autoResize())
  }
}

function autoResize() {
  const el = inputRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 160) + 'px'
  }
}
</script>

<style lang="scss" scoped>
.chat-input-wrapper {
  padding: 12px 24px 16px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg);
}

.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  background: var(--color-bg-secondary);
  transition: border-color var(--transition-fast);

  &:focus-within { border-color: var(--color-primary); }

  textarea {
    flex: 1;
    resize: none;
    background: transparent;
    color: var(--color-text);
    font-size: 14px;
    line-height: 1.5;
    max-height: 160px;

    &::placeholder { color: var(--color-text-placeholder); }
    &:disabled { opacity: 0.6; }
  }
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
  transition: opacity var(--transition-fast);

  &:disabled { opacity: 0.4; cursor: not-allowed; }
  &:not(:disabled):hover { opacity: 0.85; }
}

.stop-icon { font-size: 12px; }

.input-hint {
  display: flex;
  justify-content: space-between;
  padding: 4px 4px 0;
  font-size: 11px;
  color: var(--color-text-placeholder);
}
</style>
