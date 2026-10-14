/**
 * 数据填报 - 台账接口
 * mock 数据用 localStorage 持久化（刷新不丢）
 */
import request from '@/utils/request'

const USE_MOCK = true
const STORAGE_KEY = 'wuzi_ledger_mock'

export interface Ledger {
  id: number
  period: string
  contract_entity?: string
  management_type?: string
  supply_category?: string
  project_id?: number | null
  project_name?: string
  project_category?: string
  project_status?: string
  subsidiary_id?: number | null
  subsidiary_name?: string
  project_address?: string
  supplier_id?: number | null
  supplier_name?: string
  procurement_method?: string
  is_manufacturer?: number | null
  material_category?: string
  payment_mode?: string
  debt_grade?: string
  existing_risk_category?: string
  installment_plan_total?: number
  installment_plan_current_month?: number
  installment_plan_next_month?: number
  monthly_purchase_quantity?: number
  monthly_purchase_amount?: number
  monthly_purchase_confirmed_overdue_fee?: number
  monthly_purchase_confirmed_interest_subsidy_fee?: number
  monthly_purchase_total?: number
  monthly_purchase_actual_payment?: number
  next_month_payment_plan?: number
  monthly_supply_quantity?: number
  monthly_supply_amount?: number
  monthly_supply_prepayment_amount?: number
  monthly_supply_confirmed_overdue_fee?: number
  monthly_supply_confirmed_interest_subsidy_fee?: number
  monthly_supply_total?: number
  monthly_supply_actual_collection?: number
  profit_management_fee?: number
  next_month_supply_plan?: number
  next_month_collection_plan?: number
  upstream_debt_prepayment_balance?: number
  upstream_debt_total_amount?: number
  upstream_debt_due_payable?: number
  upstream_debt_expected_total?: number
  upstream_debt_overdue_within_3m?: number
  upstream_debt_overdue_3_6m?: number
  upstream_debt_overdue_6_12m?: number
  upstream_debt_overdue_over_1y?: number
  upstream_debt_max_overdue_days?: number
  downstream_receivable_prepayment_balance?: number
  downstream_receivable_amount?: number
  downstream_overdue_receivable_total?: number
  downstream_overdue_receivable_within_3m?: number
  downstream_overdue_receivable_3_6m?: number
  downstream_overdue_receivable_6_12m?: number
  downstream_overdue_receivable_over_1y?: number
  downstream_max_overdue_days?: number
  yearly_supply_quantity?: number
  yearly_supply_amount?: number
  yearly_supply_prepayment_amount?: number
  yearly_supply_confirmed_overdue_fee?: number
  yearly_supply_confirmed_interest_subsidy_fee?: number
  yearly_supply_total?: number
  yearly_supply_actual_collection?: number
  yearly_profit_management_fee?: number
  yearly_purchase_amount?: number
  yearly_payment_amount?: number
  yearly_payment_ratio?: number
  yearly_summary_supply_amount?: number
  yearly_remittance_amount?: number
  yearly_remittance_ratio?: number
  document_date?: string
  created_at?: string
  updated_at?: string
}

const DEFAULT_MOCK_ROWS: Ledger[] = [
  {
    id: 1, period: '2026-09',
    contract_entity: '物资分公司', management_type: 'A类材料厂', supply_category: '内供集采',
    project_id: 1, project_name: '大瑞1', project_category: '铁路', project_status: '在供',
    subsidiary_id: 1, subsidiary_name: '一处', project_address: '云南大理',
    supplier_id: 1, supplier_name: '泰安现代塑料有限公司',
    procurement_method: '公开招标', is_manufacturer: 1, material_category: '土工材料',
    payment_mode: '第四月付第一月80%', debt_grade: '高风险', existing_risk_category: '两拖欠',
    monthly_purchase_quantity: 1, monthly_purchase_amount: 33, monthly_purchase_total: 33,
    monthly_purchase_actual_payment: 0,
    monthly_supply_quantity: 1, monthly_supply_amount: 34, monthly_supply_total: 34,
    monthly_supply_actual_collection: 0, profit_management_fee: 20,
    upstream_debt_total_amount: 46.28, upstream_debt_max_overdue_days: 187,
    downstream_receivable_amount: 0, downstream_overdue_receivable_total: 0,
  },
  {
    id: 2, period: '2026-09',
    contract_entity: '物资分公司', management_type: 'A类材料厂', supply_category: '内供集采',
    project_id: 1, project_name: '大瑞1', project_category: '铁路', project_status: '在供',
    subsidiary_id: 1, subsidiary_name: '一处', project_address: '云南大理',
    supplier_id: 1, supplier_name: '泰安现代塑料有限公司',
    procurement_method: '公开招标', is_manufacturer: 1, material_category: '木材',
    payment_mode: '第四月付第一月80%', debt_grade: '高风险', existing_risk_category: '两拖欠',
    monthly_purchase_quantity: 2, monthly_purchase_amount: 33, monthly_purchase_total: 33,
    monthly_purchase_actual_payment: 0,
    monthly_supply_quantity: 2, monthly_supply_amount: 34, monthly_supply_total: 34,
    monthly_supply_actual_collection: 0, profit_management_fee: 0,
    upstream_debt_total_amount: 88.49,
    upstream_debt_overdue_6_12m: 88.49, upstream_debt_max_overdue_days: 187,
    downstream_receivable_amount: 0, downstream_overdue_receivable_total: 0,
  },
  {
    id: 3, period: '2026-09',
    contract_entity: '物资分公司', management_type: 'A类材料厂', supply_category: '内供集采',
    project_id: 2, project_name: '大瑞3', project_category: '铁路', project_status: '在供',
    subsidiary_id: 1, subsidiary_name: '一处', project_address: '云南大理',
    supplier_id: 1, supplier_name: '泰安现代塑料有限公司',
    procurement_method: '公开谈判', is_manufacturer: 1, material_category: '波纹管',
    payment_mode: '第四月付第一月80%', debt_grade: '中风险',
    monthly_purchase_quantity: 4, monthly_purchase_amount: 33, monthly_purchase_total: 33,
    monthly_purchase_actual_payment: 0,
    monthly_supply_quantity: 4, monthly_supply_amount: 34, monthly_supply_total: 34,
    monthly_supply_actual_collection: 0, profit_management_fee: 0,
    upstream_debt_total_amount: 5.74, upstream_debt_max_overdue_days: 62,
    downstream_receivable_amount: 0, downstream_overdue_receivable_total: 0,
  },
  {
    id: 4, period: '2026-09',
    contract_entity: '物资分公司', management_type: 'A类材料厂', supply_category: '内供集采',
    project_id: 3, project_name: '大瑞4', project_category: '铁路', project_status: '在供',
    subsidiary_id: 1, subsidiary_name: '一处', project_address: '云南大理',
    supplier_id: 1, supplier_name: '泰安现代塑料有限公司',
    procurement_method: '公开招标', is_manufacturer: 1, material_category: '槽道',
    payment_mode: '第四月付第一月80%', debt_grade: '中风险',
    monthly_purchase_quantity: 5, monthly_purchase_amount: 33, monthly_purchase_total: 33,
    monthly_purchase_actual_payment: 0,
    monthly_supply_quantity: 5, monthly_supply_amount: 34, monthly_supply_total: 34,
    monthly_supply_actual_collection: 0, profit_management_fee: 0,
    upstream_debt_total_amount: 28.65, upstream_debt_max_overdue_days: 95,
    downstream_receivable_amount: 0, downstream_overdue_receivable_total: 0,
  },
  {
    id: 5, period: '2026-09',
    contract_entity: '物资分公司', management_type: '集采中心', supply_category: '区域集采',
    project_id: 4, project_name: '成达万', project_category: '铁路', project_status: '在供',
    subsidiary_id: 1, subsidiary_name: '一处', project_address: '四川成都',
    supplier_id: 2, supplier_name: '物产中大金属集团有限公司',
    procurement_method: '战略采购', is_manufacturer: 1, material_category: '型材',
    payment_mode: '月结80%', debt_grade: '战略',
    monthly_purchase_quantity: 460, monthly_purchase_amount: 180, monthly_purchase_total: 180,
    monthly_purchase_actual_payment: 80,
    monthly_supply_quantity: 420, monthly_supply_amount: 168, monthly_supply_total: 168,
    monthly_supply_actual_collection: 0, profit_management_fee: 18,
    upstream_debt_total_amount: 168, upstream_debt_max_overdue_days: 0,
    downstream_receivable_amount: 96, downstream_overdue_receivable_total: 0,
  },
  {
    id: 6, period: '2026-09',
    contract_entity: '物资分公司', management_type: '集采中心', supply_category: '区域集采',
    project_id: 9, project_name: '中吉乌', project_category: '铁路', project_status: '在供',
    subsidiary_id: 5, subsidiary_name: '五处', project_address: '新疆喀什',
    supplier_id: 4, supplier_name: '海螺水泥股份有限公司',
    procurement_method: '战略采购', is_manufacturer: 1, material_category: '水泥',
    payment_mode: '月结80%', debt_grade: '战略',
    monthly_purchase_quantity: 3200, monthly_purchase_amount: 96, monthly_purchase_total: 96,
    monthly_purchase_actual_payment: 90,
    monthly_supply_quantity: 3000, monthly_supply_amount: 90, monthly_supply_total: 90,
    monthly_supply_actual_collection: 0, profit_management_fee: 9,
    upstream_debt_total_amount: 90, upstream_debt_max_overdue_days: 0,
    downstream_receivable_amount: 88, downstream_overdue_receivable_total: 0,
  },
  {
    id: 7, period: '2026-09',
    contract_entity: '物资分公司', management_type: 'A类材料厂', supply_category: '内供集采',
    project_id: 5, project_name: '宜兴', project_category: '市政', project_status: '在供',
    subsidiary_id: 2, subsidiary_name: '二处', project_address: '江苏宜兴',
    supplier_id: 7, supplier_name: '四川金阳外加剂有限公司',
    procurement_method: '公开招标', is_manufacturer: 1, material_category: '外加剂',
    payment_mode: '月结70%', debt_grade: '中风险',
    monthly_purchase_quantity: 200, monthly_purchase_amount: 18.6, monthly_purchase_total: 18.6,
    monthly_purchase_actual_payment: 0,
    monthly_supply_quantity: 180, monthly_supply_amount: 17.5, monthly_supply_total: 17.5,
    monthly_supply_actual_collection: 0, profit_management_fee: 2,
    upstream_debt_total_amount: 18.6, upstream_debt_max_overdue_days: 0,
    downstream_receivable_amount: 72, downstream_overdue_receivable_total: 0,
  },
  {
    id: 8, period: '2026-09',
    contract_entity: '物资分公司', management_type: '集采中心', supply_category: '区域集采',
    project_id: 7, project_name: '侨城东路', project_category: '市政', project_status: '在供',
    subsidiary_id: 4, subsidiary_name: '四处', project_address: '广东深圳',
    supplier_id: 5, supplier_name: '云南建投混凝土公司',
    procurement_method: '框架采购', is_manufacturer: 1, material_category: '商砼',
    payment_mode: '按月结算', debt_grade: '低风险',
    monthly_purchase_quantity: 900, monthly_purchase_amount: 45, monthly_purchase_total: 45,
    monthly_purchase_actual_payment: 22,
    monthly_supply_quantity: 850, monthly_supply_amount: 42, monthly_supply_total: 42,
    monthly_supply_actual_collection: 0, profit_management_fee: 4.5,
    upstream_debt_total_amount: 42,
    upstream_debt_overdue_within_3m: 8, upstream_debt_overdue_3_6m: 4,
    upstream_debt_max_overdue_days: 45,
    downstream_receivable_amount: 58,
    downstream_overdue_receivable_total: 12,
    downstream_overdue_receivable_within_3m: 8, downstream_overdue_receivable_3_6m: 4,
    downstream_max_overdue_days: 45,
  },
  {
    id: 9, period: '2026-09',
    contract_entity: '物资分公司', management_type: '集采中心', supply_category: '区域集采',
    project_id: 6, project_name: '西十2标', project_category: '铁路', project_status: '在供',
    subsidiary_id: 3, subsidiary_name: '三处', project_address: '陕西西安',
    supplier_id: 6, supplier_name: '陕西钢铁集团有限公司',
    procurement_method: '框架采购', is_manufacturer: 1, material_category: '钢绞线',
    payment_mode: '季度结算', debt_grade: '低风险',
    monthly_purchase_quantity: 150, monthly_purchase_amount: 72.4, monthly_purchase_total: 72.4,
    monthly_purchase_actual_payment: 0,
    monthly_supply_quantity: 130, monthly_supply_amount: 66, monthly_supply_total: 66,
    monthly_supply_actual_collection: 0, profit_management_fee: 7,
    upstream_debt_total_amount: 66, upstream_debt_max_overdue_days: 0,
    downstream_receivable_amount: 95, downstream_overdue_receivable_total: 0,
  },
  {
    id: 10, period: '2026-09',
    contract_entity: '物资分公司', management_type: 'A类材料厂', supply_category: '内供集采',
    project_id: 8, project_name: '西丽', project_category: '市政', project_status: '在供',
    subsidiary_id: 4, subsidiary_name: '四处', project_address: '广东深圳',
    supplier_id: 1, supplier_name: '泰安现代塑料有限公司',
    procurement_method: '公开招标', is_manufacturer: 1, material_category: '土工材料',
    payment_mode: '第四月付第一月80%', debt_grade: '高风险', existing_risk_category: '诉讼',
    monthly_purchase_quantity: 600, monthly_purchase_amount: 28, monthly_purchase_total: 28,
    monthly_purchase_actual_payment: 0,
    monthly_supply_quantity: 550, monthly_supply_amount: 26, monthly_supply_total: 26,
    monthly_supply_actual_collection: 0, profit_management_fee: 0,
    upstream_debt_total_amount: 28,
    upstream_debt_overdue_6_12m: 28, upstream_debt_max_overdue_days: 120,
    downstream_receivable_amount: 120,
    downstream_overdue_receivable_total: 35,
    downstream_overdue_receivable_6_12m: 35, downstream_max_overdue_days: 120,
  },
]

function loadMock(): Ledger[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      // ⭐ 兼容：如果本地只存了旧版 3 条，直接用新的 10 条覆盖
      if (Array.isArray(parsed) && parsed.length >= 10) return parsed
    }
  } catch { /* ignore */ }
  return JSON.parse(JSON.stringify(DEFAULT_MOCK_ROWS))
}

function saveMock(rows: Ledger[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(rows))
  } catch { /* ignore */ }
}

let MOCK_ROWS: Ledger[] = loadMock()
// ⭐ 首次或旧数据 < 10 条时，保存新版覆盖
saveMock(MOCK_ROWS)

function mockFilter(params?: any) {
  let rows = [...MOCK_ROWS]
  if (params?.period) {
    rows = rows.filter((r) => r.period === params.period)
  }
  if (params?.management_type) {
    rows = rows.filter((r) => r.management_type === params.management_type)
  }
  if (params?.supplier_id) {
    rows = rows.filter((r) => r.supplier_id === params.supplier_id)
  }
  if (params?.project_id) {
    rows = rows.filter((r) => r.project_id === params.project_id)
  }
  return rows.sort((a, b) => a.id - b.id)
}

export const listLedgerApi = async (params?: {
  period?: string
  project_id?: number
  supplier_id?: number
  management_type?: string
}): Promise<Ledger[]> => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 200))
    return mockFilter(params)
  }
  return request.get<any, Ledger[]>('/ledger', { params })
}

export const getLedgerApi = async (id: number): Promise<Ledger> => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 100))
    const row = MOCK_ROWS.find((r) => r.id === id)
    if (!row) throw new Error('not found')
    return row
  }
  return request.get<any, Ledger>(`/ledger/${id}`)
}

export const createLedgerApi = async (data: Partial<Ledger>): Promise<Ledger> => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 200))
    const newId = Math.max(0, ...MOCK_ROWS.map((r) => r.id)) + 1
    const row = { id: newId, period: '2026-09', ...data } as Ledger
    MOCK_ROWS.push(row)
    saveMock(MOCK_ROWS)
    return row
  }
  return request.post<any, Ledger>('/ledger', data)
}

export const updateLedgerApi = async (id: number, data: Partial<Ledger>): Promise<Ledger> => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 200))
    const idx = MOCK_ROWS.findIndex((r) => r.id === id)
    if (idx < 0) throw new Error('not found')
    MOCK_ROWS[idx] = { ...MOCK_ROWS[idx], ...data }
    saveMock(MOCK_ROWS)
    return MOCK_ROWS[idx]
  }
  return request.put<any, Ledger>(`/ledger/${id}`, data)
}

export const deleteLedgerApi = async (id: number): Promise<void> => {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 200))
    MOCK_ROWS = MOCK_ROWS.filter((r) => r.id !== id)
    saveMock(MOCK_ROWS)
    return
  }
  await request.delete(`/ledger/${id}`)
}

// 供其他模块复用
export const getAllMockLedgers = (): Ledger[] => {
  if (USE_MOCK) return [...MOCK_ROWS]
  return []
}

// 调试：清空 mock，恢复 10 条初始数据
export const resetLedgerMock = () => {
  MOCK_ROWS = JSON.parse(JSON.stringify(DEFAULT_MOCK_ROWS))
  saveMock(MOCK_ROWS)
}