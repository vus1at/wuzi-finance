<template>
  <div>
    <!-- 顶部 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><Connection /></el-icon>
        <span>供应商管理</span>
        <span class="page-sub">{{ list.length }}家 · 支持编辑修改</span>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增供应商
        </el-button>
      </div>
    </div>

    <!-- 筛选 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <el-input v-model="filters.keyword" placeholder="搜索供应商名称" clearable
          style="width: 240px" @keyup.enter="loadList" />
        <el-select v-model="filters.type_filter" placeholder="类型" clearable style="width: 130px">
          <el-option label="全部" value="" />
          <el-option label="厂商" value="厂商" />
          <el-option label="非厂商" value="非厂商" />
        </el-select>
        <el-button type="primary" @click="loadList">
          <el-icon><Search /></el-icon> 查询
        </el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-card shadow="never" style="margin-top: 12px">
      <el-table :data="list" v-loading="loading" border
        :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }"
        style="width: 100%">
        <el-table-column prop="id" label="编号" width="70" align="center">
          <template #default="{ row }">S{{ String(row.id).padStart(3, '0') }}</template>
        </el-table-column>
        <el-table-column prop="name" label="供应商名称" min-width="200" />
        <el-table-column prop="type" label="类型" width="90">
          <template #default="{ row }">
            <span :class="['tag', row.type === '厂商' ? 'blue' : 'gray']">{{ row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="contact" label="联系人" width="90" />
        <el-table-column prop="phone" label="联系方式" width="140" />
        <el-table-column prop="addr" label="企业地址" min-width="180" show-overflow-tooltip />
        <el-table-column prop="scope" label="经营范围" min-width="180" show-overflow-tooltip />
        <el-table-column prop="capital" label="注册资本" width="90" />
        <el-table-column prop="founded" label="成立时间" width="110" />
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">共 {{ list.length }} 条</div>
    </el-card>

    <!-- 弹窗 -->
    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑供应商' : '新增供应商'"
      width="620px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="供应商名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入全称" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio value="厂商">厂商</el-radio>
            <el-radio value="非厂商">非厂商</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="联系人" prop="contact">
          <el-input v-model="form.contact" placeholder="如：张伟" />
        </el-form-item>
        <el-form-item label="联系方式" prop="phone">
          <el-input v-model="form.phone" placeholder="如：138-0000-0000" />
        </el-form-item>
        <el-form-item label="企业地址" prop="addr">
          <el-input v-model="form.addr" placeholder="如：山东省泰安市..." />
        </el-form-item>
        <el-form-item label="经营范围" prop="scope">
          <el-input v-model="form.scope" placeholder="如：土工材料生产销售" />
        </el-form-item>
        <el-form-item label="注册资本" prop="capital">
          <el-input v-model="form.capital" placeholder="如：8000万" />
        </el-form-item>
        <el-form-item label="成立时间" prop="founded">
        <el-date-picker
            v-model="form.founded"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
        />
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
import { Connection, Plus, Search } from '@element-plus/icons-vue'
import {
  listSuppliersApi, createSupplierApi, updateSupplierApi,
  deleteSupplierApi, type Supplier,
} from '@/api/supplier'

const list = ref<Supplier[]>([])
const loading = ref(false)
const saving = ref(false)
const filters = reactive({ keyword: '', type_filter: '' })

const dialog = reactive({ visible: false, isEdit: false, editingId: 0 })
const formRef = ref<FormInstance>()
const form = reactive({
  name: '', type: '厂商', contact: '', phone: '',
  addr: '', scope: '', capital: '', founded: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
}

async function loadList() {
  loading.value = true
  try { list.value = await listSuppliersApi(filters) }
  finally { loading.value = false }
}

function resetFilters() {
  filters.keyword = ''
  filters.type_filter = ''
  loadList()
}

function openCreate() {
  dialog.isEdit = false
  dialog.editingId = 0
  Object.assign(form, {
    name: '', type: '厂商', contact: '', phone: '',
    addr: '', scope: '', capital: '', founded: '',
  })
  dialog.visible = true
}

function openEdit(row: Supplier) {
  dialog.isEdit = true
  dialog.editingId = row.id
  Object.assign(form, {
    name: row.name,
    type: row.type || '厂商',
    contact: row.contact || '',
    phone: row.phone || '',
    addr: row.addr || '',
    scope: row.scope || '',
    capital: row.capital || '',
    founded: row.founded || '',
  })
  dialog.visible = true
}

async function onSubmit() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) return
  saving.value = true
  try {
    if (dialog.isEdit) {
      await updateSupplierApi(dialog.editingId, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createSupplierApi({ ...form })
      ElMessage.success('新增成功')
    }
    dialog.visible = false
    loadList()
  } finally {
    saving.value = false
  }
}

async function onDelete(row: Supplier) {
  try {
    await ElMessageBox.confirm(`确定删除供应商"${row.name}"？`, '提示', { type: 'warning' })
  } catch { return }
  await deleteSupplierApi(row.id)
  ElMessage.success('删除成功')
  loadList()
}

onMounted(loadList)
</script>

<style scoped>
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px;
}
.page-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 16px; font-weight: 700; color: #0f2a4a;
}
.page-sub { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 4px; }
.filter-card :deep(.el-card__body) { padding: 12px 16px; }
.filter-bar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.table-footer { padding-top: 12px; font-size: 12px; color: #94a3b8; }

.tag {
  display: inline-block; padding: 2px 8px; border-radius: 10px;
  font-size: 11px; font-weight: 600;
}
.tag.blue { background: #dbeafe; color: #2563eb; }
.tag.gray { background: #f3f4f6; color: #6b7280; }
</style>