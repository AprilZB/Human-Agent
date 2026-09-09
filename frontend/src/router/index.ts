import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

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
        meta: { title: '生产工作台', roles: ['TEAM_LEADER'] }
      },
      {
        path: 'data',
        name: 'DataMaintenance',
        component: () => import('@/views/data/index.vue'),
        meta: { title: '数据维护', roles: ['DATA_ADMIN'] }
      },
      {
        path: 'settings',
        name: 'SystemSettings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '系统设置', roles: ['SYS_ADMIN'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const role = userStore.userInfo?.role
  
  if (!role) {
    // 还没登录（刷新页面状态丢失），放行让他进去，Layout 里的 onMounted 会进行 mock 登录并重定向
    return next()
  }
  
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    if (!to.meta.roles.includes(role)) {
      ElMessage.error('无权访问该页面')
      // 重定向到该角色的首页
      if (role === 'TEAM_LEADER') return next('/dashboard')
      if (role === 'DATA_ADMIN') return next('/data')
      if (role === 'SYS_ADMIN') return next('/settings')
      return next(false)
    }
  }
  next()
})

export default router
