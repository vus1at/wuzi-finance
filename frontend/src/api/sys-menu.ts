import request from '@/utils/request'

export interface Menu {
  id: number
  parent_id: number
  menu_name: string
  menu_code?: string
  path?: string
  component?: string
  icon?: string
  menu_type: number
  sort_order: number
  status: number
  children: Menu[]
}

export interface MenuCreate {
  parent_id?: number
  menu_name: string
  menu_code?: string
  path?: string
  component?: string
  icon?: string
  menu_type?: number
  sort_order?: number
  status?: number
}

/** 全部菜单（菜单管理页用） */
export const getMenuTreeApi = () =>
  request.get<any, Menu[]>('/menus/tree')

/** 我的菜单（侧边栏用，按角色过滤） */
export const getMyMenuTreeApi = () =>
  request.get<any, Menu[]>('/menus/me')

export const createMenuApi = (data: MenuCreate) =>
  request.post<any, Menu>('/menus', data)

export const updateMenuApi = (id: number, data: Partial<MenuCreate>) =>
  request.put<any, Menu>(`/menus/${id}`, data)

export const deleteMenuApi = (id: number) =>
  request.delete(`/menus/${id}`)