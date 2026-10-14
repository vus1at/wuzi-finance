/**
 * 债务概况接口
 * 用 mock 聚合，接后端后改 USE_MOCK = false
 */
import request from '@/utils/request'
import { getAllMockLedgers, type Ledger } from './ledger'

const USE_MOCK = true

export interface DebtKPI {
  total_debt: number
  overdue_debt: number
  high_risk_debt: number
  supplier_count: number
  overdue_rate: number
}

export interface DebtRow {
  ledger_id: number
  supplier_id?: number
  supplier_name?: string
  project_id?: number
  project_name?: string
  material_category?: string
  total_debt: number
  overdue_total: number
  overdue_within_3m: number
  overdue_3_6m: number
  overdue_6_12m: number
  overdue_over_1y: number
  max_overdue_days: number
  debt_grade?: string
  risk_category?: string
}

export interface DebtOverview {
  kpi: DebtKPI
  rows: DebtRow[]
}

function aggregate(rows: Ledger[]): DebtOverview {
  const detail: DebtRow[] = rows
    .filter((r) => (r.upstream_debt_total_amount || 0) > 0)
    .map((r) => {
      const ov3 = r.upstream_debt_overdue_within_3m || 0
      const ov36 = r.upstream_debt_overdue_3_6m || 0
      const ov612 = r.upstream_debt_overdue_6_12m || 0
      const ov1y = r.upstream_debt_overdue_over_1y || 0
      return {
        ledger_id: r.id,
        supplier_id: r.supplier_id ?? undefined,
        supplier_name: r.supplier_name,
        project_id: r.project_id ?? undefined,
        project_name: r.project_name,
        material_category: r.material_category,
        total_debt: r.upstream_debt_total_amount || 0,
        overdue_total: ov3 + ov36 + ov612 + ov1y,
        overdue_within_3m: ov3,
        overdue_3_6m: ov36,
        overdue_6_12m: ov612,
        overdue_over_1y: ov1y,
        max_overdue_days: r.upstream_debt_max_overdue_days || 0,
        debt_grade: r.debt_grade,
        risk_category: r.existing_risk_category,
      }
    })

  const total = detail.reduce((s, r) => s + r.total_debt, 0)
  const overdue = detail.reduce((s, r) => s + r.overdue_total, 0)
  const highRisk = detail
    .filter((r) => r.debt_grade === '高风险')
    .reduce((s, r) => s + r.total_debt, 0)
  const supplierCount = new Set(detail.map((r) => r.supplier_id).filter(Boolean)).size

  return {
    kpi: {
      total_debt: round(total),
      overdue_debt: round(overdue),
      high_risk_debt: round(highRisk),
      supplier_count: supplierCount,
      overdue_rate: total > 0 ? round((overdue / total) * 100) : 0,
    },
    rows: detail.sort((a, b) => b.total_debt - a.total_debt),
  }
}

function round(v: number) {
  return Math.round(v * 100) / 100
}

export const getDebtOverviewApi = async (): Promise<DebtOverview> => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 200))
    return aggregate(getAllMockLedgers())
  }
  return request.get<any, DebtOverview>('/debt/overview')
}