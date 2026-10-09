import request from '@/utils/request'

export interface Supplier {
  id: number
  name: string
  type?: number
  contact_name?: string
  contact_mobile?: string
  company_address?: string
  business_scope?: string
  amount?: number
  established_date?: string
  status?: string
  created_at?: string
}

export interface SupplierCreate {
  name: string
  type?: number
  contact_name?: string
  contact_mobile?: string
  company_address?: string
  business_scope?: string
  amount?: number
  established_date?: string
}

export const listSuppliersApi = (params?: { keyword?: string; type_filter?: number }) =>
  request.get<any, Supplier[]>('/suppliers', { params })

export const createSupplierApi = (data: SupplierCreate) =>
  request.post<any, Supplier>('/suppliers', data)

export const updateSupplierApi = (id: number, data: Partial<SupplierCreate>) =>
  request.put<any, Supplier>(`/suppliers/${id}`, data)

export const deleteSupplierApi = (id: number) =>
  request.delete(`/suppliers/${id}`)