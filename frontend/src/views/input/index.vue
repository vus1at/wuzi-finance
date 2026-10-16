<template>
  <div>
    <!-- 顶部 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><Upload /></el-icon>
        <span>数据填报</span>
        <span class="page-sub">{{ list.length }}条台账</span>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 手动填报
        </el-button>
        <el-button @click="onImport">
          <el-icon><DocumentAdd /></el-icon> 导入 Excel
        </el-button>
        <el-button @click="onDownloadTemplate">
          <el-icon><Download /></el-icon> 下载模板
        </el-button>
      </div>
    </div>

    <!-- 筛选：期间 + 管理类型 + 供应商 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <el-select v-model="filters.period" placeholder="期间" style="width: 130px">
          <el-option label="2026年9月" value="2026-09" />
          <el-option label="2026年8月" value="2026-08" />
        </el-select>
        <el-select v-model="filters.management_type" placeholder="管理类型" clearable style="width: 160px">
          <el-option label="全部" value="" />
          <el-option v-for="t in ['A类材料厂', '集采中心', '收尾材料厂', '华阳分公司']"
            :key="t" :label="t" :value="t" />
        </el-select>
        <el-select
          v-model="filters.supplier_id"
          placeholder="供应商"
          clearable
          filterable
          style="width: 240px"
        >
          <el-option
            v-for="s in suppliers"
            :key="s.id"
            :label="s.name"
            :value="s.id"
          />
        </el-select>
        <el-button type="primary" @click="onSearch">
          <el-icon><Search /></el-icon> 查询
        </el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-card shadow="never" style="margin-top: 12px">
      <el-table
        :data="list"
        v-loading="loading"
        border
        style="width: 100%"
        :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }"
      >
        <el-table-column prop="id" label="序号" width="70" align="center" />
        <el-table-column prop="project_name" label="项目" min-width="120">
          <template #default="{ row }">
            <span class="link-cell" @click="onView(row)">{{ row.project_name || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="supplier_name" label="供应商" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="link-cell" @click="onView(row)">{{ row.supplier_name || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="material_category" label="物资" width="100" />
        <el-table-column prop="management_type" label="管理类型" width="110" />
        <el-table-column prop="supply_category" label="供应类别" width="100" />
        <el-table-column label="本月采购" width="100" align="right">
          <template #default="{ row }">{{ fmt(row.monthly_purchase_amount) }}</template>
        </el-table-column>
        <el-table-column label="本月供应" width="100" align="right">
          <template #default="{ row }">{{ fmt(row.monthly_supply_amount) }}</template>
        </el-table-column>
        <el-table-column label="利润" width="90" align="right">
          <template #default="{ row }">
            <span class="up">{{ fmt(row.profit_management_fee) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="债务" width="100" align="right">
          <template #default="{ row }">
            <span class="dn">{{ fmt(row.upstream_debt_total_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="逾期" width="90" align="center">
          <template #default="{ row }">
            <span v-if="(row.upstream_debt_overdue_6_12m || 0) > 0" class="tag red">
              {{ fmt(row.upstream_debt_overdue_6_12m) }}
            </span>
            <span v-else class="tag green">正常</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">
        共 {{ list.length }} 条
        <span class="tip">（数据暂用 mock，等 data_detail 定稿后自动接后端）</span>
      </div>
    </el-card>

    <!-- 表单抽屉 -->
    <LedgerFormDrawer
      v-model="drawer.visible"
      :mode="drawer.mode"
      :edit-id="drawer.editId"
      :projects="projects"
      :suppliers="suppliers"
      @saved="loadList"
    />

    <!-- 详情抽屉 -->
    <LedgerDetailDrawer v-model="detail.visible" :ledger-id="detail.id" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Plus, DocumentAdd, Download, Search } from '@element-plus/icons-vue'
import {
  listLedgerApi, deleteLedgerApi, type Ledger,
} from '@/api/ledger'
import request from '@/utils/request'
import LedgerFormDrawer from './LedgerFormDrawer.vue'
import LedgerDetailDrawer from './LedgerDetailDrawer.vue'

interface Project { id: number; name: string }
interface Supplier { id: number; name: string }

const list = ref<Ledger[]>([])
const projects = ref<Project[]>([])
const suppliers = ref<Supplier[]>([])
const loading = ref(false)

const filters = reactive({
  period: '2026-09',
  management_type: '',
  supplier_id: undefined as number | undefined,
})

const drawer = reactive({
  visible: false,
  mode: 'create' as 'create' | 'edit',
  editId: 0,
})

const detail = reactive({
  visible: false,
  id: 0,
})

function fmt(v?: number) {
  if (v === undefined || v === null) return '—'
  return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadList() {
  loading.value = true
  try {
    list.value = await listLedgerApi(filters)
  } finally {
    loading.value = false
  }
}

async function loadProjects() {
  try {
    projects.value = await request.get<any, Project[]>('/projects', { params: { } }).catch(() => [])
  } catch { projects.value = [] }
}

async function loadSuppliers() {
  try {
    const res = await request.get<any, Supplier[]>('/suppliers')
    suppliers.value = Array.isArray(res) ? res : []
  } catch {
    suppliers.value = []
  }
}

function onSearch() {
  ElMessage.success('筛选条件已应用')
  loadList()
}

function resetFilters() {
  filters.period = '2026-09'
  filters.management_type = ''
  filters.supplier_id = undefined
  ElMessage.success('已重置')
  loadList()
}
function openCreate() {
  drawer.mode = 'create'
  drawer.editId = 0
  drawer.visible = true
}

function openEdit(row: Ledger) {
  drawer.mode = 'edit'
  drawer.editId = row.id
  drawer.visible = true
}

function onView(row: Ledger) {
  detail.id = row.id
  detail.visible = true
}

async function onDelete(row: Ledger) {
  try {
    await ElMessageBox.confirm(`确定删除该台账记录？`, '提示', { type: 'warning' })
  } catch { return }
  await deleteLedgerApi(row.id)
  ElMessage.success('删除成功')
  loadList()
}

function onImport() {
  ElMessage.info('Excel 导入功能待开发（需等真实样例数据）')
}

function onDownloadTemplate() {
  ElMessage.info('模板下载功能待开发')
}

onMounted(() => {
  loadList()
  loadProjects()
  loadSuppliers()
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #0f2a4a; }
.page-sub { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 4px; }
.filter-card :deep(.el-card__body) { padding: 12px 16px; }
.filter-bar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.table-footer {
  padding-top: 12px; font-size: 12px; color: #94a3b8;
  display: flex; justify-content: space-between;
}
.tip { color: #f59e0b; }

.link-cell { color: #2563eb; cursor: pointer; }
.link-cell:hover { text-decoration: underline; }
.up { color: #16a34a; font-weight: 500; }
.dn { color: #e5484d; font-weight: 500; }

.tag {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 11px; font-weight: 600;
}
.tag.red { background: #fee2e2; color: #dc2626; }
.tag.green { background: #d1fae5; color: #059669; }
</style>