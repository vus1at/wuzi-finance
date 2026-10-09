import request from '@/utils/request'

export interface Project {
  id: number
  name: string
  short_name?: string
  category?: string
  subsidiary_id?: number | null
  subsidiary_name?: string | null
  address?: string
  status: number          // 1启用 0停用
  created_at?: string
}

export interface ProjectCreate {
  name: string
  short_name?: string
  category?: string
  subsidiary_id?: number | null
  address?: string
  status?: number
}

export const listProjectsApi = (params?: {
  keyword?: string
  category?: string
  status_filter?: number
}) => request.get<any, Project[]>('/projects', { params })

export const createProjectApi = (data: ProjectCreate) =>
  request.post<any, Project>('/projects', data)

export const updateProjectApi = (id: number, data: Partial<ProjectCreate>) =>
  request.put<any, Project>(`/projects/${id}`, data)

export const deleteProjectApi = (id: number) =>
  request.delete(`/projects/${id}`)

export const toggleProjectStatusApi = (id: number, status: number) =>
  request.patch<any, Project>(`/projects/${id}/status`, { status })