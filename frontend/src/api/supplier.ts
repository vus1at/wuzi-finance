import request from '@/utils/request'

export interface Supplier {
  id: number
  name: string
  type?: string
  contact?: string
  phone?: string
  addr?: string
  scope?: string
  capital?: string
  founded?: string
  created_at?: string
}

export interface SupplierCreate {
  name: string
  type?: string
  contact?: string
  phone?: string
  addr?: string
  scope?: string
  capital?: string
  founded?: string
}

export const listSuppliersApi = (params?: { keyword?: string; type_filter?: string }) =>
  request.get<any, Supplier[]>('/suppliers', { params })

export const createSupplierApi = (data: SupplierCreate) =>
  request.post<any, Supplier>('/suppliers', data)

export const updateSupplierApi = (id: number, data: Partial<SupplierCreate>) =>
  request.put<any, Supplier>(`/suppliers/${id}`, data)

export const deleteSupplierApi = (id: number) =>
  request.delete(`/suppliers/${id}`)