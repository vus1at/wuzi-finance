/**
 * 13 张报表配置 + mock 聚合
 * 等后端定稿：把 USE_MOCK 改成 false，每张报表接对应接口
 */
import request from '@/utils/request'
import { getAllMockLedgers, type Ledger } from './ledger'

const USE_MOCK = true

export interface ReportColumn {
  prop: string
  label: string
  width?: number
  minWidth?: number
  align?: 'left' | 'center' | 'right'
  /** 自定义格式化；不填则原样显示 */
  formatter?: (val: any, row: any) => string
}

export interface ReportConfig {
  code: string
  name: string
  group: '核心报表' | '债务风控' | '供应商监控'
  desc: string
  columns: ReportColumn[]
  fetch: () => Promise<any[]>
  /** 表头样式（默认灰色） */
  headerStyle?: 'navy' | 'gray'
}

// ============ 工具 ============
function sum<T>(arr: T[], f: (x: T) => number) {
  return arr.reduce((s, x) => s + (f(x) || 0), 0)
}
function getOverdue(r: Ledger) {
  return (r.upstream_debt_overdue_within_3m || 0)
       + (r.upstream_debt_overdue_3_6m || 0)
       + (r.upstream_debt_overdue_6_12m || 0)
       + (r.upstream_debt_overdue_over_1y || 0)
}
function fmt2(v: any) {
  const n = Number(v)
  if (!isFinite(n)) return v ?? '—'
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// ============ 1. 供应欠款情况表（项目维度） ============
const report01: ReportConfig = {
  code: '01', name: '供应欠款情况表', group: '核心报表',
  desc: '项目维度：供应/利润/回款/债权',
  columns: [
    { prop: 'project_name', label: '项目名称', width: 120 },
    { prop: 'subsidiary_name', label: '子分公司', width: 90 },
    { prop: 'supplier_count', label: '供应商数', width: 90, align: 'center' },
    { prop: 'month_supply', label: '本月供应', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'month_profit', label: '本月利润', width: 100, align: 'right', formatter: fmt2 },
    { prop: 'month_receive', label: '本月回款', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'year_supply', label: '年累供应', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'cum_supply', label: '开累供应', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'receivable', label: '应收债权', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'overdue_receivable', label: '逾期债权', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'max_overdue_days', label: '最长逾期', width: 100, align: 'center',
      formatter: (v) => (v > 0 ? `${v}天` : '—') },
  ],
  async fetch() {
    if (!USE_MOCK) return request.get('/report/01')
    const rows = getAllMockLedgers()
    const map = new Map<string, any>()
    for (const r of rows) {
      const key = r.project_name || '未知'
      const exist = map.get(key)
      const cum = r.yearly_supply_amount || r.monthly_supply_amount || 0
      if (exist) {
        exist.supplier_set.add(r.supplier_id)
        exist.month_supply += r.monthly_supply_amount || 0
        exist.month_profit += r.profit_management_fee || 0
        exist.month_receive += r.monthly_supply_actual_collection || 0
        exist.year_supply += r.yearly_supply_amount || 0
        exist.cum_supply += cum
        exist.receivable += r.downstream_receivable_amount || 0
        exist.overdue_receivable += r.downstream_overdue_receivable_total || 0
        exist.max_overdue_days = Math.max(exist.max_overdue_days, r.downstream_max_overdue_days || 0)
      } else {
        map.set(key, {
          project_name: key,
          subsidiary_name: r.subsidiary_name,
          supplier_set: new Set([r.supplier_id]),
          month_supply: r.monthly_supply_amount || 0,
          month_profit: r.profit_management_fee || 0,
          month_receive: r.monthly_supply_actual_collection || 0,
          year_supply: r.yearly_supply_amount || 0,
          cum_supply: cum,
          receivable: r.downstream_receivable_amount || 0,
          overdue_receivable: r.downstream_overdue_receivable_total || 0,
          max_overdue_days: r.downstream_max_overdue_days || 0,
        })
      }
    }
    return Array.from(map.values()).map((x) => ({
      ...x,
      supplier_count: x.supplier_set.size,
    }))
  },
}

// ============ 2. 子分公司欠款（区域集采） ============
function buildSubsidiaryReport(supplyCategory: '区域集采' | '内供集采'): () => Promise<any[]> {
  return async () => {
    if (!USE_MOCK) return request.get('/report/02')
    const rows = getAllMockLedgers().filter((r) => r.supply_category === supplyCategory)
    const map = new Map<string, any>()
    for (const r of rows) {
      const key = r.subsidiary_name || '未分配'
      const exist = map.get(key)
      const cum = r.yearly_supply_amount || r.monthly_supply_amount || 0
      if (exist) {
        exist.cum_supply += cum
        exist.receivable += r.downstream_receivable_amount || 0
        exist.overdue += r.downstream_overdue_receivable_total || 0
        exist.ov3 += r.downstream_overdue_receivable_within_3m || 0
        exist.ov36 += r.downstream_overdue_receivable_3_6m || 0
        exist.ov612 += r.downstream_overdue_receivable_6_12m || 0
        exist.ov1y += r.downstream_overdue_receivable_over_1y || 0
      } else {
        map.set(key, {
          subsidiary_name: key,
          supply_category: supplyCategory,
          cum_supply: cum,
          receivable: r.downstream_receivable_amount || 0,
          overdue: r.downstream_overdue_receivable_total || 0,
          ov3: r.downstream_overdue_receivable_within_3m || 0,
          ov36: r.downstream_overdue_receivable_3_6m || 0,
          ov612: r.downstream_overdue_receivable_6_12m || 0,
          ov1y: r.downstream_overdue_receivable_over_1y || 0,
        })
      }
    }
    return Array.from(map.values())
  }
}

const report02: ReportConfig = {
  code: '02', name: '子分公司欠款（区域集采）', group: '核心报表',
  desc: '区域集采应收账款',
  columns: [
    { prop: 'subsidiary_name', label: '子分公司', width: 110 },
    { prop: 'supply_category', label: '供应类别', width: 100 },
    { prop: 'cum_supply', label: '开累供应', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'receivable', label: '应收债权', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'overdue', label: '逾期合计', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'ov3', label: '3月以下', width: 100, align: 'right', formatter: fmt2 },
    { prop: 'ov36', label: '3-6月', width: 100, align: 'right', formatter: fmt2 },
    { prop: 'ov612', label: '6-12月', width: 100, align: 'right', formatter: fmt2 },
    { prop: 'ov1y', label: '1年以上', width: 100, align: 'right', formatter: fmt2 },
  ],
  fetch: buildSubsidiaryReport('区域集采'),
}

const report03: ReportConfig = {
  ...report02,
  code: '03', name: '子分公司欠款（内供集采）', desc: '内供集采应收账款',
  fetch: buildSubsidiaryReport('内供集采'),
}

// ============ 4. 供应金额利润表（按月） ============
const report04: ReportConfig = {
  code: '04', name: '供应金额利润表', group: '核心报表',
  desc: '月度供应/回款/利润',
  columns: [
    { prop: 'month', label: '月份', width: 90, align: 'center' },
    { prop: 'supply', label: '供应金额', width: 120, align: 'right', formatter: fmt2 },
    { prop: 'receive', label: '回款金额', width: 120, align: 'right', formatter: fmt2 },
    { prop: 'profit', label: '利润/管理费', width: 120, align: 'right', formatter: fmt2 },
  ],
  async fetch() {
    if (!USE_MOCK) return request.get('/report/04')
    // mock：仅当年 9 月有数，前面用静态模拟
    const rows = getAllMockLedgers()
    const monthly = [3, 4, 5, 6, 7, 8].map((m) => ({
      month: `${m}月`,
      supply: 220 + m * 10,
      receive: 160 + m * 8,
      profit: 18 + m * 1.2,
    }))
    monthly.push({
      month: '9月',
      supply: sum(rows, (r) => r.monthly_supply_amount || 0),
      receive: sum(rows, (r) => r.monthly_supply_actual_collection || 0),
      profit: sum(rows, (r) => r.profit_management_fee || 0),
    })
    return monthly
  },
}

// ============ 5. 资金收支计划表 ============
const report05: ReportConfig = {
  code: '05', name: '资金收支计划表', group: '核心报表',
  desc: '各集采中心资金计划',
  columns: [
    { prop: 'project_name', label: '项目', width: 120 },
    { prop: 'supplier_name', label: '供应商', minWidth: 180 },
    { prop: 'material_category', label: '物资', width: 100 },
    { prop: 'debt_total', label: '到期应付', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'plan_supply', label: '计划供应', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'plan_receive', label: '计划回款', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'plan_pay', label: '计划支付', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'gap', label: '收支结余', width: 110, align: 'right',
      formatter: (v) => (v >= 0 ? '+' : '') + fmt2(v) },
  ],
  async fetch() {
    if (!USE_MOCK) return request.get('/report/05')
    const rows = getAllMockLedgers()
    return rows.map((r) => {
      const planReceive = r.monthly_supply_amount || 0
      const planPay = r.upstream_debt_due_payable || r.upstream_debt_total_amount || 0
      return {
        project_name: r.project_name,
        supplier_name: r.supplier_name,
        material_category: r.material_category,
        debt_total: r.upstream_debt_due_payable || 0,
        plan_supply: r.monthly_supply_amount || 0,
        plan_receive: planReceive,
        plan_pay: planPay,
        gap: planReceive - planPay,
      }
    })
  },
}

// ============ 6-13（占位，下一批实现） ============
const placeholder = (code: string, name: string, group: ReportConfig['group'], desc: string): ReportConfig => ({
  code, name, group, desc,
  columns: [{ prop: 'info', label: '状态', minWidth: 200 }],
  async fetch() {
    return [{ info: '该报表将在下一批实现' }]
  },
})

// ============ 汇总 ============
export const ALL_REPORTS: ReportConfig[] = [
  report01, report02, report03, report04, report05,
  placeholder('06', '上游采购债务汇总表', '债务风控', '按管理类型汇总'),
  placeholder('07', '上游采购债务明细', '债务风控', '按单位明细'),
  placeholder('08', '区域集采超1000万供应商', '债务风控', '大额供应商监控'),
  placeholder('09', '内供集采超1000万供应商', '债务风控', '大额供应商监控'),
  placeholder('10', '高风险供应商明细', '供应商监控', '债务分级=高风险'),
  placeholder('11', '高风险排查表', '供应商监控', '两拖欠/诉讼'),
  placeholder('12', '区域集采债务明细', '供应商监控', '集采中心债务'),
  placeholder('13', '内供集采债务明细', '供应商监控', '材料厂债务'),
]

export const getReportByCode = (code: string) =>
  ALL_REPORTS.find((r) => r.code === code)

export const REPORT_GROUPS: { key: ReportConfig['group']; label: string }[] = [
  { key: '核心报表', label: '核心报表' },
  { key: '债务风控', label: '债务风控' },
  { key: '供应商监控', label: '供应商监控' },
]