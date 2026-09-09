import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('app_token') || '')
  const userInfo = ref<any>(JSON.parse(localStorage.getItem('app_user') || 'null'))

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('app_token', newToken)
  }

  const setUserInfo = (info: any) => {
    userInfo.value = info
    if (info) {
      localStorage.setItem('app_user', JSON.stringify(info))
    } else {
      localStorage.removeItem('app_user')
    }
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('app_token')
    localStorage.removeItem('app_user')
  }

  return { token, userInfo, setToken, setUserInfo, logout }
})
