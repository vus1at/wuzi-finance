import request from '@/utils/request'

export interface Project {
  id: number
  name: string
  category?: string
  sub_company?: string
  addr?: string
  status: string
  created_at?: string
}

export interface ProjectCreate {
  name: string
  category?: string
  sub_company?: string
  addr?: string
  status?: string
}

export const listProjectsApi = (params?: {
  keyword?: string
  category?: string
  status_filter?: string
}) => request.get<any, Project[]>('/projects', { params })

export const createProjectApi = (data: ProjectCreate) =>
  request.post<any, Project>('/projects', data)

export const updateProjectApi = (id: number, data: Partial<ProjectCreate>) =>
  request.put<any, Project>(`/projects/${id}`, data)

export const deleteProjectApi = (id: number) =>
  request.delete(`/projects/${id}`)

export const toggleProjectStatusApi = (id: number, status: string) =>
  request.patch<any, Project>(`/projects/${id}/status`, { status })