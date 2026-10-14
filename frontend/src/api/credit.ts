/**
 * 债权概况接口
 */
import request from '@/utils/request'
import { getAllMockLedgers, type Ledger } from './ledger'

const USE_MOCK = true

export interface CreditKPI {
  receivable: number
  overdue_receivable: number
  cum_supply: number
  receive_rate: number
}

export interface CreditRow {
  ledger_id: number
  project_id?: number
  project_name?: string
  subsidiary_id?: number
  subsidiary_name?: string
  cum_supply: number
  receivable: number
  overdue_total: number
  overdue_within_3m: number
  overdue_3_6m: number
  overdue_6_12m: number
  overdue_over_1y: number
  max_overdue_days: number
}

export interface CreditOverview {
  kpi: CreditKPI
  rows: CreditRow[]
}

function aggregate(rows: Ledger[]): CreditOverview {
  // 按项目聚合（同一项目多行合并）
  const projectMap = new Map<string, CreditRow>()
  for (const r of rows) {
    const key = r.project_name || `#${r.project_id || 'unknown'}`
    const exist = projectMap.get(key)
    const cumSupply = r.yearly_supply_amount || r.monthly_supply_amount || 0
    const receivable = r.downstream_receivable_amount || 0
    const ov3 = r.downstream_overdue_receivable_within_3m || 0
    const ov36 = r.downstream_overdue_receivable_3_6m || 0
    const ov612 = r.downstream_overdue_receivable_6_12m || 0
    const ov1y = r.downstream_overdue_receivable_over_1y || 0
    const overdue = r.downstream_overdue_receivable_total || ov3 + ov36 + ov612 + ov1y

    if (exist) {
      exist.cum_supply += cumSupply
      exist.receivable += receivable
      exist.overdue_total += overdue
      exist.overdue_within_3m += ov3
      exist.overdue_3_6m += ov36
      exist.overdue_6_12m += ov612
      exist.overdue_over_1y += ov1y
      exist.max_overdue_days = Math.max(exist.max_overdue_days, r.downstream_max_overdue_days || 0)
    } else {
      projectMap.set(key, {
        ledger_id: r.id,
        project_id: r.project_id ?? undefined,
        project_name: r.project_name,
        subsidiary_id: r.subsidiary_id ?? undefined,
        subsidiary_name: r.subsidiary_name,
        cum_supply: cumSupply,
        receivable,
        overdue_total: overdue,
        overdue_within_3m: ov3,
        overdue_3_6m: ov36,
        overdue_6_12m: ov612,
        overdue_over_1y: ov1y,
        max_overdue_days: r.downstream_max_overdue_days || 0,
      })
    }
  }

  const details = Array.from(projectMap.values()).map((r) => ({
    ...r,
    cum_supply: round(r.cum_supply),
    receivable: round(r.receivable),
    overdue_total: round(r.overdue_total),
  }))

  const totalReceivable = details.reduce((s, r) => s + r.receivable, 0)
  const totalOverdue = details.reduce((s, r) => s + r.overdue_total, 0)
  const totalCumSupply = details.reduce((s, r) => s + r.cum_supply, 0)

  return {
    kpi: {
      receivable: round(totalReceivable),
      overdue_receivable: round(totalOverdue),
      cum_supply: round(totalCumSupply),
      receive_rate: totalCumSupply > 0
        ? round(((totalCumSupply - totalReceivable) / totalCumSupply) * 100)
        : 0,
    },
    rows: details.sort((a, b) => b.receivable - a.receivable),
  }
}

function round(v: number) {
  return Math.round(v * 100) / 100
}

export const getCreditOverviewApi = async (): Promise<CreditOverview> => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 200))
    return aggregate(getAllMockLedgers())
  }
  return request.get<any, CreditOverview>('/credit/overview')
}