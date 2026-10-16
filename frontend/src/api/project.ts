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
  formatter?: (val: any, row: any) => string
}

export interface ReportConfig {
  code: string
  name: string
  group: '核心报表' | '债务风控' | '供应商监控'
  desc: string
  columns: ReportColumn[]
  fetch: () => Promise<any[]>
}

// ============ 工具 ============
function sum<T>(arr: T[], f: (x: T) => number) {
  return arr.reduce((s, x) => s + (f(x) || 0), 0)
}
function fmt2(v: any) {
  const n = Number(v)
  if (!isFinite(n)) return v ?? '—'
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 债权账龄分档工具
function creditAging(r: Ledger) {
  const ov3   = r.downstream_overdue_receivable_within_3m || 0
  const ov36  = r.downstream_overdue_receivable_3_6m || 0
  const ov612 = r.downstream_overdue_receivable_6_12m || 0
  const ov1y  = r.downstream_overdue_receivable_over_1y || 0
  const ovTotal = r.downstream_overdue_receivable_total || (ov3 + ov36 + ov612 + ov1y)
  return { ov3, ov36, ov612, ov1y, ovTotal, ovWithin1y: ov3 + ov36 + ov612 }
}

// 按【子分公司+项目】聚合的通用函数（报表 01/02/03 共用）
function aggregateBySubsidiaryProject(
  rows: Ledger[],
  fixedSupplyCategory?: string,
) {
  const map = new Map<string, any>()
  for (const r of rows) {
    const key = `${r.subsidiary_name || '_'}__${r.project_name || '_'}`
    const { ov3, ov36, ov612, ov1y, ovTotal, ovWithin1y } = creditAging(r)
    const cumSupply = r.yearly_supply_amount || r.monthly_supply_amount || 0

    const exist = map.get(key)
    if (exist) {
      exist.cum_supply += cumSupply
      exist.receivable += r.downstream_receivable_amount || 0
      exist.overdue_total += ovTotal
      exist.ov3 += ov3
      exist.ov36 += ov36
      exist.ov612 += ov612
      exist.ov_within_1y += ovWithin1y
      exist.ov1y += ov1y
    } else {
      map.set(key, {
        subsidiary_name: r.subsidiary_name || '—',
        management_type: r.management_type || '—',
        supply_category: fixedSupplyCategory || r.supply_category || '—',
        project_name: r.project_name || '—',
        cum_supply: cumSupply,
        receivable: r.downstream_receivable_amount || 0,
        overdue_total: ovTotal,
        ov3, ov36, ov612,
        ov_within_1y: ovWithin1y,
        ov1y,
      })
    }
  }
  return Array.from(map.values()).map((x, i) => ({ seq: i + 1, ...x }))
}

// 通用的 13 列定义（01/02/03 共用）
const SUBSIDIARY_PROJECT_COLUMNS: ReportColumn[] = [
  { prop: 'seq',              label: '序号',     width: 60,  align: 'center' },
  { prop: 'subsidiary_name',  label: '子分公司', width: 100 },
  { prop: 'management_type',  label: '管理类型', width: 110 },
  { prop: 'supply_category',  label: '供应类别', width: 100 },
  { prop: 'project_name',     label: '项目名称', width: 120 },
  { prop: 'cum_supply',       label: '开累供应', width: 110, align: 'right', formatter: fmt2 },
  { prop: 'receivable',       label: '应收债权', width: 110, align: 'right', formatter: fmt2 },
  { prop: 'overdue_total',    label: '逾期合计', width: 110, align: 'right', formatter: fmt2 },
  { prop: 'ov3',              label: '<3月',     width: 90,  align: 'right', formatter: fmt2 },
  { prop: 'ov36',             label: '3-6月',    width: 90,  align: 'right', formatter: fmt2 },
  { prop: 'ov612',            label: '6-12月',   width: 90,  align: 'right', formatter: fmt2 },
  { prop: 'ov_within_1y',     label: '一年以内', width: 100, align: 'right', formatter: fmt2 },
  { prop: 'ov1y',             label: '>一年',    width: 90,  align: 'right', formatter: fmt2 },
]

// ============ 1. 供应欠款情况表 ============
const report01: ReportConfig = {
  code: '01',
  name: '供应欠款情况表',
  group: '核心报表',
  desc: '开累供应 / 应收债权 / 逾期账龄',
  columns: SUBSIDIARY_PROJECT_COLUMNS,
  async fetch() {
    if (!USE_MOCK) return request.get('/report/01')
    return aggregateBySubsidiaryProject(getAllMockLedgers())
  },
}

// ============ 2/3. 子分公司欠款（区域 / 内供） ============
function buildSubsidiaryReport(
  code: string,
  name: string,
  desc: string,
  supplyCategory: '区域集采' | '内供集采',
): ReportConfig {
  return {
    code, name, group: '核心报表', desc,
    columns: SUBSIDIARY_PROJECT_COLUMNS,
    async fetch() {
      if (!USE_MOCK) return request.get(`/report/${code}`)
      const rows = getAllMockLedgers().filter((r) => r.supply_category === supplyCategory)
      return aggregateBySubsidiaryProject(rows, supplyCategory)
    },
  }
}

const report02 = buildSubsidiaryReport('02', '子分公司欠款（区域集采）', '区域集采应收账款', '区域集采')
const report03 = buildSubsidiaryReport('03', '子分公司欠款（内供集采）', '内供集采应收账款', '内供集采')

// ============ 4. 供应金额利润表 ============
const report04: ReportConfig = {
  code: '04', name: '供应金额利润表', group: '核心报表',
  desc: '月度供应 / 回款 / 利润',
  columns: [
    { prop: 'month',   label: '月份',       width: 90,  align: 'center' },
    { prop: 'supply',  label: '供应金额',   width: 120, align: 'right', formatter: fmt2 },
    { prop: 'receive', label: '回款金额',   width: 120, align: 'right', formatter: fmt2 },
    { prop: 'profit',  label: '利润/管理费', width: 120, align: 'right', formatter: fmt2 },
  ],
  async fetch() {
    if (!USE_MOCK) return request.get('/report/04')
    const rows = getAllMockLedgers()
    const monthly = [3, 4, 5, 6, 7, 8].map((m) => ({
      month: `${m}月`,
      supply: 220 + m * 10,
      receive: 160 + m * 8,
      profit: 18 + m * 1.2,
    }))
    monthly.push({
      month: '9月',
      supply:  sum(rows, (r) => r.monthly_supply_amount || 0),
      receive: sum(rows, (r) => r.monthly_supply_actual_collection || 0),
      profit:  sum(rows, (r) => r.profit_management_fee || 0),
    })
    return monthly
  },
}

// ============ 5. 资金收支计划表 ============
const report05: ReportConfig = {
  code: '05', name: '资金收支计划表', group: '核心报表',
  desc: '各集采中心资金计划',
  columns: [
    { prop: 'project_name',      label: '项目',     width: 120 },
    { prop: 'supplier_name',     label: '供应商',   minWidth: 180 },
    { prop: 'material_category', label: '物资',     width: 100 },
    { prop: 'debt_total',        label: '到期应付', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'plan_supply',       label: '计划供应', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'plan_receive',      label: '计划回款', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'plan_pay',          label: '计划支付', width: 110, align: 'right', formatter: fmt2 },
    { prop: 'gap',               label: '收支结余', width: 110, align: 'right',
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

// ============ 6-13 占位 ============
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
  { key: '核心报表',   label: '核心报表' },
  { key: '债务风控',   label: '债务风控' },
  { key: '供应商监控', label: '供应商监控' },
]