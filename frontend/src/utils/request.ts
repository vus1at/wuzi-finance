import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const service = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 20000,
})

service.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

service.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err.response?.status
    const msg = err.response?.data?.detail ?? '请求失败'
    const url = err.config?.url ?? ''

    if (status === 401) {
      // 登录接口的401是密码错误
      if (url.includes('/auth/login')) {
        ElMessage.error(msg)   // 显示后端返回的"用户名或密码错误"
        return Promise.reject(err)
      }
      // 其他接口的401才是token过期
      localStorage.removeItem('token')
      ElMessage.error('登录已过期，请重新登录')
      if (router.currentRoute.value.path !== '/login') {
        router.replace({
          path: '/login',
          query: { redirect: router.currentRoute.value.fullPath },
        })
      }
    } else if (status === 403) {
      ElMessage.error('无操作权限')
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(err)
  }
)

export default service