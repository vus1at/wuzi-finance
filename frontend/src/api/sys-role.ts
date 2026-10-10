import request from '@/utils/request'

export interface Role {
  id: number
  role_name: string
  role_code: string
  description?: string
  created_at?: string
}

export interface RoleCreate {
  role_name: string
  role_code: string
  description?: string
}

export const listRolesApi = () =>
  request.get<any, Role[]>('/sys-roles')

export const createRoleApi = (data: RoleCreate) =>
  request.post<any, Role>('/sys-roles', data)

export const updateRoleApi = (id: number, data: Partial<RoleCreate>) =>
  request.put<any, Role>(`/sys-roles/${id}`, data)

export const deleteRoleApi = (id: number) =>
  request.delete(`/sys-roles/${id}`)

export const getRoleMenusApi = (id: number) =>
  request.get<any, { menu_ids: number[] }>(`/sys-roles/${id}/menus`)

export const setRoleMenusApi = (id: number, menuIds: number[]) =>
  request.put<any, { ok: boolean; count: number }>(`/sys-roles/${id}/menus`, { menu_ids: menuIds })