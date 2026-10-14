<template>
  <div v-loading="loading">
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><ScaleToOriginal /></el-icon>
        <span>债权概况</span>
        <span class="page-sub">下游应收 · {{ rows.length }} 个项目有债权</span>
      </div>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card" @click="onKpiClick('receivable')">
        <div class="kpi-label">应收债权</div>
        <div class="kpi-value" style="color:#2563eb">¥{{ fmt(kpi.receivable) }} 万</div>
        <div class="kpi-sub">涉及 {{ rows.filter(r => r.receivable > 0).length }} 个项目</div>
      </div>
      <div class="kpi-card" @click="onKpiClick('overdue')">
        <div class="kpi-label">逾期债权</div>
        <div class="kpi-value" style="color:#e5484d">¥{{ fmt(kpi.overdue_receivable) }} 万</div>
        <div class="kpi-sub dn">
          {{ kpi.receivable > 0 ? ((kpi.overdue_receivable / kpi.receivable) * 100).toFixed(2) : 0 }}% 逾期
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">开累供应</div>
        <div class="kpi-value">¥{{ fmt(kpi.cum_supply) }} 万</div>
        <div class="kpi-sub">全部历史累计</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">回款率</div>
        <div class="kpi-value" style="color:#16a34a">{{ kpi.receive_rate }}%</div>
        <div class="kpi-sub">已回款 / 开累供应</div>
      </div>
    </div>

    <el-card shadow="never" style="margin-top: 12px">
      <template #header>
        <div style="display:flex; align-items:center; justify-content:space-between">
          <b>债权明细</b>
          <span style="font-size:11px; color:#94a3b8">点击项目 → 穿透查看</span>
        </div>
      </template>
      <el-table :data="rows" border style="width:100%"
        :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }">
        <el-table-column label="项目" width="130">
          <template #default="{ row }">
            <span class="link-cell" @click="onProjectClick(row)">{{ row.project_name || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="subsidiary_name" label="子分公司" width="100" />
        <el-table-column label="开累供应" width="120" align="right">
          <template #default="{ row }">{{ fmt(row.cum_supply) }}</template>
        </el-table-column>
        <el-table-column label="应收债权" width="120" align="right">
          <template #default="{ row }">
            <span style="color:#2563eb; font-weight:500">{{ fmt(row.receivable) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="逾期债权" width="120" align="right">
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
      </el-table>
      <div class="table-footer">共 {{ rows.length }} 条</div>
    </el-card>

    <el-drawer v-model="drawer.visible" size="780px" :with-header="false">
      <div class="d-header">
        <div class="d-title">
          <el-icon color="#2563eb"><ScaleToOriginal /></el-icon>
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
          <el-table-column prop="subsidiary_name" label="子分公司" width="100" />
          <el-table-column label="应收债权" width="120" align="right">
            <template #default="{ row }">{{ fmt(row.receivable) }}</template>
          </el-table-column>
          <el-table-column label="逾期债权" width="120" align="right">
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
import { onMounted, reactive, ref } from 'vue'
import { ScaleToOriginal, Close } from '@element-plus/icons-vue'
import { getCreditOverviewApi, type CreditKPI, type CreditRow } from '@/api/credit'

const loading = ref(false)
const kpi = ref<CreditKPI>({ receivable: 0, overdue_receivable: 0, cum_supply: 0, receive_rate: 0 })
const rows = ref<CreditRow[]>([])

const drawer = reactive({
  visible: false,
  title: '',
  subtitle: '',
  rows: [] as CreditRow[],
})

function fmt(v?: number) {
  if (v === undefined || v === null) return '0.00'
  return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadData() {
  loading.value = true
  try {
    const data = await getCreditOverviewApi()
    kpi.value = data.kpi
    rows.value = data.rows
  } finally {
    loading.value = false
  }
}

function onKpiClick(type: 'receivable' | 'overdue') {
  if (type === 'receivable') {
    const sorted = [...rows.value].sort((a, b) => b.receivable - a.receivable)
    const top = sorted[0]
    if (top) {
      drawer.title = '最大应收项目'
      drawer.rows = [top]
      drawer.subtitle = `${top.project_name} · ¥${fmt(top.receivable)} 万`
      drawer.visible = true
    }
  } else {
    const overdue = rows.value.filter((r) => r.overdue_total > 0)
    if (overdue.length === 0) return
    drawer.title = '逾期债权明细'
    drawer.subtitle = `共 ${overdue.length} 条`
    drawer.rows = overdue
    drawer.visible = true
  }
}

function onProjectClick(row: CreditRow) {
  drawer.title = row.project_name || '项目'
  drawer.rows = [row]
  drawer.subtitle = `应收 ¥${fmt(row.receivable)} 万 · 逾期 ¥${fmt(row.overdue_total)} 万`
  drawer.visible = true
}

onMounted(loadData)
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #0f2a4a; }
.page-sub { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 4px; }

.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.kpi-card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
  padding: 16px; cursor: pointer; transition: all 0.15s;
}
.kpi-card:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
  transform: translateY(-1px);
}
.kpi-label { font-size: 12px; color: #94a3b8; margin-bottom: 8px; font-weight: 500; }
.kpi-value { font-size: 22px; font-weight: 700; }
.kpi-sub { font-size: 11px; color: #64748b; margin-top: 6px; }
.kpi-sub.dn { color: #e5484d; }

.table-footer { padding-top: 12px; font-size: 12px; color: #94a3b8; }
.link-cell { color: #2563eb; cursor: pointer; font-weight: 500; }
.link-cell:hover { text-decoration: underline; }
.dn { color: #e5484d; font-weight: 500; }

.d-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #e5e7eb; }
.d-title { display: flex; align-items: center; gap: 8px; font-size: 15px; }
.d-title b { font-weight: 600; color: #0f2a4a; }
.d-sub { color: #94a3b8; font-size: 12px; font-weight: 400; }
.d-body { padding: 20px; overflow-y: auto; flex: 1; }
.d-footer { padding: 12px 20px; border-top: 1px solid #e5e7eb; display: flex; justify-content: flex-end; }
</style>