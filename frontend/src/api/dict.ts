import request from '@/utils/request'

export interface DictData {
  key: string
  label: string
  group: string
  desc: string
  items: string[]
}

export const listDictsApi = () =>
  request.get<any, DictData[]>('/dicts')

export const getDictApi = (key: string) =>
  request.get<any, DictData>(`/dicts/${key}`)

export const updateDictApi = (key: string, items: string[]) =>
  request.put<any, DictData>(`/dicts/${key}`, { items })