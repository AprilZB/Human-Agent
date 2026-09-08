import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const userInfo = ref<any>(null)

  const setToken = (newToken: string) => {
    token.value = newToken
  }

  const setUserInfo = (info: any) => {
    userInfo.value = info
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
  }

  return { token, userInfo, setToken, setUserInfo, logout }
})
