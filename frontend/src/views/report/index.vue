<template>
  <div>
    <!-- 顶部 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><PieChart /></el-icon>
        <span>报表中心</span>
        <span class="page-sub">13张 · 支持多字段筛选和分类导出</span>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="onGenerateAll">
          <el-icon><Refresh /></el-icon> 全量生成
        </el-button>
        <el-button @click="onClassifyExport">
          <el-icon><FolderOpened /></el-icon> 分类导出
        </el-button>
        <el-button @click="onBatchExport">
          <el-icon><Download /></el-icon> 批量导出
        </el-button>
      </div>
    </div>

    <!-- 筛选条 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <label class="filter-label">期间</label>
        <el-select v-model="filters.period" style="width: 130px">
          <el-option label="2026年9月" value="2026-09" />
        </el-select>

        <label class="filter-label">管理类型</label>
        <el-select v-model="filters.management_type" clearable style="width: 130px">
          <el-option label="全部" value="" />
          <el-option v-for="t in ['A类材料厂', '集采中心', '收尾材料厂', '华阳分公司']"
            :key="t" :label="t" :value="t" />
        </el-select>

        <label class="filter-label">供应类别</label>
        <el-select v-model="filters.supply_category" clearable style="width: 130px">
          <el-option label="全部" value="" />
          <el-option v-for="t in ['区域集采', '内供集采', '三方供应', '自产', '外购']"
            :key="t" :label="t" :value="t" />
        </el-select>

        <label class="filter-label">项目</label>
        <el-select v-model="filters.project_id" clearable filterable style="width: 150px">
          <el-option label="全部" :value="undefined" />
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>

        <el-button type="primary" @click="onSearch">
          <el-icon><Search /></el-icon> 筛选
        </el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 分组 Tab -->
    <el-card shadow="never" style="margin-top: 12px">
      <el-tabs v-model="activeGroup">
        <el-tab-pane v-for="g in REPORT_GROUPS" :key="g.key" :label="g.label" :name="g.key">
          <div class="rpt-grid">
            <div
              v-for="rpt in reportsOfGroup(g.key)"
              :key="rpt.code"
              class="rpt-card"
              @click="openPreview(rpt)"
            >
              <!-- 图标 -->
              <div class="rpt-icon">
                <el-icon :size="20" color="#2563eb"><Document /></el-icon>
              </div>

              <!-- 名字 + 描述 -->
              <div class="rpt-content">
                <div class="rpt-name">{{ rpt.name }}</div>
                <div class="rpt-desc">{{ rpt.desc }}</div>
              </div>

              <!-- 右上角编号 -->
              <div class="rpt-code">{{ rpt.code }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 预览抽屉 -->
    <ReportPreviewDrawer v-model="preview.visible" :config="preview.config" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  PieChart, Document, Refresh, Download, Search, FolderOpened,
} from '@element-plus/icons-vue'
import { ALL_REPORTS, REPORT_GROUPS, type ReportConfig } from '@/api/reports'
import request from '@/utils/request'
import ReportPreviewDrawer from './ReportPreviewDrawer.vue'

interface Project { id: number; name: string }

const activeGroup = ref<ReportConfig['group']>('核心报表')
const projects = ref<Project[]>([])

const filters = reactive({
  period: '2026-09',
  management_type: '',
  supply_category: '',
  project_id: undefined as number | undefined,
})

const reports = ref<ReportConfig[]>([])

const preview = reactive<{
  visible: boolean
  config: ReportConfig | null
}>({
  visible: false,
  config: null,
})

function reportsOfGroup(g: ReportConfig['group']) {
  return reports.value.filter((r) => r.group === g)
}

async function loadProjects() {
  try {
    const res = await request.get<any, Project[]>('/projects')
    projects.value = Array.isArray(res) ? res : []
  } catch {
    projects.value = []
  }
}

function resetFilters() {
  filters.period = '2026-09'
  filters.management_type = ''
  filters.supply_category = ''
  filters.project_id = undefined
  ElMessage.success('已重置')
}

function onSearch() {
  ElMessage.success('筛选条件已应用（mock 阶段暂不过滤）')
}

function openPreview(rpt: ReportConfig) {
  preview.config = rpt
  preview.visible = true
}

function onGenerateAll() {
  ElMessage.success('已触发全量生成（13 张报表）')
}

function onClassifyExport() {
  ElMessage.info('分类导出待开发（按管理类型 / 供应类别打包 ZIP）')
}

function onBatchExport() {
  ElMessage.info('批量导出待开发')
}

onMounted(() => {
  reports.value = ALL_REPORTS
  loadProjects()
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #0f2a4a; }
.page-sub { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 4px; }

.filter-card :deep(.el-card__body) { padding: 12px 16px; }
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.filter-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

/* ============ 卡片网格 ============ */
.rpt-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 6px;
}

.rpt-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s;
}
.rpt-card:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
  transform: translateY(-1px);
}

.rpt-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rpt-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rpt-name {
  font-size: 14px;
  font-weight: 600;
  color: #0f2a4a;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rpt-desc {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rpt-code {
  position: absolute;
  top: 8px;
  right: 12px;
  font-size: 11px;
  font-weight: 600;
  color: #e2e8f0;
  letter-spacing: 0.5px;
  user-select: none;
}
.rpt-card:hover .rpt-code {
  color: #93c5fd;
}
</style>