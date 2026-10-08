<template>
  <div v-loading="loading">
    <!-- 标题 -->
    <div class="st">
      <el-icon :size="20" color="#2563eb"><Odometer /></el-icon>
      <span class="title">看板统计</span>
      <span class="sub">2026年9月 · {{ overview.project_count }}条台账 · {{ overview.project_count }}个项目 · {{ overview.supplier_count }}家供应商</span>
    </div>

    <!-- KPI 卡片（真数据） -->
    <div class="kpi-grid">
      <div class="kpi-card" @click="router.push('/input')">
        <div class="kpi-label">本月采购总额</div>
        <div class="kpi-value">¥{{ fmt(kpi.month_purchase) }} 万</div>
        <div class="kpi-sub up">环比 ↑8.3%</div>
      </div>
      <div class="kpi-card" @click="router.push('/input')">
        <div class="kpi-label">本月供应总额</div>
        <div class="kpi-value">¥{{ fmt(kpi.month_supply) }} 万</div>
        <div class="kpi-sub up">利润 ¥{{ fmt(overview.total_profit) }} 万</div>
      </div>
      <div class="kpi-card" @click="router.push('/debt')">
        <div class="kpi-label">总债务余额</div>
        <div class="kpi-value" style="color: #e5484d">¥{{ fmt(kpi.total_debt) }} 万</div>
        <div class="kpi-sub dn">逾期率 {{ kpi.overdue_rate }}%</div>
      </div>
      <div class="kpi-card" @click="router.push('/credit')">
        <div class="kpi-label">应收债权</div>
        <div class="kpi-value" style="color: #2563eb">¥{{ fmt(kpi.receivable) }} 万</div>
        <div class="kpi-sub dn">逾期 {{ kpi.recv_overdue_rate }}%</div>
      </div>
      <div class="kpi-card" @click="router.push('/report')">
        <div class="kpi-label">本月回款</div>
        <div class="kpi-value" style="color: #16a34a">¥{{ fmt(kpi.month_receive) }} 万</div>
        <div class="kpi-sub">回款率 {{ kpi.receive_rate }}%</div>
      </div>
    </div>

    <!-- 图表区（趋势图仍用静态，饼图用真数据） -->
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

    <!-- TOP5（真数据） -->
    <div class="row">
      <el-card class="flex1">
        <template #header>
          <el-icon color="#f59e0b"><Trophy /></el-icon>
          <b>项目供应 TOP5</b>
        </template>
        <div v-for="(p, i) in top_projects" :key="p.name" class="rank-item">
          <span class="rank-badge" :class="i < 3 ? 'blue' : 'gray'">{{ i + 1 }}</span>
          <span class="rank-name">{{ p.name }}</span>
          <span class="rank-mat">{{ p.material }}</span>
          <span class="rank-val">{{ fmt(p.value) }} 万</span>
        </div>
      </el-card>

      <el-card class="flex1">
        <template #header>
          <el-icon color="#2563eb"><OfficeBuilding /></el-icon>
          <b>供应商债务 TOP5</b>
        </template>
        <div v-for="(s, i) in top_suppliers" :key="s.name" class="rank-item">
          <span class="rank-badge" :class="i < 3 ? 'red' : 'orange'">{{ i + 1 }}</span>
          <span class="rank-name">{{ s.name }}</span>
          <span class="rank-mat">{{ s.pct }}%</span>
          <span class="rank-val danger">{{ fmt(s.value) }} 万</span>
        </div>
      </el-card>
    </div>

    <!-- 预警 + 概览（真数据） -->
    <div class="row">
      <el-card class="flex1">
        <template #header>
          <el-icon color="#e5484d"><Warning /></el-icon>
          <b>逾期预警</b>
          <span class="hdr-sub">{{ alerts.length }}项逾期</span>
        </template>
        <div v-for="a in alerts" :key="a.supplier + a.project" class="rank-item">
          <span class="rank-badge red">逾期</span>
          <span class="rank-name">{{ a.supplier }}（{{ a.project }}）</span>
          <span class="rank-val danger">{{ fmt(a.value) }} 万</span>
          <span class="rank-days">{{ a.days }}天</span>
        </div>
      </el-card>

      <el-card class="flex1">
        <template #header>
          <el-icon color="#16a34a"><Document /></el-icon>
          <b>本月数据概览</b>
        </template>
        <div class="overview">
          <div class="ov-item"><span>项目数</span><b>{{ overview.project_count }}</b></div>
          <div class="ov-item"><span>供应商数</span><b>{{ overview.supplier_count }}</b></div>
          <div class="ov-item"><span>区域集采</span><b>¥{{ fmt(overview.region_supply) }} 万</b></div>
          <div class="ov-item"><span>内供集采</span><b>¥{{ fmt(overview.inner_supply) }} 万</b></div>
          <div class="ov-item"><span>高风险债务</span><b style="color: #e5484d">¥{{ fmt(overview.high_risk_debt) }} 万</b></div>
          <div class="ov-item"><span>总利润</span><b style="color: #16a34a">¥{{ fmt(overview.total_profit) }} 万</b></div>
          <div class="ov-item"><span>总逾期债务</span><b style="color: #e5484d">¥{{ fmt(overview.total_overdue_debt) }} 万</b></div>
          <div class="ov-item"><span>逾期债权</span><b style="color: #e5484d">¥{{ fmt(overview.total_overdue_recv) }} 万</b></div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import {
  Odometer, TrendCharts, PieChart, Trophy, OfficeBuilding, Warning, Document,
} from '@element-plus/icons-vue'
import { getDashboardApi } from '@/api/dashboard'

const router = useRouter()
const loading = ref(false)
const trendRef = ref<HTMLElement>()
const pieRef = ref<HTMLElement>()

const kpi = reactive({
  month_purchase: 0, month_supply: 0, total_debt: 0,
  receivable: 0, month_receive: 0,
  overdue_rate: 0, recv_overdue_rate: 0, receive_rate: 0,
})
const overview = reactive({
  project_count: 0, supplier_count: 0,
  region_supply: 0, inner_supply: 0,
  high_risk_debt: 0, total_profit: 0,
  total_overdue_debt: 0, total_overdue_recv: 0,
})
const top_projects = ref<{ name: string; value: number; material: string }[]>([])
const top_suppliers = ref<{ name: string; value: number; pct: number }[]>([])
const alerts = ref<{ supplier: string; project: string; value: number; days: number }[]>([])
const debt_pie = ref<{ name: string; value: number }[]>([])

function fmt(v: number) {
  return (v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadData() {
  loading.value = true
  try {
    const data = await getDashboardApi()
    Object.assign(kpi, data.kpi)
    Object.assign(overview, data.overview)
    top_projects.value = data.top_projects
    top_suppliers.value = data.top_suppliers
    alerts.value = data.alerts
    debt_pie.value = data.debt_pie
    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  // 月度趋势（暂时用静态数据）
  if (trendRef.value) {
    const c = echarts.init(trendRef.value)
    c.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['采购', '供应', '回款'], bottom: 0, itemWidth: 10, itemHeight: 10, textStyle: { fontSize: 11 } },
      grid: { left: 40, right: 16, top: 16, bottom: 36 },
      xAxis: { type: 'category', data: ['3月', '4月', '5月', '6月', '7月', '8月', '9月'], axisLabel: { fontSize: 11 } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f2f4' } }, axisLabel: { fontSize: 11 } },
      series: [
        { name: '采购', type: 'bar', data: [240, 310, 280, 340, 320, 380, kpi.month_purchase], barWidth: 14, itemStyle: { color: '#2563eb', borderRadius: [4, 4, 0, 0] } },
        { name: '供应', type: 'bar', data: [220, 290, 265, 320, 300, 350, kpi.month_supply], barWidth: 14, itemStyle: { color: '#93c5fd', borderRadius: [4, 4, 0, 0] } },
        { name: '回款', type: 'line', data: [160, 200, 210, 230, 240, 260, kpi.month_receive], smooth: true, lineStyle: { color: '#16a34a' }, itemStyle: { color: '#16a34a' } },
      ],
    })
  }

  // 债务饼图（真数据）
  if (pieRef.value && debt_pie.value.length > 0) {
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
        data: debt_pie.value.map((d) => ({
          value: d.value, name: d.name,
          itemStyle: { color: colors[d.name] || '#6b7280' },
        })),
      }],
    })
  }
}

onMounted(loadData)
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
  padding: 10px 8px; margin: 0 -8px;
  border-bottom: 1px solid #f1f2f4;
  font-size: 13px; font-weight: 500;
  border-radius: 6px;
}
.rank-item:last-child { border-bottom: none; }

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
.rank-val { font-weight: 600; color: #1e293b; }
.rank-val.danger { color: #e5484d; }
.rank-days { font-size: 11px; color: #94a3b8; margin-left: 6px; font-weight: 500; }

.rank-mat {
  color: #94a3b8;
  font-size: 11px;
  margin-right: 8px;
  font-weight: 500;
}

.overview { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 20px; }
.ov-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f2f4; font-size: 12px; }
.ov-item span { color: #94a3b8; font-weight: 500; }
.ov-item b { font-weight: 600; }
</style>