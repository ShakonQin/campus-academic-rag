<template>
  <div class="settings-page">
    <div class="page-header">
      <h2>系统设置</h2>
    </div>

    <div class="settings-body">
      <!-- 基础配置 -->
      <div class="settings-section">
        <h3>基础配置</h3>
        <div class="setting-item">
          <label>界面主题</label>
          <div class="setting-control">
            <el-radio-group v-model="config.theme" @change="applyConfig">
              <el-radio-button value="light">浅色</el-radio-button>
              <el-radio-button value="dark">深色</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="setting-item">
          <label>字体大小</label>
          <div class="setting-control">
            <el-slider v-model="config.fontSize" :min="12" :max="18" :step="1" style="width: 200px" @change="applyConfig" />
            <span class="setting-value">{{ config.fontSize }}px</span>
          </div>
        </div>
        <div class="setting-item">
          <label>自动展开引用面板</label>
          <div class="setting-control">
            <el-switch v-model="config.autoExpandCitation" @change="applyConfig" />
          </div>
        </div>
      </div>

      <!-- 检索配置 -->
      <div class="settings-section">
        <h3>检索配置</h3>
        <div class="setting-item">
          <label>Top-K 返回数量</label>
          <div class="setting-control">
            <el-input-number v-model="config.topK" :min="1" :max="50" @change="applyConfig" />
          </div>
        </div>
        <div class="setting-item">
          <label>默认场景</label>
          <div class="setting-control">
            <el-select v-model="config.sceneType" @change="applyConfig">
              <el-option label="通用问答" value="general" />
              <el-option label="考点梳理" value="exam" />
              <el-option label="作业答疑" value="homework" />
              <el-option label="论文解读" value="paper" />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 数据管理 -->
      <div class="settings-section">
        <h3>数据管理</h3>
        <div class="setting-item">
          <label>清空对话历史</label>
          <div class="setting-control">
            <el-button type="danger" plain size="small" @click="handleClearHistory">清空</el-button>
          </div>
        </div>
        <div class="setting-item">
          <label>系统状态</label>
          <div class="setting-control">
            <el-button size="small" @click="checkHealth">检查服务状态</el-button>
            <span v-if="healthStatus" class="health-status" :class="healthStatus">
              {{ healthStatus === 'ok' ? '正常' : '异常' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 关于 -->
      <div class="settings-section">
        <h3>关于</h3>
        <div class="about-info">
          <p><strong>校园学术智能RAG检索系统</strong> v1.0.0</p>
          <p>专为校园学习科研场景打造的私有化RAG问答系统</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { healthCheck } from '@/api/chat'

const userStore = useUserStore()
const config = reactive({ ...userStore.config })
const healthStatus = ref('')

function applyConfig() {
  userStore.updateConfig({ ...config })
}

async function handleClearHistory() {
  try {
    await ElMessageBox.confirm('确定要清空所有对话历史吗？此操作不可恢复。', '确认', { type: 'warning' })
    localStorage.removeItem('rag_chat_history')
    ElMessage.success('对话历史已清空，请刷新页面')
  } catch {}
}

async function checkHealth() {
  try {
    const res = await healthCheck()
    healthStatus.value = res.status === 'ok' ? 'ok' : 'error'
  } catch {
    healthStatus.value = 'error'
  }
}
</script>

<style lang="scss" scoped>
.settings-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
  h2 { font-size: 16px; font-weight: 600; }
}

.settings-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  max-width: 680px;
}

.settings-section {
  margin-bottom: 32px;

  h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--color-border-light);
  }
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;

  label {
    font-size: 13px;
    color: var(--color-text-secondary);
    flex-shrink: 0;
    min-width: 140px;
  }
}

.setting-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-value {
  font-size: 12px;
  color: var(--color-text-tertiary);
  min-width: 36px;
}

.health-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  &.ok { color: var(--color-success); background: rgba(0, 180, 42, 0.1); }
  &.error { color: var(--color-danger); background: rgba(245, 63, 63, 0.1); }
}

.about-info {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 2;
}
</style>
