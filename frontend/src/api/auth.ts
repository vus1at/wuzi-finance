import request from '@/utils/request'

export interface LoginParams {
  username: string
  password: string
}

export interface UserInfo {
  id: number
  username: string
  real_name?: string
  dept?: string
  role: 'admin' | 'editor' | 'viewer'
  data_scope: string
}

export const loginApi = (data: LoginParams) =>
  request.post<any, { token: string; user: UserInfo }>('/auth/login', data)

export const getMeApi = () => request.get<any, UserInfo>('/auth/me')