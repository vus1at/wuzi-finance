<template>
  <div v-loading="loading">
    <!-- 顶部 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><Tickets /></el-icon>
        <span>债务概况</span>
        <span class="page-sub">上游应付 · {{ rows.length }} 条债务记录</span>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-grid">
      <!-- 1. 总债务 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <span class="kpi-label">总债务余额</span>
          <span class="kpi-link" @click="onMaxSupplierClick">最大供应商 ›</span>
        </div>
        <div class="kpi-value" style="color:#2563eb">¥{{ fmt(kpi.total_debt) }} 万</div>
      </div>

      <!-- 2. 逾期债务 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <span class="kpi-label">逾期债务</span>
          <span class="kpi-link" @click="onMaxOverdueClick">最大逾期 ›</span>
        </div>
        <div class="kpi-value" style="color:#e5484d">¥{{ fmt(kpi.overdue_debt) }} 万</div>
        <div class="kpi-sub dn">逾期率 {{ kpi.overdue_rate }}%</div>
      </div>

      <!-- 3. 高风险债务 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <span class="kpi-label">高风险债务</span>
          <span class="kpi-risk-count">{{ highRiskCount }} 项</span>
        </div>
        <div class="kpi-value" style="color:#e5484d">¥{{ fmt(kpi.high_risk_debt) }} 万</div>
      </div>

      <!-- 4. 涉及供应商 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <span class="kpi-label">涉及供应商</span>
        </div>
        <div class="kpi-value">
          {{ kpi.supplier_count }}<span style="font-size:14px;color:#64748b;margin-left:2px">家</span>
        </div>
      </div>
    </div>

    <!-- 明细表 -->
    <el-card shadow="never" style="margin-top: 12px">
      <template #header>
        <div style="display:flex; align-items:center; justify-content:space-between">
          <b>债务明细</b>
          <span style="font-size:11px; color:#94a3b8">点击供应商/项目 → 穿透查看</span>
        </div>
      </template>

      <el-table
        :data="rows"
        border
        style="width:100%"
        show-summary
        :summary-method="getSummaries"
        :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }"
        :summary-cell-style="{ background: '#f0f7ff', fontWeight: 600, color: '#0f2a4a' }"
      >
        <el-table-column label="供应商" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="link-cell" @click="onSupplierClick(row)">{{ row.supplier_name || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="项目" width="120">
          <template #default="{ row }">
            <span class="link-cell" @click="onProjectClick(row)">{{ row.project_name || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="material_category" label="物资" width="100" />
        <el-table-column label="总债务" width="110" align="right">
          <template #default="{ row }">
            <span class="dn">{{ fmt(row.total_debt) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="逾期" width="110" align="right">
          <template #default="{ row }">
            <span :class="row.overdue_total > 0 ? 'dn' : ''">{{ fmt(row.overdue_total) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="逾期账龄" min-width="240">
          <template #default="{ row }">
            <el-tag v-if="row.overdue_within_3m > 0" size="small" type="warning" style="margin-right:4px">
              &lt;3月 {{ fmt(row.overdue_within_3m) }}
            </el-tag>
            <el-tag v-if="row.overdue_3_6m > 0" size="small" type="warning" style="margin-right:4px">
              3-6月 {{ fmt(row.overdue_3_6m) }}
            </el-tag>
            <el-tag v-if="row.overdue_6_12m > 0" size="small" type="danger" style="margin-right:4px">
              6-12月 {{ fmt(row.overdue_6_12m) }}
            </el-tag>
            <el-tag v-if="row.overdue_over_1y > 0" size="small" type="danger" style="margin-right:4px">
              &gt;1年 {{ fmt(row.overdue_over_1y) }}
            </el-tag>
            <span v-if="row.overdue_total === 0" style="color:#16a34a; font-size:12px">无逾期</span>
          </template>
        </el-table-column>
        <el-table-column label="最长逾期" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.max_overdue_days > 0" type="danger" size="small">{{ row.max_overdue_days }}天</el-tag>
            <span v-else style="color:#94a3b8">—</span>
          </template>
        </el-table-column>
        <el-table-column label="债务分级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="gradeColor(row.debt_grade)" effect="light" size="small">{{ row.debt_grade || '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="风险类别" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.risk_category" type="danger" effect="light" size="small">{{ row.risk_category }}</el-tag>
            <span v-else style="color:#94a3b8">—</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 穿透抽屉 -->
    <el-drawer v-model="drawer.visible" size="780px" :with-header="false">
      <div class="d-header">
        <div class="d-title">
          <el-icon color="#2563eb"><Tickets /></el-icon>
          <b>{{ drawer.title }}</b>
          <span class="d-sub">{{ drawer.subtitle }}</span>
        </div>
        <el-button link @click="drawer.visible = false">
          <el-icon :size="18"><Close /></el-icon>
        </el-button>
      </div>
      <div class="d-body">
        <el-table :data="drawer.rows" border size="small"
          :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }">
          <el-table-column prop="project_name" label="项目" width="110" />
          <el-table-column prop="supplier_name" label="供应商" min-width="180" show-overflow-tooltip />
          <el-table-column prop="material_category" label="物资" width="90" />
          <el-table-column label="总债务" width="100" align="right">
            <template #default="{ row }">
              <span class="dn">{{ fmt(row.total_debt) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="逾期" width="100" align="right">
            <template #default="{ row }">
              <span :class="row.overdue_total > 0 ? 'dn' : ''">{{ fmt(row.overdue_total) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="最长逾期" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.max_overdue_days > 0" type="danger" size="small">{{ row.max_overdue_days }}天</el-tag>
              <span v-else style="color:#94a3b8">—</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="d-footer">
        <el-button @click="drawer.visible = false">关闭</el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Tickets, Close } from '@element-plus/icons-vue'
import { getDebtOverviewApi, type DebtKPI, type DebtRow } from '@/api/debt'

const loading = ref(false)
const kpi = ref<DebtKPI>({
  total_debt: 0, overdue_debt: 0, high_risk_debt: 0,
  supplier_count: 0, overdue_rate: 0,
})
const rows = ref<DebtRow[]>([])

// 高风险债务的条数
const highRiskCount = computed(() => rows.value.filter((r) => r.debt_grade === '高风险').length)

const drawer = reactive({
  visible: false,
  title: '',
  subtitle: '',
  rows: [] as DebtRow[],
})

function fmt(v?: number) {
  if (v === undefined || v === null) return '0.00'
  return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function gradeColor(g?: string) {
  const map: Record<string, string> = {
    高风险: 'danger', 中风险: 'warning', 低风险: 'success',
    战略: 'primary', 既有: 'danger', 保供: 'info',
  }
  return (g && map[g]) || 'info'
}

async function loadData() {
  loading.value = true
  try {
    const data = await getDebtOverviewApi()
    kpi.value = data.kpi
    rows.value = data.rows
  } finally {
    loading.value = false
  }
}

// KPI卡片1：点"最大供应商"，弹总债务最大的供应商
function onMaxSupplierClick() {
  if (rows.value.length === 0) return ElMessage.info('暂无数据')
  const sorted = [...rows.value].sort((a, b) => b.total_debt - a.total_debt)
  const top = sorted[0]
  drawer.title = `最大债务供应商`
  drawer.subtitle = `${top.supplier_name} · ¥${fmt(top.total_debt)} 万`
  drawer.rows = rows.value.filter((r) => r.supplier_id === top.supplier_id)
  drawer.visible = true
}

// KPI卡片2：点"最大逾期"，弹逾期最多的供应商
function onMaxOverdueClick() {
  if (rows.value.length === 0) return ElMessage.info('暂无数据')
  const overdue = rows.value.filter((r) => r.overdue_total > 0)
  if (overdue.length === 0) return ElMessage.info('无逾期债务')
  const sorted = [...overdue].sort((a, b) => b.overdue_total - a.overdue_total)
  const top = sorted[0]
  drawer.title = `最大逾期供应商`
  drawer.subtitle = `${top.supplier_name} · 逾期 ¥${fmt(top.overdue_total)} 万`
  drawer.rows = rows.value.filter((r) => r.supplier_id === top.supplier_id)
  drawer.visible = true
}

function onSupplierClick(row: DebtRow) {
  if (!row.supplier_id) return
  drawer.title = row.supplier_name || '供应商'
  drawer.rows = rows.value.filter((r) => r.supplier_id === row.supplier_id)
  const total = drawer.rows.reduce((s, r) => s + r.total_debt, 0)
  drawer.subtitle = `共 ${drawer.rows.length} 条 · 总债务 ¥${fmt(total)} 万`
  drawer.visible = true
}

function onProjectClick(row: DebtRow) {
  if (!row.project_id) return
  drawer.title = row.project_name || '项目'
  drawer.rows = rows.value.filter((r) => r.project_id === row.project_id)
  const total = drawer.rows.reduce((s, r) => s + r.total_debt, 0)
  drawer.subtitle = `共 ${drawer.rows.length} 条 · 总债务 ¥${fmt(total)} 万`
  drawer.visible = true
}

// 表尾合计
function getSummaries() {
  const total = rows.value.reduce((s, r) => s + r.total_debt, 0)
  const overdue = rows.value.reduce((s, r) => s + r.overdue_total, 0)
  // 按列顺序返回：
  // 供应商 | 项目 | 物资 | 总债务 | 逾期 | 逾期账龄 | 最长逾期 | 债务分级 | 风险类别
  return [
    '合计',
    '',
    '',
    fmt(total),
    fmt(overdue),
    '',
    '',
    '',
    '',
  ]
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #0f2a4a; }
.page-sub { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 4px; }

/* ============ KPI 卡片 ============ */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.kpi-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.15s;
}
.kpi-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* 卡片顶部：左标签 + 右链接 */
.kpi-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.kpi-label {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

/* 点击右侧"最大供应商 ›" */
.kpi-link {
  font-size: 11px;
  color: #2563eb;
  cursor: pointer;
  font-weight: 500;
  transition: color 0.15s;
}
.kpi-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}

/* 高风险"x项" 红色小字 */
.kpi-risk-count {
  font-size: 11px;
  color: #e5484d;
  font-weight: 600;
}

.kpi-value {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.2;
}
.kpi-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 6px;
}
.kpi-sub.dn { color: #e5484d; }

/* ============ 表格 ============ */
.link-cell { color: #2563eb; cursor: pointer; font-weight: 500; }
.link-cell:hover { text-decoration: underline; }
.dn { color: #e5484d; font-weight: 500; }

/* ============ 抽屉 ============ */
.d-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #e5e7eb; }
.d-title { display: flex; align-items: center; gap: 8px; font-size: 15px; }
.d-title b { font-weight: 600; color: #0f2a4a; }
.d-sub { color: #94a3b8; font-size: 12px; font-weight: 400; }
.d-body { padding: 20px; overflow-y: auto; flex: 1; }
.d-footer { padding: 12px 20px; border-top: 1px solid #e5e7eb; display: flex; justify-content: flex-end; }
</style>