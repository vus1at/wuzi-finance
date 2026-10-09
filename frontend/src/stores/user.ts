import { defineStore } from 'pinia'
import { loginApi, getMeApi, type LoginParams, type UserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as UserInfo | null,
  }),
  getters: {
    isLogin: (s) => !!s.token,
    isAdmin: (s) => (s.user?.roles || []).includes('ADMIN'),
  },
  actions: {
    async login(params: LoginParams) {
      const { token, user } = await loginApi(params)
      this.token = token
      this.user = user
      localStorage.setItem('token', token)
    },
    async fetchMe() {
      this.user = await getMeApi()
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    },
  },
})