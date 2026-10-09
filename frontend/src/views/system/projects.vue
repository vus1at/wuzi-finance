<template>
  <div>
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><OfficeBuilding /></el-icon>
        <span>项目管理</span>
        <span class="page-sub">{{ list.length }}个项目 · 支持编辑修改</span>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增项目
        </el-button>
      </div>
    </div>

    <!-- 筛选区 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索项目名称"
          clearable
          style="width: 200px"
          @keyup.enter="loadList"
        />
        <el-select v-model="filters.category" placeholder="项目类别" clearable style="width: 130px">
          <el-option label="全部" value="" />
          <el-option label="铁路" value="铁路" />
          <el-option label="公路" value="公路" />
          <el-option label="市政" value="市政" />
          <el-option label="水利" value="水利" />
        </el-select>
        <el-select v-model="filters.status_filter" placeholder="项目状态" clearable style="width: 130px">
          <el-option label="全部" :value="undefined" />
          <el-option label="启用" :value="1" />
          <el-option label="停用" :value="0" />
        </el-select>
        <el-button type="primary" @click="loadList">
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
        <el-table-column prop="id" label="编号" width="80" align="center">
          <template #default="{ row }">P{{ String(row.id).padStart(3, '0') }}</template>
        </el-table-column>
        <el-table-column prop="name" label="项目名称" min-width="140" />
        <el-table-column prop="category" label="类别" width="100" />
        <el-table-column prop="subsidiary_name" label="子分公司" width="110">
          <template #default="{ row }">
            <span>{{ row.subsidiary_name || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="项目地址" min-width="140" />
        <el-table-column prop="status" label="项目状态" width="140">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              :active-value="1"
              :inactive-value="0"
              @change="(val: number) => onToggleStatus(row, val)"
            />
            <span
              :style="{
                marginLeft: '8px',
                fontSize: '12px',
                color: row.status === 1 ? '#16a34a' : '#94a3b8',
              }"
            >
              {{ row.status === 1 ? '开启' : '关闭' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="table-footer">共 {{ list.length }} 条</div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑项目' : '新增项目'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="如：大瑞1" />
        </el-form-item>
        <el-form-item label="项目类别" prop="category">
          <el-select v-model="form.category" style="width: 100%">
            <el-option label="铁路" value="铁路" />
            <el-option label="公路" value="公路" />
            <el-option label="市政" value="市政" />
            <el-option label="水利" value="水利" />
          </el-select>
        </el-form-item>
        <el-form-item label="子分公司" prop="subsidiary_id">
          <el-select
            v-model="form.subsidiary_id"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="d in departments"
              :key="d.id"
              :label="d.name"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目地址" prop="address">
          <el-input v-model="form.address" placeholder="如：云南大理" />
        </el-form-item>
        <el-form-item label="项目状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSubmit">
          {{ dialog.isEdit ? '保存修改' : '确认新增' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { OfficeBuilding, Plus, Search } from '@element-plus/icons-vue'
import {
  listProjectsApi,
  createProjectApi,
  updateProjectApi,
  deleteProjectApi,
  toggleProjectStatusApi,
  type Project,
} from '@/api/project'
import request from '@/utils/request'

interface Department {
  id: number
  name: string
}

const list = ref<Project[]>([])
const departments = ref<Department[]>([])
const loading = ref(false)
const saving = ref(false)

const filters = reactive<{
  keyword: string
  category: string
  status_filter: number | undefined
}>({
  keyword: '',
  category: '',
  status_filter: undefined,
})

const dialog = reactive({ visible: false, isEdit: false, editingId: 0 })
const formRef = ref<FormInstance>()
const form = reactive({
  name: '',
  category: '铁路',
  subsidiary_id: undefined as number | undefined,
  address: '',
  status: 1,
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

async function loadList() {
  loading.value = true
  try {
    list.value = await listProjectsApi(filters)
  } finally {
    loading.value = false
  }
}

async function loadDepartments() {
  departments.value = await request.get<any, Department[]>('/projects/meta/departments')
}

function resetFilters() {
  filters.keyword = ''
  filters.category = ''
  filters.status_filter = undefined
  loadList()
}

function openCreate() {
  dialog.isEdit = false
  dialog.editingId = 0
  Object.assign(form, {
    name: '',
    category: '铁路',
    subsidiary_id: undefined,
    address: '',
    status: 1,
  })
  dialog.visible = true
}

function openEdit(row: Project) {
  dialog.isEdit = true
  dialog.editingId = row.id
  Object.assign(form, {
    name: row.name,
    category: row.category || '铁路',
    subsidiary_id: row.subsidiary_id ?? undefined,
    address: row.address || '',
    status: row.status,
  })
  dialog.visible = true
}

async function onSubmit() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) return
  saving.value = true
  try {
    const payload = {
      ...form,
      subsidiary_id: form.subsidiary_id ?? null,
    }
    if (dialog.isEdit) {
      await updateProjectApi(dialog.editingId, payload as any)
      ElMessage.success('修改成功')
    } else {
      await createProjectApi(payload as any)
      ElMessage.success('新增成功')
    }
    dialog.visible = false
    loadList()
  } finally {
    saving.value = false
  }
}

async function onDelete(row: Project) {
  try {
    await ElMessageBox.confirm(`确定删除项目"${row.name}"？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  await deleteProjectApi(row.id)
  ElMessage.success('删除成功')
  loadList()
}

async function onToggleStatus(row: Project, val: number) {
  try {
    await toggleProjectStatusApi(row.id, val)
    ElMessage.success(`项目已${val === 1 ? '启用' : '停用'}`)
  } catch {
    // 失败回滚
    row.status = val === 1 ? 0 : 1
  }
}

onMounted(() => {
  loadList()
  loadDepartments()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}
.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #0f2a4a;
}
.page-sub {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 400;
  margin-left: 4px;
}
.filter-card :deep(.el-card__body) {
  padding: 12px 16px;
}
.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.table-footer {
  padding-top: 12px;
  font-size: 12px;
  color: #94a3b8;
}
</style>