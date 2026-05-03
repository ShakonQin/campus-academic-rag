// 配置相关接口（前端本地管理）

const CONFIG_KEY = 'rag_user_config'

const defaultConfig = {
  theme: 'light',
  fontSize: 14,
  autoExpandCitation: false,
  topK: 10,
  sceneType: 'general',
}

export function getConfig() {
  const data = localStorage.getItem(CONFIG_KEY)
  return data ? { ...defaultConfig, ...JSON.parse(data) } : { ...defaultConfig }
}

export function saveConfig(config) {
  localStorage.setItem(CONFIG_KEY, JSON.stringify(config))
}
