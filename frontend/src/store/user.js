import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { getConfig, saveConfig } from '@/api/config'

export const useUserStore = defineStore('user', () => {
  const config = ref(getConfig())

  function updateConfig(partial) {
    Object.assign(config.value, partial)
    saveConfig(config.value)
    // 应用主题
    if (partial.theme !== undefined) {
      document.documentElement.setAttribute('data-theme', partial.theme)
    }
  }

  // 初始化主题
  document.documentElement.setAttribute('data-theme', config.value.theme)

  return { config, updateConfig }
})
