/**
 * 生成唯一ID
 */
export function genId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

/**
 * 格式化时间
 */
export function formatTime(date) {
  const d = new Date(date)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/**
 * 下载文本文件
 */
export function downloadText(filename, text) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

/**
 * 导出对话为Markdown
 */
export function exportChatAsMarkdown(messages) {
  const lines = messages.map((m) => {
    const role = m.role === 'user' ? '**提问**' : '**回答**'
    return `### ${role}\n\n${m.content}\n`
  })
  return `# 校园学术RAG对话导出\n\n${lines.join('\n---\n\n')}`
}

/**
 * 获取文件扩展名
 */
export function getFileExt(name) {
  return name.split('.').pop().toLowerCase()
}

/**
 * 文件大小格式化
 */
export function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}
