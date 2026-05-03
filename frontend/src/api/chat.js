import request from './index'

/**
 * 发送查询（非流式）
 */
export function queryApi(data) {
  return request.post('/query', data)
}

/**
 * 健康检查
 */
export function healthCheck() {
  return request.get('/health')
}

/**
 * 获取系统统计
 */
export function getStats() {
  return request.get('/stats')
}
