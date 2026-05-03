<template>
  <aside class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <div v-if="!collapsed" class="logo">
        <span class="logo-icon">📚</span>
        <span class="logo-text">学术RAG</span>
      </div>
      <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? '展开' : '收起'">
        <span>{{ collapsed ? '▶' : '◀' }}</span>
      </button>
    </div>

    <nav class="sidebar-nav">
      <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
        <span class="nav-icon">💬</span>
        <span v-if="!collapsed" class="nav-label">问答</span>
      </router-link>
      <router-link to="/knowledge" class="nav-item" :class="{ active: $route.path === '/knowledge' }">
        <span class="nav-icon">📁</span>
        <span v-if="!collapsed" class="nav-label">知识库</span>
      </router-link>
      <router-link to="/settings" class="nav-item" :class="{ active: $route.path === '/settings' }">
        <span class="nav-icon">⚙️</span>
        <span v-if="!collapsed" class="nav-label">设置</span>
      </router-link>
    </nav>

    <div v-if="!collapsed" class="sidebar-section">
      <div class="section-header">
        <span>知识库</span>
        <button class="icon-btn" @click="showAddBase = true" title="新建知识库">+</button>
      </div>
      <div class="kb-list">
        <div
          v-for="kb in knowledgeStore.bases"
          :key="kb.id"
          class="kb-item"
          :class="{ active: kb.id === knowledgeStore.currentId }"
          @click="knowledgeStore.switchBase(kb.id)"
        >
          <span class="kb-name">{{ kb.name }}</span>
          <span class="kb-count">{{ kb.documents.length }}</span>
        </div>
      </div>
    </div>

    <div v-if="!collapsed" class="sidebar-section sidebar-section--grow">
      <div class="section-header">
        <span>对话历史</span>
        <button class="icon-btn" @click="handleNewChat" title="新对话">+</button>
      </div>
      <div class="session-list">
        <div
          v-for="s in chatStore.sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: s.id === chatStore.currentSessionId }"
          @click="chatStore.switchSession(s.id)"
        >
          <span class="session-title">{{ s.title }}</span>
          <button class="icon-btn icon-btn--sm" @click.stop="chatStore.deleteSession(s.id)" title="删除">×</button>
        </div>
      </div>
    </div>

    <!-- 新建知识库弹窗 -->
    <el-dialog v-model="showAddBase" title="新建知识库" width="360px" :append-to-body="true">
      <el-input v-model="newBaseName" placeholder="请输入知识库名称" @keyup.enter="handleAddBase" />
      <template #footer>
        <el-button @click="showAddBase = false">取消</el-button>
        <el-button type="primary" @click="handleAddBase">确定</el-button>
      </template>
    </el-dialog>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useChatStore } from '@/store/chat'
import { useKnowledgeStore } from '@/store/knowledge'

const chatStore = useChatStore()
const knowledgeStore = useKnowledgeStore()

const collapsed = ref(false)
const showAddBase = ref(false)
const newBaseName = ref('')

function handleNewChat() {
  chatStore.createSession()
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
.sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  overflow: hidden;
  flex-shrink: 0;

  &.collapsed {
    width: var(--sidebar-collapsed-width);
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-bottom: 1px solid var(--color-border);
  min-height: var(--header-height);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
  white-space: nowrap;
}

.collapse-btn {
  color: var(--color-text-tertiary);
  font-size: 12px;
  padding: 4px;
  &:hover { color: var(--color-text); }
}

.sidebar-nav {
  padding: 8px;
  border-bottom: 1px solid var(--color-border);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  white-space: nowrap;

  &:hover { background: var(--color-bg-tertiary); color: var(--color-text); }
  &.active { background: var(--color-primary-light); color: var(--color-primary); font-weight: 500; }
}

.nav-icon { font-size: 16px; flex-shrink: 0; }

.sidebar-section {
  padding: 8px 12px;
  &--grow { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 12px;
  color: var(--color-text-tertiary);
  font-weight: 500;
}

.icon-btn {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  color: var(--color-text-tertiary);
  font-size: 14px;
  &:hover { background: var(--color-bg-tertiary); color: var(--color-text); }
  &--sm { font-size: 12px; }
}

.kb-list, .session-list {
  overflow-y: auto;
  flex: 1;
}

.kb-item, .session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
  font-size: 13px;

  &:hover { background: var(--color-bg-tertiary); }
  &.active { background: var(--color-primary-light); color: var(--color-primary); }
}

.kb-count {
  font-size: 11px;
  color: var(--color-text-tertiary);
  background: var(--color-bg-tertiary);
  padding: 1px 6px;
  border-radius: 10px;
}

.session-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
</style>
