import request from './index'

/**
 * 上传文档
 */
export function uploadDocument(data) {
  return request.post('/documents', data)
}
