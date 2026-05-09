import request from './index'

/**
 * 上传文档（文件上传）
 * @param {File} file - 文件对象
 * @param {object} meta - 元数据 { course_name, chapter, tags }
 * @param {Function} onProgress - 进度回调
 */
export function uploadDocument(file, meta = {}, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('course_name', meta.course_name || '')
  formData.append('chapter', meta.chapter || '')
  formData.append('tags', (meta.tags || []).join(','))

  return request.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
    onUploadProgress: onProgress,
  })
}
