<template>
  <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
    <div v-if="uploading" class="upload-progress">
      <div class="progress-info">
        <span>{{ uploadingName }}</span>
        <span class="progress-status">解析中...</span>
      </div>
      <el-progress :percentage="percentage" :stroke-width="6" />
    </div>
    <div v-else class="upload-zone" @click="triggerInput">
      <div class="upload-icon">📎</div>
      <div class="upload-text">拖放文件到此处，或点击上传</div>
      <div class="upload-hint">支持 PDF / PPTX / DOCX / MD / TXT</div>
    </div>
    <input
      ref="fileInput"
      type="file"
      multiple
      accept=".pdf,.pptx,.ppt,.docx,.doc,.md,.txt"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadDocument } from '@/api/document'
import { getFileExt } from '@/utils/common'

const props = defineProps({
  kbId: { type: String, default: 'default' },
})

const emit = defineEmits(['uploaded'])

const fileInput = ref(null)
const uploading = ref(false)
const uploadingName = ref('')
const percentage = ref(0)

const allowedExts = ['pdf', 'pptx', 'ppt', 'docx', 'doc', 'md', 'txt']

function triggerInput() {
  fileInput.value?.click()
}

function handleFileChange(e) {
  const files = Array.from(e.target.files || [])
  processFiles(files)
  e.target.value = ''
}

function handleDrop(e) {
  const files = Array.from(e.dataTransfer?.files || [])
  processFiles(files)
}

async function processFiles(files) {
  for (const file of files) {
    const ext = getFileExt(file.name)
    if (!allowedExts.includes(ext)) {
      ElMessage.warning(`不支持的文件格式: ${file.name}`)
      continue
    }

    uploading.value = true
    uploadingName.value = file.name
    percentage.value = 10

    try {
      // 通过FormData上传文件到后端
      const res = await uploadDocument(file, {}, (e) => {
        if (e.total) {
          percentage.value = Math.min(90, Math.round((e.loaded / e.total) * 90))
        }
      })
      percentage.value = 100

      if (res.success) {
        emit('uploaded', {
          docId: res.doc_id,
          docName: res.doc_name || file.name,
          chunksCount: res.chunks_count,
          size: file.size,
          type: ext,
          uploadedAt: Date.now(),
        })
        ElMessage.success(`${file.name} 上传成功`)
      } else {
        ElMessage.error(`${file.name} 上传失败: ${res.message || '未知错误'}`)
      }
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || '未知错误'
      ElMessage.error(`${file.name} 上传失败: ${msg}`)
    } finally {
      uploading.value = false
    }
  }
}

defineExpose({ triggerInput })
</script>

<style lang="scss" scoped>
.upload-area {
  margin-bottom: 16px;
}

.upload-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);

  &:hover {
    border-color: var(--color-primary);
    background: var(--color-primary-light);
  }
}

.upload-icon { font-size: 28px; margin-bottom: 8px; }
.upload-text { font-size: 13px; color: var(--color-text-secondary); }
.upload-hint { font-size: 12px; color: var(--color-text-tertiary); margin-top: 4px; }

.upload-progress {
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
}

.progress-status { color: var(--color-primary); }
</style>
