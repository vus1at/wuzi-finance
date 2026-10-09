import request from '@/utils/request'

export interface Role {
  id: number
  role_name: string
  role_code: string
  description?: string
}

export interface SysUser {
  id: number
  username: string
  real_name?: string
  phone?: string
  status: number
  role_ids: number[]
  role_names: string[]
  created_at?: string
}

export interface UserCreate {
  username: string
  password: string
  real_name?: string
  phone?: string
  status?: number
  role_ids?: number[]
}

export interface UserUpdate {
  real_name?: string
  phone?: string
  status?: number
  role_ids?: number[]
}

export const listRolesApi = () =>
  request.get<any, Role[]>('/sys-users/roles')

export const listUsersApi = (params?: { keyword?: string; status_filter?: number }) =>
  request.get<any, SysUser[]>('/sys-users', { params })

export const createUserApi = (data: UserCreate) =>
  request.post<any, SysUser>('/sys-users', data)

export const updateUserApi = (id: number, data: UserUpdate) =>
  request.put<any, SysUser>(`/sys-users/${id}`, data)

export const deleteUserApi = (id: number) =>
  request.delete(`/sys-users/${id}`)

export const resetPasswordApi = (id: number, newPassword: string) =>
  request.post(`/sys-users/${id}/reset-password`, { new_password: newPassword })