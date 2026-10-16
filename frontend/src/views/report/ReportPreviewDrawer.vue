<template>
  <el-drawer
    :model-value="modelValue"
    size="92%"
    :with-header="false"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="d-header">
      <div class="d-title">
        <el-icon color="#2563eb"><Document /></el-icon>
        <b>{{ config?.name || '报表' }}</b>
        <span class="d-sub">{{ config?.desc }}</span>
      </div>
      <el-button link @click="emit('update:modelValue', false)">
        <el-icon :size="18"><Close /></el-icon>
      </el-button>
    </div>

    <div class="d-body" v-loading="loading">
      <div v-if="config" class="table-wrap">
        <table class="report-table">
          <thead>
            <tr>
              <th v-for="col in config.columns" :key="col.prop"
                :style="thStyle(col)">
                {{ col.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in rows" :key="i">
              <td v-for="col in config.columns" :key="col.prop"
                :style="tdStyle(col)"
                :class="{ 'align-right': col.align === 'right', 'align-center': col.align === 'center' }">
                {{ col.formatter ? col.formatter(row[col.prop], row) : (row[col.prop] ?? '—') }}
              </td>
            </tr>
            <tr v-if="rows.length === 0">
              <td :colspan="config.columns.length" class="empty-cell">
                <el-icon :size="30" style="opacity:.3"><Document /></el-icon>
                <div style="margin-top:8px;color:#94a3b8">暂无数据</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="d-footer">
      <span class="record-count">共 {{ rows.length }} 条</span>
      <div class="spacer"></div>
      <el-button @click="emit('update:modelValue', false)">关闭</el-button>
      <el-button @click="onExportPDF">
        <el-icon><Document /></el-icon> 导出 PDF
      </el-button>
      <el-button type="primary" @click="onExportExcel">
        <el-icon><Download /></el-icon> 导出 Excel
      </el-button>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Close, Download } from '@element-plus/icons-vue'
import type { ReportConfig, ReportColumn } from '@/api/reports'

const props = defineProps<{
  modelValue: boolean
  config: ReportConfig | null
}>()
const emit = defineEmits<{ 'update:modelValue': [boolean] }>()

const rows = ref<any[]>([])
const loading = ref(false)

function thStyle(col: ReportColumn) {
  const w = col.width ? `${col.width}px` : col.minWidth ? `min-width:${col.minWidth}px` : ''
  return w
}
function tdStyle(col: ReportColumn) {
  return ''
}

async function loadData() {
  if (!props.config) return
  loading.value = true
  try {
    rows.value = await props.config.fetch()
  } catch (e) {
    ElMessage.error('加载报表失败')
    rows.value = []
  } finally {
    loading.value = false
  }
}

function onExportExcel() {
  ElMessage.info('Excel 导出待开发（等后端数据接口定稿）')
}
function onExportPDF() {
  ElMessage.info('PDF 导出待开发（等后端数据接口定稿）')
}

watch(
  () => [props.modelValue, props.config?.code] as const,
  ([visible]) => { if (visible) loadData() },
)
</script>

<style scoped>
.d-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; border-bottom: 1px solid #e5e7eb; flex-shrink: 0;
}
.d-title { display: flex; align-items: center; gap: 8px; font-size: 15px; }
.d-title b { font-weight: 600; color: #0f2a4a; }
.d-sub { color: #94a3b8; font-size: 12px; font-weight: 400; margin-left: 4px; }

.d-body { padding: 0; overflow: auto; flex: 1; }
.table-wrap { padding: 16px 20px; overflow-x: auto; }

.report-table {
  border-collapse: collapse;
  font-size: 12px;
  width: 100%;
  font-variant-numeric: tabular-nums;
}
.report-table th {
  background: #0f2a4a;
  color: #fff;
  font-weight: 600;
  padding: 8px 10px;
  text-align: left;
  white-space: nowrap;
  border: 1px solid #1e3a5f;
  position: sticky; top: 0; z-index: 1;
}
.report-table td {
  padding: 6px 10px;
  border: 1px solid #e5e7eb;
  white-space: nowrap;
  color: #1e293b;
}
.report-table tbody tr:nth-child(even) {
  background: #fafbfc;
}
.report-table tbody tr:hover {
  background: #eff6ff;
}
.align-right { text-align: right !important; }
.align-center { text-align: center !important; }

.empty-cell {
  text-align: center;
  padding: 60px 0 !important;
  color: #94a3b8;
}

.d-footer {
  padding: 12px 20px; border-top: 1px solid #e5e7eb;
  display: flex; align-items: center; gap: 8px; flex-shrink: 0;
}
.record-count { font-size: 12px; color: #94a3b8; }
.spacer { flex: 1; }
</style>