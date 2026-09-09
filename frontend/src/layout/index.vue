<template>
  <el-container class="app-wrapper">
    <el-header class="app-header">
      <div class="logo">
        <img src="@/assets/logo/LOGO.png" alt="logo" style="height: 38px; border-radius: 50%; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />
        <span class="title">甲丁智能体</span>
      </div>
      
      <div class="top-menu">
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          router
          class="nav-menu"
          :ellipsis="false"
        >
          <el-menu-item index="/dashboard" v-if="userStore.userInfo?.role === 'TEAM_LEADER'">
            <el-icon><Monitor /></el-icon>
            生产工作台
          </el-menu-item>
          <el-menu-item index="/data" v-if="userStore.userInfo?.role === 'DATA_ADMIN'">
            <el-icon><Coin /></el-icon>
            数据维护
          </el-menu-item>
          <el-menu-item index="/settings" v-if="userStore.userInfo?.role === 'SYS_ADMIN'">
            <el-icon><Setting /></el-icon>
            系统设置
          </el-menu-item>
        </el-menu>
      </div>

      <div class="right-menu">
        <el-switch
          v-model="isDark"
          class="theme-switch"
          inline-prompt
          active-text="🌙"
          inactive-text="☀️"
          @change="toggleTheme"
        />
        <el-dropdown>
          <span class="el-dropdown-link user-info">
            {{ userStore.userInfo?.name || '未登录' }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item disabled>当前角色: {{ userRoleName }}</el-dropdown-item>
              <el-dropdown-item divided @click="switchRole('TEAM_LEADER')">切换测试: 班组长</el-dropdown-item>
              <el-dropdown-item @click="switchRole('DATA_ADMIN')">切换测试: 数据管理员</el-dropdown-item>
              <el-dropdown-item @click="switchRole('SYS_ADMIN')">切换测试: 系统管理员</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Monitor, Coin, Setting } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { mockAphrLogin } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isDark = ref(false)

const activeMenu = computed(() => route.path)

const userRoleName = computed(() => {
  const r = userStore.userInfo?.role
  if (r === 'TEAM_LEADER') return '班组长'
  if (r === 'DATA_ADMIN') return '数据管理员'
  if (r === 'SYS_ADMIN') return '系统管理员'
  return r || '未知'
})

const toggleTheme = (val: boolean) => {
  if (val) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const switchRole = (role: string) => {
  let name = 'Mock User'
  if (role === 'TEAM_LEADER') name = '张工 (班组长)'
  if (role === 'DATA_ADMIN') name = '李工 (数据管理员)'
  if (role === 'SYS_ADMIN') name = '王工 (系统管理员)'
  
  userStore.setUserInfo({ ...userStore.userInfo, role, name })
  
  if (role === 'TEAM_LEADER') router.push('/dashboard')
  if (role === 'DATA_ADMIN') router.push('/data')
  if (role === 'SYS_ADMIN') router.push('/settings')
}

const handleLogout = () => {
  userStore.logout()
}

onMounted(async () => {
  if (!userStore.token) {
    const res: any = await mockAphrLogin('EMP1001')
    userStore.setToken(res.token)
    userStore.setUserInfo(res.user)
  }
  // 如果当前路由不在权限内，做个简单的重定向
  setTimeout(() => {
    const r = userStore.userInfo?.role
    if (r === 'TEAM_LEADER' && route.path !== '/dashboard') router.push('/dashboard')
    if (r === 'DATA_ADMIN' && route.path !== '/data') router.push('/data')
    if (r === 'SYS_ADMIN' && route.path !== '/settings') router.push('/settings')
  }, 100)
})
</script>

<style scoped>
.app-wrapper {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}
.app-header {
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 240px;
}
.logo .title {
  font-size: 24px;
  font-weight: 900;
  letter-spacing: 1.5px;
  background: linear-gradient(135deg, #409EFF, #67C23A);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.03);
  margin-left: 5px;
}
.top-menu {
  flex: 1;
  display: flex;
  justify-content: center;
}
.nav-menu {
  border-bottom: none;
  height: 64px;
  background: transparent;
}
:deep(.el-menu-item) {
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  padding: 0 25px;
  color: #606266;
  transition: all 0.3s;
}
:deep(.el-menu-item.is-active) {
  font-size: 17px;
  font-weight: bold;
  color: #409EFF;
  border-bottom-width: 3px !important;
}
:deep(.el-menu-item:hover) {
  background-color: transparent !important;
  color: #409EFF !important;
}
.right-menu {
  display: flex;
  align-items: center;
  gap: 24px;
  width: 240px;
  justify-content: flex-end;
}
.user-info {
  cursor: pointer;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  font-weight: 500;
  font-size: 15px;
}
.app-main {
  flex: 1;
  background-color: var(--bg-base);
  padding: 24px;
  overflow-x: hidden;
  overflow-y: auto;
}
</style>
