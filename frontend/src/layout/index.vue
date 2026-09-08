<template>
  <el-container class="app-wrapper">
    <el-header class="app-header">
      <div class="logo">
        <img src="@/assets/logo/LOGO.png" alt="logo" style="height: 32px;" />
        <span class="title">甲丁智能体</span>
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
              <el-dropdown-item>角色: {{ userStore.userInfo?.role }}</el-dropdown-item>
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
import { ref, onMounted } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { mockAphrLogin } from '@/api/auth'

const userStore = useUserStore()
const isDark = ref(false)

const toggleTheme = (val: boolean) => {
  if (val) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const handleLogout = () => {
  userStore.logout()
}

onMounted(async () => {
  // 模拟 APHR SSO 自动登录
  if (!userStore.token) {
    const res: any = await mockAphrLogin('EMP1001')
    userStore.setToken(res.token)
    userStore.setUserInfo(res.user)
  }
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
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}
.logo .title {
  font-size: 20px;
  font-weight: bold;
  color: var(--color-primary);
}
.right-menu {
  display: flex;
  align-items: center;
  gap: 20px;
}
.user-info {
  cursor: pointer;
  color: var(--text-primary);
  display: flex;
  align-items: center;
}
.app-main {
  flex: 1;
  background-color: var(--bg-base);
  padding: 20px;
  overflow-x: hidden;
  overflow-y: auto;
}
</style>
