<template>
  <div class="chat-page">
    <!-- 对话主区域 -->
    <div class="chat-main">
      <ChatToolbar />
      <div class="chat-messages" ref="messagesRef">
        <div v-if="currentMessages.length === 0" class="chat-empty">
          <div class="empty-icon">📚</div>
          <div class="empty-title">校园学术智能RAG检索系统</div>
          <div class="empty-desc">上传学术文档，精准问答，引用溯源</div>
          <div class="empty-hints">
            <button v-for="hint in defaultHints" :key="hint" class="hint-btn" @click="sendHint(hint)">
              {{ hint }}
            </button>
          </div>
        </div>
        <MessageItem
          v-for="msg in currentMessages"
          :key="msg.id"
          :message="msg"
          @cite-click="handleCiteClick"
        />
      </div>
      <ChatInput @send="handleSend" :disabled="chatStore.generating" />
    </div>

    <!-- 引用溯源面板 -->
    <transition name="slide">
      <CitationPanel
        v-if="citationPanelVisible"
        :citations="activeCitations"
        @close="citationPanelVisible = false"
      />
    </transition>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/store/chat'
import { useUserStore } from '@/store/user'
import { queryApi } from '@/api/chat'
import { genId } from '@/utils/common'
import MessageItem from '@/components/chat/MessageItem.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import ChatToolbar from '@/components/chat/ChatToolbar.vue'
import CitationPanel from '@/components/chat/CitationPanel.vue'

const chatStore = useChatStore()
const userStore = useUserStore()
const { currentMessages } = storeToRefs(chatStore)

const messagesRef = ref(null)
const citationPanelVisible = ref(false)
const activeCitations = ref([])

const defaultHints = [
  '什么是梯度下降？',
  '请梳理机器学习的重点知识点',
  '解释反向传播算法的推导过程',
]

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

async function handleSend(text) {
  if (!text.trim() || chatStore.generating) return

  // 确保有当前会话
  if (!chatStore.currentSessionId) {
    chatStore.createSession()
  }

  // 添加用户消息
  const userMsg = { id: genId(), role: 'user', content: text }
  chatStore.addMessage(null, userMsg)
  scrollToBottom()

  // 添加助手占位消息
  const assistantMsg = { id: genId(), role: 'assistant', content: '', citations: [], confidence: 0 }
  chatStore.addMessage(null, assistantMsg)
  chatStore.generating = true

  try {
    const history = currentMessages.value
      .filter((m) => m.id !== assistantMsg.id && m.id !== userMsg.id)
      .slice(-10)
      .map((m) => ({ query: m.role === 'user' ? m.content : '', answer: m.role === 'assistant' ? m.content : '' }))
      .filter((h) => h.query)

    const res = await queryApi({
      query: text,
      top_k: userStore.config.topK,
      scene_type: userStore.config.sceneType,
      history,
    })

    chatStore.updateLastAssistant(null, res.answer || '未获取到回答')

    // 更新引用和置信度
    const session = chatStore.currentSession
    if (session) {
      const last = [...session.messages].reverse().find((m) => m.role === 'assistant')
      if (last) {
        last.citations = res.citations || []
        last.confidence = res.confidence || 0
      }
    }

    // 自动展开引用面板
    if (res.citations?.length && userStore.config.autoExpandCitation) {
      activeCitations.value = res.citations
      citationPanelVisible.value = true
    }
  } catch (e) {
    chatStore.updateLastAssistant(null, '查询失败，请检查后端服务是否正常运行。')
  } finally {
    chatStore.generating = false
    scrollToBottom()
  }
}

function sendHint(hint) {
  handleSend(hint)
}

function handleCiteClick(citations) {
  activeCitations.value = citations
  citationPanelVisible.value = true
}

// 切换会话时滚动到底部
watch(() => chatStore.currentSessionId, () => scrollToBottom())
</script>

<style lang="scss" scoped>
.chat-page {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.chat-empty {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.empty-icon { font-size: 48px; }
.empty-title { font-size: 20px; font-weight: 600; color: var(--color-text); }
.empty-desc { font-size: 14px; color: var(--color-text-tertiary); }

.empty-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.hint-btn {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  font-size: 13px;
  background: var(--color-bg);
  transition: all var(--transition-fast);

  &:hover {
    border-color: var(--color-primary);
    color: var(--color-primary);
    background: var(--color-primary-light);
  }
}
</style>
