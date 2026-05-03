import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { genId } from '@/utils/common'

const HISTORY_KEY = 'rag_chat_history'

function loadHistory() {
  const data = localStorage.getItem(HISTORY_KEY)
  return data ? JSON.parse(data) : []
}

function saveHistory(sessions) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(sessions))
}

export const useChatStore = defineStore('chat', () => {
  // 所有会话列表
  const sessions = ref(loadHistory())
  // 当前会话ID
  const currentSessionId = ref(sessions.value[0]?.id || null)
  // 正在生成中
  const generating = ref(false)

  const currentSession = computed(() =>
    sessions.value.find((s) => s.id === currentSessionId.value)
  )

  const currentMessages = computed(() => currentSession.value?.messages || [])

  function createSession(title = '新对话') {
    const session = {
      id: genId(),
      title,
      messages: [],
      createdAt: Date.now(),
    }
    sessions.value.unshift(session)
    currentSessionId.value = session.id
    saveHistory(sessions.value)
    return session
  }

  function switchSession(id) {
    currentSessionId.value = id
  }

  function deleteSession(id) {
    sessions.value = sessions.value.filter((s) => s.id !== id)
    if (currentSessionId.value === id) {
      currentSessionId.value = sessions.value[0]?.id || null
    }
    saveHistory(sessions.value)
  }

  function addMessage(sessionId, message) {
    const session = sessions.value.find((s) => s.id === (sessionId || currentSessionId.value))
    if (session) {
      session.messages.push(message)
      // 自动更新标题（用第一条用户消息）
      if (session.messages.filter((m) => m.role === 'user').length === 1 && message.role === 'user') {
        session.title = message.content.slice(0, 30) || '新对话'
      }
      saveHistory(sessions.value)
    }
  }

  function updateLastAssistant(sessionId, content) {
    const session = sessions.value.find((s) => s.id === (sessionId || currentSessionId.value))
    if (session) {
      const last = [...session.messages].reverse().find((m) => m.role === 'assistant')
      if (last) {
        last.content = content
      }
    }
  }

  function clearCurrentSession() {
    if (currentSession.value) {
      currentSession.value.messages = []
      saveHistory(sessions.value)
    }
  }

  return {
    sessions, currentSessionId, currentSession, currentMessages, generating,
    createSession, switchSession, deleteSession, addMessage,
    updateLastAssistant, clearCurrentSession,
  }
})
