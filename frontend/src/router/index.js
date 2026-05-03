import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: () => import('@/views/ChatIndex.vue'),
    meta: { title: '问答' },
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('@/views/KnowledgeManage.vue'),
    meta: { title: '知识库管理' },
  },
  {
    path: '/preview',
    name: 'Preview',
    component: () => import('@/views/DocumentPreview.vue'),
    meta: { title: '原文预览' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SystemSettings.vue'),
    meta: { title: '系统设置' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '问答'} - 校园学术RAG`
})

export default router
