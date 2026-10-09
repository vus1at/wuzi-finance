<template>
  <div>
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><UserFilled /></el-icon>
        <span>用户权限</span>
        <span class="page-sub">{{ list.length }}个用户 · 支持编辑、角色分配</span>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增用户
        </el-button>
      </div>
    </div>

    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <el-input v-model="filters.keyword" placeholder="搜索用户名/姓名" clearable
          style="width: 220px" @keyup.enter="loadList" />
        <el-select v-model="filters.status_filter" placeholder="状态" clearable style="width: 130px">
          <el-option label="全部" :value="undefined" />
          <el-option label="启用" :value="1" />
          <el-option label="禁用" :value="0" />
        </el-select>
        <el-button type="primary" @click="loadList">
          <el-icon><Search /></el-icon> 查询
        </el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top: 12px">
      <el-table :data="list" v-loading="loading" border
        :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }"
        style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column prop="real_name" label="真实姓名" width="110" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column label="角色" min-width="180">
          <template #default="{ row }">
            <el-tag v-for="rn in row.role_names" :key="rn" type="primary" effect="light" style="margin-right: 4px">
              {{ rn }}
            </el-tag>
            <span v-if="!row.role_names.length" style="color: #94a3b8">未分配</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="light">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="warning" @click="onResetPwd(row)">重置密码</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">共 {{ list.length }} 条</div>
    </el-card>

    <el-dialog v-model="dialog.visible" :title="dialog.isEdit ? '编辑用户' : '新增用户'"
      width="560px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="登录账号" :disabled="dialog.isEdit" />
        </el-form-item>
        <el-form-item v-if="!dialog.isEdit" label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="至少 6 位" show-password />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="如：张三" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="如：13800000000" />
        </el-form-item>
        <el-form-item label="角色" prop="role_ids">
          <el-select v-model="form.role_ids" multiple style="width: 100%" placeholder="选择角色">
            <el-option v-for="r in roles" :key="r.id" :label="r.role_name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
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
import { UserFilled, Plus, Search } from '@element-plus/icons-vue'
import {
  listRolesApi, listUsersApi, createUserApi, updateUserApi,
  deleteUserApi, resetPasswordApi, type SysUser, type Role,
} from '@/api/sys-user'

const list = ref<SysUser[]>([])
const roles = ref<Role[]>([])
const loading = ref(false)
const saving = ref(false)

const filters = reactive<{ keyword: string; status_filter: number | undefined }>({
  keyword: '', status_filter: undefined,
})

const dialog = reactive({ visible: false, isEdit: false, editingId: 0 })
const formRef = ref<FormInstance>()
const form = reactive({
  username: '', password: '', real_name: '', phone: '',
  role_ids: [] as number[], status: 1,
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少 6 位', trigger: 'blur' }],
}

async function loadList() {
  loading.value = true
  try {
    list.value = await listUsersApi(filters)
  } finally { loading.value = false }
}

async function loadRoles() {
  roles.value = await listRolesApi()
}

function resetFilters() {
  filters.keyword = ''
  filters.status_filter = undefined
  loadList()
}

function openCreate() {
  dialog.isEdit = false
  dialog.editingId = 0
  Object.assign(form, {
    username: '', password: '', real_name: '', phone: '',
    role_ids: [], status: 1,
  })
  dialog.visible = true
}

function openEdit(row: SysUser) {
  dialog.isEdit = true
  dialog.editingId = row.id
  Object.assign(form, {
    username: row.username,
    password: '',
    real_name: row.real_name || '',
    phone: row.phone || '',
    role_ids: [...row.role_ids],
    status: row.status,
  })
  dialog.visible = true
}

async function onSubmit() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) return
  saving.value = true
  try {
    if (dialog.isEdit) {
      await updateUserApi(dialog.editingId, {
        real_name: form.real_name,
        phone: form.phone,
        role_ids: form.role_ids,
        status: form.status,
      })
      ElMessage.success('修改成功')
    } else {
      await createUserApi({ ...form })
      ElMessage.success('新增成功')
    }
    dialog.visible = false
    loadList()
  } finally { saving.value = false }
}

async function onDelete(row: SysUser) {
  try {
    await ElMessageBox.confirm(`确定删除用户"${row.username}"？`, '提示', { type: 'warning' })
  } catch { return }
  await deleteUserApi(row.id)
  ElMessage.success('删除成功')
  loadList()
}

async function onResetPwd(row: SysUser) {
  try {
    const { value } = await ElMessageBox.prompt(
      `为用户"${row.username}"设置新密码（至少 6 位）`,
      '重置密码',
      { inputType: 'password', inputValidator: (v) => v.length >= 6 || '密码至少 6 位' },
    )
    await resetPasswordApi(row.id, value)
    ElMessage.success('密码已重置')
  } catch { /* 取消 */ }
}

onMounted(() => { loadList(); loadRoles() })
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #0f2a4a; }
.page-sub { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 4px; }
.filter-card :deep(.el-card__body) { padding: 12px 16px; }
.filter-bar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.table-footer { padding-top: 12px; font-size: 12px; color: #94a3b8; }
</style>