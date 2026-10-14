<template>
  <div v-loading="loading">
    <!-- 标题 -->
    <div class="st">
      <el-icon :size="20" color="#2563eb"><Odometer /></el-icon>
      <span class="title">看板统计</span>
      <span class="sub">
        2026年9月 · {{ allLedgers.length }}条台账 · {{ projectAggs.length }}个项目 · {{ supplierAggs.length }}家供应商
      </span>
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-grid">
      <div class="kpi-card" @click="router.push('/input')">
        <div class="kpi-label">本月采购总额</div>
        <div class="kpi-value">¥{{ fmt(kpi.purchase) }} 万</div>
        <div class="kpi-sub up">环比 ↑8.3%</div>
      </div>
      <div class="kpi-card" @click="router.push('/input')">
        <div class="kpi-label">本月供应总额</div>
        <div class="kpi-value">¥{{ fmt(kpi.supply) }} 万</div>
        <div class="kpi-sub up">利润 ¥{{ fmt(kpi.profit) }} 万</div>
      </div>
      <div class="kpi-card" @click="router.push('/debt')">
        <div class="kpi-label">总债务余额</div>
        <div class="kpi-value" style="color:#e5484d">¥{{ fmt(kpi.debt) }} 万</div>
        <div class="kpi-sub dn">逾期率 {{ overdueRate }}%</div>
      </div>
      <div class="kpi-card" @click="router.push('/credit')">
        <div class="kpi-label">应收债权</div>
        <div class="kpi-value" style="color:#2563eb">¥{{ fmt(kpi.receivable) }} 万</div>
        <div class="kpi-sub dn">逾期 {{ receivableOverdueRate }}%</div>
      </div>
      <div class="kpi-card" @click="router.push('/report')">
        <div class="kpi-label">本月回款</div>
        <div class="kpi-value" style="color:#16a34a">¥{{ fmt(kpi.receive) }} 万</div>
        <div class="kpi-sub">回款率 {{ receiveRate }}%</div>
      </div>
    </div>

    <!-- 趋势图 + 饼图 -->
    <div class="row">
      <el-card class="flex3">
        <template #header>
          <el-icon color="#2563eb"><TrendCharts /></el-icon>
          <b>月度趋势</b>
          <span class="hdr-sub">采购/供应/回款(万元)</span>
        </template>
        <div ref="trendRef" style="height: 240px"></div>
      </el-card>
      <el-card class="flex2">
        <template #header>
          <el-icon color="#f59e0b"><PieChart /></el-icon>
          <b>债务分级分布</b>
        </template>
        <div ref="pieRef" style="height: 240px"></div>
      </el-card>
    </div>

    <!-- TOP5 -->
    <div class="row">
      <el-card class="flex1">
        <template #header>
          <el-icon color="#f59e0b"><Trophy /></el-icon>
          <b>项目供应 TOP5</b>
        </template>
        <div
          v-for="(p, i) in topProjects"
          :key="p.id"
          class="rank-item"
          @click="openProjectDrawer(p.id)"
        >
          <span class="rank-badge" :class="i < 3 ? 'blue' : 'gray'">{{ i + 1 }}</span>
          <span class="rank-name">{{ p.name }}</span>
          <span class="rank-mat">{{ p.material }}</span>
          <span class="rank-val">{{ fmt(p.month_supply) }} 万</span>
          <el-icon class="rank-arrow"><ArrowRight /></el-icon>
        </div>
        <div v-if="topProjects.length === 0" class="empty-tip">暂无数据</div>
      </el-card>

      <el-card class="flex1">
        <template #header>
          <el-icon color="#2563eb"><OfficeBuilding /></el-icon>
          <b>供应商债务 TOP5</b>
        </template>
        <div
          v-for="(s, i) in topSuppliers"
          :key="s.id"
          class="rank-item"
          @click="openSupplierDrawer(s.id)"
        >
          <span class="rank-badge" :class="i < 3 ? 'red' : 'orange'">{{ i + 1 }}</span>
          <span class="rank-name">{{ s.name }}</span>
          <span class="rank-mat">{{ s.pct }}%</span>
          <span class="rank-val danger">{{ fmt(s.total_debt) }} 万</span>
          <el-icon class="rank-arrow"><ArrowRight /></el-icon>
        </div>
        <div v-if="topSuppliers.length === 0" class="empty-tip">暂无数据</div>
      </el-card>
    </div>

    <!-- 逾期预警 + 概览 -->
    <div class="row">
      <el-card class="flex1">
        <template #header>
          <el-icon color="#e5484d"><Warning /></el-icon>
          <b>逾期预警</b>
          <span class="hdr-sub">{{ alerts.length }}项逾期</span>
        </template>
        <div
          v-for="(a, i) in alerts"
          :key="i"
          class="rank-item"
          @click="openSupplierDrawer(a.supplier_id)"
        >
          <span class="rank-badge red">逾期</span>
          <span class="rank-name">{{ a.supplier_name }}（{{ a.project_name }}）</span>
          <span class="rank-val danger">{{ fmt(a.amount) }} 万</span>
          <span class="rank-days">{{ a.days }}天</span>
          <el-icon class="rank-arrow"><ArrowRight /></el-icon>
        </div>
        <div v-if="alerts.length === 0" class="empty-tip">✅ 暂无逾期</div>
      </el-card>

      <el-card class="flex1">
        <template #header>
          <el-icon color="#16a34a"><Document /></el-icon>
          <b>本月数据概览</b>
        </template>
        <div class="overview">
          <div class="ov-item"><span>项目数</span><b>{{ projectAggs.length }}</b></div>
          <div class="ov-item"><span>供应商数</span><b>{{ supplierAggs.length }}</b></div>
          <div class="ov-item"><span>区域集采</span><b>¥{{ fmt(regionSupply) }} 万</b></div>
          <div class="ov-item"><span>内供集采</span><b>¥{{ fmt(innerSupply) }} 万</b></div>
          <div class="ov-item">
            <span>高风险债务</span>
            <b style="color:#e5484d">¥{{ fmt(highRiskDebt) }} 万</b>
          </div>
          <div class="ov-item">
            <span>总利润</span>
            <b style="color:#16a34a">¥{{ fmt(kpi.profit) }} 万</b>
          </div>
          <div class="ov-item">
            <span>总逾期债务</span>
            <b style="color:#e5484d">¥{{ fmt(kpi.overdue) }} 万</b>
          </div>
          <div class="ov-item">
            <span>逾期债权</span>
            <b style="color:#e5484d">¥{{ fmt(receivableOverdue) }} 万</b>
          </div>
        </div>
      </el-card>
    </div>

    <!-- ============ 抽屉 ============ -->
    <el-drawer v-model="drawer.visible" size="820px" :with-header="false">
      <!-- 项目详情 -->
      <template v-if="drawer.type === 'project' && currentProject">
        <div class="d-header">
          <div class="d-title">
            <el-icon color="#2563eb"><OfficeBuilding /></el-icon>
            <b>{{ currentProject.name }}</b>
            <span class="d-sub">{{ currentProject.rows.length }}条记录</span>
            <span class="d-link" @click="goToInput(currentProject.name)">→ 查看全部</span>
          </div>
          <el-button link @click="drawer.visible = false">
            <el-icon :size="18"><Close /></el-icon>
          </el-button>
        </div>

        <div class="d-body">
          <!-- 4 个小统计卡 -->
          <div class="d-kpi-grid">
            <div class="d-kpi">
              <div class="d-kpi-l">本月采购</div>
              <div class="d-kpi-v">¥{{ fmt(currentProject.month_purchase) }}</div>
            </div>
            <div class="d-kpi">
              <div class="d-kpi-l">本月供应</div>
              <div class="d-kpi-v">¥{{ fmt(currentProject.month_supply) }}</div>
            </div>
            <div class="d-kpi">
              <div class="d-kpi-l">总债务</div>
              <div class="d-kpi-v" style="color:#e5484d">¥{{ fmt(currentProject.total_debt) }}</div>
            </div>
            <div class="d-kpi">
              <div class="d-kpi-l">应收债权</div>
              <div class="d-kpi-v" style="color:#2563eb">¥{{ fmt(currentProject.receivable) }}</div>
            </div>
          </div>

          <!-- 明细表 -->
          <el-table :data="currentProject.rows" border size="small"
            :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }">
            <el-table-column label="供应商" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="link-cell" @click="openSupplierDrawer(row.supplier_id)">
                  {{ row.supplier_name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="material_category" label="物资" width="100" />
            <el-table-column label="本月采购" width="100" align="right">
              <template #default="{ row }">{{ fmt(row.monthly_purchase_amount) }}</template>
            </el-table-column>
            <el-table-column label="本月供应" width="100" align="right">
              <template #default="{ row }">{{ fmt(row.monthly_supply_amount) }}</template>
            </el-table-column>
            <el-table-column label="债务" width="100" align="right">
              <template #default="{ row }">
                <span class="dn">{{ fmt(row.upstream_debt_total_amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="逾期" width="100" align="center">
              <template #default="{ row }">
                <span v-if="getOverdue(row) > 0" class="tag red">{{ fmt(getOverdue(row)) }}</span>
                <span v-else class="tag green">正常</span>
              </template>
            </el-table-column>
            <el-table-column label="债务分级" width="90">
              <template #default="{ row }">
                <span :class="['tag', gradeCls(row.debt_grade)]">{{ row.debt_grade }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="d-footer">
          <el-button @click="drawer.visible = false">关闭</el-button>
        </div>
      </template>

      <!-- 供应商详情 -->
      <template v-else-if="drawer.type === 'supplier' && currentSupplier">
        <div class="d-header">
          <div class="d-title">
            <el-icon color="#2563eb"><OfficeBuilding /></el-icon>
            <b>{{ currentSupplier.name }}</b>
          </div>
          <el-button link @click="drawer.visible = false">
            <el-icon :size="18"><Close /></el-icon>
          </el-button>
        </div>

        <div class="d-body">
          <!-- 6 字段 -->
          <div class="d-grid-3">
            <div class="d-cell">
              <div class="d-k">债务分级</div>
              <div class="d-v">
                <span :class="['tag', gradeCls(currentSupplier.debt_grade)]">
                  {{ currentSupplier.debt_grade || '—' }}
                </span>
              </div>
            </div>
            <div class="d-cell">
              <div class="d-k">总债务</div>
              <div class="d-v" style="color:#e5484d">¥{{ fmt(currentSupplier.total_debt) }}</div>
            </div>
            <div class="d-cell">
              <div class="d-k">逾期</div>
              <div class="d-v" style="color:#e5484d">¥{{ fmt(currentSupplier.overdue) }}</div>
            </div>
            <div class="d-cell">
              <div class="d-k">涉及项目</div>
              <div class="d-v">{{ currentSupplier.project_names.join('、') }}</div>
            </div>
            <div class="d-cell">
              <div class="d-k">物资</div>
              <div class="d-v">{{ currentSupplier.materials.join('、') }}</div>
            </div>
            <div class="d-cell">
              <div class="d-k">风险类别</div>
              <div class="d-v">
                <span v-if="currentSupplier.risk" class="tag red">{{ currentSupplier.risk }}</span>
                <span v-else>—</span>
              </div>
            </div>
          </div>

          <!-- 明细表 -->
          <el-table :data="currentSupplier.rows" border size="small"
            :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }">
            <el-table-column label="项目" width="120">
              <template #default="{ row }">
                <span class="link-cell" @click="openProjectDrawer(row.project_id)">
                  {{ row.project_name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="material_category" label="物资" width="100" />
            <el-table-column label="采购" width="90" align="right">
              <template #default="{ row }">{{ fmt(row.monthly_purchase_amount) }}</template>
            </el-table-column>
            <el-table-column label="供应" width="90" align="right">
              <template #default="{ row }">{{ fmt(row.monthly_supply_amount) }}</template>
            </el-table-column>
            <el-table-column label="债务" width="100" align="right">
              <template #default="{ row }">
                <span class="dn">{{ fmt(row.upstream_debt_total_amount) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="逾期" width="100" align="right">
              <template #default="{ row }">
                <span :class="getOverdue(row) > 0 ? 'dn' : ''">{{ fmt(getOverdue(row)) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="逾期天数" width="100" align="center">
              <template #default="{ row }">
                <span v-if="(row.upstream_debt_max_overdue_days || 0) > 0" class="tag red">
                  {{ row.upstream_debt_max_overdue_days }}天
                </span>
                <span v-else class="tag green">正常</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="d-footer">
          <el-button @click="drawer.visible = false">关闭</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Odometer, TrendCharts, PieChart, Trophy, OfficeBuilding,
  Warning, Document, ArrowRight, Close,
} from '@element-plus/icons-vue'
import { getAllMockLedgers, type Ledger } from '@/api/ledger'

const router = useRouter()
const trendRef = ref<HTMLElement>()
const pieRef = ref<HTMLElement>()
const loading = ref(true)

// ============ 原始数据 ============
const allLedgers = ref<Ledger[]>([])

function sum<T>(arr: T[], f: (x: T) => number) {
  return arr.reduce((s, x) => s + (f(x) || 0), 0)
}

function getOverdue(r: Ledger) {
  return (r.upstream_debt_overdue_within_3m || 0)
       + (r.upstream_debt_overdue_3_6m || 0)
       + (r.upstream_debt_overdue_6_12m || 0)
       + (r.upstream_debt_overdue_over_1y || 0)
}

function fmt(v?: number) {
  if (v === undefined || v === null) return '0.00'
  return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// ============ KPI 聚合 ============
const kpi = computed(() => {
  const rows = allLedgers.value
  return {
    purchase: sum(rows, (r) => r.monthly_purchase_amount || 0),
    supply: sum(rows, (r) => r.monthly_supply_amount || 0),
    profit: sum(rows, (r) => r.profit_management_fee || 0),
    debt: sum(rows, (r) => r.upstream_debt_total_amount || 0),
    overdue: sum(rows, getOverdue),
    receivable: sum(rows, (r) => r.downstream_receivable_amount || 0),
    receive: sum(rows, (r) => r.monthly_supply_actual_collection || 0),
  }
})

const overdueRate = computed(() =>
  kpi.value.debt > 0 ? ((kpi.value.overdue / kpi.value.debt) * 100).toFixed(2) : '0.00',
)
const receivableOverdue = computed(() =>
  sum(allLedgers.value, (r) => r.downstream_overdue_receivable_total || 0),
)
const receivableOverdueRate = computed(() =>
  kpi.value.receivable > 0
    ? ((receivableOverdue.value / kpi.value.receivable) * 100).toFixed(2)
    : '0.00',
)
const receiveRate = computed(() =>
  kpi.value.supply > 0 ? ((kpi.value.receive / kpi.value.supply) * 100).toFixed(2) : '0.00',
)

const highRiskDebt = computed(() =>
  sum(
    allLedgers.value.filter((r) => r.debt_grade === '高风险'),
    (r) => r.upstream_debt_total_amount || 0,
  ),
)
const regionSupply = computed(() =>
  sum(
    allLedgers.value.filter((r) => r.supply_category === '区域集采'),
    (r) => r.monthly_supply_amount || 0,
  ),
)
const innerSupply = computed(() =>
  sum(
    allLedgers.value.filter((r) => r.supply_category === '内供集采'),
    (r) => r.monthly_supply_amount || 0,
  ),
)

// ============ 按项目聚合 ============
interface ProjectAgg {
  id: number
  name: string
  material: string
  month_purchase: number
  month_supply: number
  total_debt: number
  receivable: number
  rows: Ledger[]
}

const projectAggs = computed<ProjectAgg[]>(() => {
  const map = new Map<number, ProjectAgg>()
  for (const r of allLedgers.value) {
    if (!r.project_id) continue
    const exist = map.get(r.project_id)
    if (exist) {
      exist.month_purchase += r.monthly_purchase_amount || 0
      exist.month_supply += r.monthly_supply_amount || 0
      exist.total_debt += r.upstream_debt_total_amount || 0
      exist.receivable += r.downstream_receivable_amount || 0
      exist.rows.push(r)
    } else {
      map.set(r.project_id, {
        id: r.project_id,
        name: r.project_name || '未知项目',
        material: r.material_category || '',
        month_purchase: r.monthly_purchase_amount || 0,
        month_supply: r.monthly_supply_amount || 0,
        total_debt: r.upstream_debt_total_amount || 0,
        receivable: r.downstream_receivable_amount || 0,
        rows: [r],
      })
    }
  }
  return Array.from(map.values())
})

// ============ 按供应商聚合 ============
interface SupplierAgg {
  id: number
  name: string
  total_debt: number
  overdue: number
  project_names: string[]
  materials: string[]
  debt_grade: string
  risk: string
  rows: Ledger[]
}

const supplierAggs = computed<SupplierAgg[]>(() => {
  const map = new Map<number, SupplierAgg>()
  for (const r of allLedgers.value) {
    if (!r.supplier_id) continue
    const exist = map.get(r.supplier_id)
    const overdue = getOverdue(r)
    if (exist) {
      exist.total_debt += r.upstream_debt_total_amount || 0
      exist.overdue += overdue
      if (r.project_name && !exist.project_names.includes(r.project_name)) {
        exist.project_names.push(r.project_name)
      }
      if (r.material_category && !exist.materials.includes(r.material_category)) {
        exist.materials.push(r.material_category)
      }
      exist.rows.push(r)
    } else {
      map.set(r.supplier_id, {
        id: r.supplier_id,
        name: r.supplier_name || '未知供应商',
        total_debt: r.upstream_debt_total_amount || 0,
        overdue,
        project_names: r.project_name ? [r.project_name] : [],
        materials: r.material_category ? [r.material_category] : [],
        debt_grade: r.debt_grade || '',
        risk: r.existing_risk_category || '',
        rows: [r],
      })
    }
  }
  return Array.from(map.values())
})

// ============ TOP5 / 预警 ============
const topProjects = computed(() =>
  [...projectAggs.value].sort((a, b) => b.month_supply - a.month_supply).slice(0, 5),
)

const topSuppliers = computed(() => {
  const sorted = [...supplierAggs.value].sort((a, b) => b.total_debt - a.total_debt).slice(0, 5)
  return sorted.map((s) => ({
    ...s,
    pct: kpi.value.debt > 0 ? ((s.total_debt / kpi.value.debt) * 100).toFixed(1) : '0',
  }))
})

const alerts = computed(() => {
  const list: {
    supplier_id: number
    supplier_name: string
    project_name: string
    amount: number
    days: number
  }[] = []
  for (const r of allLedgers.value) {
    const ov = getOverdue(r)
    if (ov > 0) {
      list.push({
        supplier_id: r.supplier_id || 0,
        supplier_name: r.supplier_name || '',
        project_name: r.project_name || '',
        amount: ov,
        days: r.upstream_debt_max_overdue_days || 0,
      })
    }
  }
  return list.sort((a, b) => b.amount - a.amount)
})

// ============ 抽屉 ============
const drawer = reactive({
  visible: false,
  type: 'project' as 'project' | 'supplier',
  id: 0,
})

const currentProject = computed(() =>
  drawer.type === 'project' ? projectAggs.value.find((p) => p.id === drawer.id) : null,
)

const currentSupplier = computed(() =>
  drawer.type === 'supplier' ? supplierAggs.value.find((s) => s.id === drawer.id) : null,
)

function openProjectDrawer(projectId?: number | null) {
  if (!projectId) return
  drawer.type = 'project'
  drawer.id = projectId
  drawer.visible = true
}

function openSupplierDrawer(supplierId?: number | null) {
  if (!supplierId) return
  drawer.type = 'supplier'
  drawer.id = supplierId
  drawer.visible = true
}

// ⭐ "查看全部" → 跳数据填报，带上项目名作为筛选
function goToInput(projectName: string) {
  drawer.visible = false
  router.push({ path: '/input', query: { project: projectName } })
}

function gradeCls(level?: string) {
  return {
    高风险: 'red',
    中风险: 'orange',
    低风险: 'green',
    战略: 'purple',
  }[level || ''] || 'gray'
}

// ============ 图表 ============
function renderCharts() {
  if (trendRef.value) {
    const c = echarts.init(trendRef.value)
    c.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['采购', '供应', '回款'], bottom: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
      grid: { left: 40, right: 16, top: 16, bottom: 36 },
      xAxis: { type: 'category', data: ['3月', '4月', '5月', '6月', '7月', '8月', '9月'], axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f2f4' } }, axisLabel: { fontSize: 11 } },
      series: [
        { name: '采购', type: 'bar', data: [240, 310, 280, 340, 320, 380, kpi.value.purchase], barWidth: 14, itemStyle: { color: '#2563eb', borderRadius: [4, 4, 0, 0] } },
        { name: '供应', type: 'bar', data: [220, 290, 265, 320, 300, 350, kpi.value.supply], barWidth: 14, itemStyle: { color: '#93c5fd', borderRadius: [4, 4, 0, 0] } },
        { name: '回款', type: 'line', data: [160, 200, 210, 230, 240, 260, kpi.value.receive], smooth: true, lineStyle: { color: '#16a34a' }, itemStyle: { color: '#16a34a' } },
      ],
    })
  }

  if (pieRef.value) {
    const gradeMap: Record<string, number> = {}
    for (const r of allLedgers.value) {
      const g = r.debt_grade || '未分级'
      gradeMap[g] = (gradeMap[g] || 0) + (r.upstream_debt_total_amount || 0)
    }
    const colors: Record<string, string> = {
      高风险: '#dc2626', 中风险: '#d97706', 低风险: '#10b981',
      战略: '#6d28d9', 保供: '#2563eb', 既有: '#ef4444',
    }
    const c = echarts.init(pieRef.value)
    c.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: ¥{c}万 ({d}%)' },
      legend: { orient: 'vertical', right: 8, top: 'center', itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
      series: [{
        name: '债务分布', type: 'pie', radius: ['40%', '65%'], center: ['38%', '50%'], label: { show: false },
        data: Object.entries(gradeMap).map(([name, value]) => ({
          value: Number(value.toFixed(2)),
          name,
          itemStyle: { color: colors[name] || '#6b7280' },
        })),
      }],
    })
  }
}

onMounted(async () => {
  allLedgers.value = getAllMockLedgers()
  loading.value = false
  await nextTick()
  renderCharts()
})
</script>

<style scoped>
.st { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
.title { font-size: 16px; font-weight: 700; color: #0f2a4a; }
.sub { font-size: 12px; color: #94a3b8; margin-left: 4px; }

.kpi-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 14px; }
.kpi-card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px;
  cursor: pointer; transition: all 0.15s;
}
.kpi-card:hover { border-color: #2563eb; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.12); transform: translateY(-1px); }
.kpi-label { font-size: 12px; color: #94a3b8; margin-bottom: 8px; font-weight: 500; }
.kpi-value { font-size: 22px; font-weight: 700; letter-spacing: -0.3px; color: #1e293b; }
.kpi-sub { font-size: 11px; margin-top: 6px; color: #64748b; font-weight: 500; }
.kpi-sub.up { color: #16a34a; }
.kpi-sub.dn { color: #e5484d; }

.row { display: flex; gap: 12px; margin-bottom: 12px; }
.flex1 { flex: 1; }
.flex2 { flex: 2; }
.flex3 { flex: 3; }

.hdr-sub { font-size: 11px; color: #94a3b8; margin-left: 8px; font-weight: 500; }

:deep(.el-card__header) { padding: 12px 16px; display: flex; align-items: center; gap: 6px; }
:deep(.el-card__header b) { font-weight: 600; font-size: 14px; color: #0f2a4a; }

.rank-item {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 8px; margin: 0 -8px;
  border-bottom: 1px solid #f1f2f4;
  font-size: 13px; font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.15s;
}
.rank-item:last-child { border-bottom: none; }
.rank-item:hover { background: #eff6ff; }
.rank-arrow { color: #cbd5e1; opacity: 0; transition: opacity 0.15s; font-size: 14px; }
.rank-item:hover .rank-arrow { opacity: 1; color: #2563eb; }

.rank-badge {
  min-width: 20px; height: 20px; padding: 0 6px;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 10px; font-size: 11px; font-weight: 600;
  flex-shrink: 0;
}
.rank-badge.blue { background: #dbeafe; color: #2563eb; }
.rank-badge.gray { background: #f3f4f6; color: #6b7280; }
.rank-badge.red { background: #fee2e2; color: #dc2626; }
.rank-badge.orange { background: #fef3c7; color: #b45309; }

.rank-name { flex: 1; color: #1e293b; }
.rank-mat { color: #94a3b8; font-size: 11px; margin-right: 8px; font-weight: 500; }
.rank-val { font-weight: 600; color: #1e293b; }
.rank-val.danger { color: #e5484d; }
.rank-days { font-size: 11px; color: #94a3b8; margin-left: 6px; font-weight: 500; }

.empty-tip { text-align: center; color: #94a3b8; padding: 20px 0; font-size: 12px; }

.overview { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 20px; }
.ov-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f2f4; font-size: 12px; }
.ov-item span { color: #94a3b8; font-weight: 500; }
.ov-item b { font-weight: 600; }

/* ============ 抽屉 ============ */
.d-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}
.d-title { display: flex; align-items: center; gap: 8px; font-size: 15px; }
.d-title b { font-weight: 600; color: #0f2a4a; }
.d-sub { color: #94a3b8; font-size: 12px; font-weight: 400; margin-left: 4px; }
.d-link { color: #2563eb; cursor: pointer; font-size: 12px; margin-left: 8px; font-weight: 500; }
.d-link:hover { text-decoration: underline; }

.d-body { padding: 20px; overflow-y: auto; flex: 1; }

.d-kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.d-kpi { background: #f9fafb; border-radius: 8px; padding: 14px; text-align: center; }
.d-kpi-l { font-size: 12px; color: #94a3b8; margin-bottom: 6px; font-weight: 500; }
.d-kpi-v { font-size: 18px; font-weight: 700; }

.d-grid-3 {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 1px; background: #e5e7eb; border: 1px solid #e5e7eb;
  border-radius: 6px; overflow: hidden; margin-bottom: 16px;
}
.d-cell { background: #fff; padding: 12px 14px; }
.d-k { font-size: 12px; color: #94a3b8; margin-bottom: 6px; font-weight: 500; }
.d-v { font-size: 14px; font-weight: 500; }

.d-footer { padding: 12px 20px; border-top: 1px solid #e5e7eb; display: flex; justify-content: flex-end; }

.link-cell { color: #2563eb; cursor: pointer; font-weight: 500; }
.link-cell:hover { text-decoration: underline; }
.dn { color: #e5484d; font-weight: 500; }

.tag { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.tag.red { background: #fee2e2; color: #dc2626; }
.tag.orange { background: #fef3c7; color: #b45309; }
.tag.green { background: #d1fae5; color: #059669; }
.tag.purple { background: #ede9fe; color: #6d28d9; }
.tag.gray { background: #f3f4f6; color: #6b7280; }
</style>