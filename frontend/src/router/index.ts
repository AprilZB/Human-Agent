import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '生产工作台' }
      },
      {
        path: 'data',
        name: 'DataMaintenance',
        component: () => import('@/views/data/index.vue'),
        meta: { title: '数据维护' }
      },
      {
        path: 'settings',
        name: 'SystemSettings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
