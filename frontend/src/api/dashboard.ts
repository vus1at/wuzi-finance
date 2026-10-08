import request from '@/utils/request'

export interface DashboardData {
  kpi: {
    month_purchase: number
    month_supply: number
    total_debt: number
    receivable: number
    month_receive: number
    overdue_rate: number
    recv_overdue_rate: number
    receive_rate: number
  }
  debt_pie: { name: string; value: number }[]
  top_projects: { name: string; value: number; material: string }[]
  top_suppliers: { name: string; value: number; pct: number }[]
  alerts: { supplier: string; project: string; value: number; days: number }[]
  overview: {
    project_count: number
    supplier_count: number
    region_supply: number
    inner_supply: number
    high_risk_debt: number
    total_profit: number
    total_overdue_debt: number
    total_overdue_recv: number
  }
}

export const getDashboardApi = () =>
  request.get<any, DashboardData>('/dashboard/overview')