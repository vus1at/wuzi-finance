<template>
  <div>
    <!-- 顶部 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><UserFilled /></el-icon>
        <span>角色管理</span>
        <span class="page-sub">{{ list.length }}个角色 · 支持菜单权限分配</span>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon> 新增角色
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-card shadow="never">
      <el-table
        :data="list"
        v-loading="loading"
        border
        style="width: 100%"
        :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }"
      >
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="role_name" label="角色名称" width="140" />
        <el-table-column prop="role_code" label="角色编码" width="130">
          <template #default="{ row }">
            <el-tag type="info" effect="plain">{{ row.role_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="220" show-overflow-tooltip />
        <el-table-column label="操作" width="260" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openPermission(row)">菜单权限</el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button
              link
              type="danger"
              :disabled="isBuiltin(row)"
              @click="onDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="table-footer">共 {{ list.length }} 条</div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑角色' : '新增角色'"
      width="520px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="角色名称" prop="role_name">
          <el-input v-model="form.role_name" placeholder="如：管理员" />
        </el-form-item>
        <el-form-item label="角色编码" prop="role_code">
          <el-input
            v-model="form.role_code"
            placeholder="如：ADMIN（大写英文）"
            :disabled="isEditBuiltin"
          />
          <div v-if="isEditBuiltin" class="form-hint">内置角色编码不可修改</div>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSubmit">
          {{ dialog.isEdit ? '保存修改' : '确认新增' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 菜单权限抽屉 -->
    <el-drawer v-model="perm.visible" size="500px" :with-header="false">
      <div class="d-header">
        <div class="d-title">
          <el-icon color="#2563eb"><Menu /></el-icon>
          <b>菜单权限 · {{ perm.roleName }}</b>
          <span class="d-sub">{{ perm.roleCode }}</span>
        </div>
        <el-button link @click="perm.visible = false">
          <el-icon :size="18"><Close /></el-icon>
        </el-button>
      </div>

      <div class="d-body">
        <div class="d-hint">
          勾选该角色能看到的菜单。保存后，该角色的用户登录时会按此权限过滤菜单。
          <br><b>⚠️ ADMIN 角色会自动拥有全部菜单，不受此处限制。</b>
        </div>

        <el-tree
          ref="treeRef"
          :data="menuTree"
          show-checkbox
          node-key="id"
          :props="{ label: 'menu_name', children: 'children' }"
          :default-expand-all="true"
          style="margin-top: 12px"
        />
      </div>

      <div class="d-footer">
        <el-button @click="perm.visible = false">取消</el-button>
        <el-button type="primary" :loading="perm.saving" @click="onSavePermission">
          <el-icon><Check /></el-icon> 保存权限
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { UserFilled, Plus, Menu, Close, Check } from '@element-plus/icons-vue'
import {
  listRolesApi, createRoleApi, updateRoleApi, deleteRoleApi,
  getRoleMenusApi, setRoleMenusApi, type Role,
} from '@/api/sys-role'
import { getMenuTreeApi, type Menu as MenuType } from '@/api/sys-menu'

const BUILTIN = ['ADMIN', 'EDITOR', 'VIEWER']

function isBuiltin(row: Role) {
  return BUILTIN.includes(row.role_code)
}

const list = ref<Role[]>([])
const menuTree = ref<MenuType[]>([])
const loading = ref(false)
const saving = ref(false)

const dialog = reactive({ visible: false, isEdit: false, editingId: 0 })
const formRef = ref<FormInstance>()
const form = reactive({ role_name: '', role_code: '', description: '' })

const rules: FormRules = {
  role_name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  role_code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }],
}

const perm = reactive({
  visible: false,
  roleId: 0,
  roleName: '',
  roleCode: '',
  checkedIds: [] as number[],
  saving: false,
})
const treeRef = ref<any>()

// ⭐ 编辑内置角色时禁用 role_code 输入
const isEditBuiltin = computed(() => {
  if (!dialog.isEdit) return false
  const r = list.value.find((x) => x.id === dialog.editingId)
  return r ? BUILTIN.includes(r.role_code) : false
})

async function loadList() {
  loading.value = true
  try {
    list.value = await listRolesApi()
  } finally {
    loading.value = false
  }
}

async function loadMenuTree() {
  menuTree.value = await getMenuTreeApi()
}

function openCreate() {
  dialog.isEdit = false
  dialog.editingId = 0
  Object.assign(form, { role_name: '', role_code: '', description: '' })
  dialog.visible = true
}

function openEdit(row: Role) {
  dialog.isEdit = true
  dialog.editingId = row.id
  Object.assign(form, {
    role_name: row.role_name,
    role_code: row.role_code,
    description: row.description || '',
  })
  dialog.visible = true
}

async function onSubmit() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) return
  saving.value = true
  try {
    if (dialog.isEdit) {
      // 内置角色：不传 role_code（后端也会拦截）
      const payload = isEditBuiltin.value
        ? { role_name: form.role_name, description: form.description }
        : { ...form }
      await updateRoleApi(dialog.editingId, payload as any)
      ElMessage.success('修改成功')
    } else {
      await createRoleApi({ ...form })
      ElMessage.success('新增成功')
    }
    dialog.visible = false
    loadList()
  } finally {
    saving.value = false
  }
}

async function onDelete(row: Role) {
  try {
    await ElMessageBox.confirm(`确定删除角色"${row.role_name}"？`, '提示', { type: 'warning' })
  } catch { return }
  await deleteRoleApi(row.id)
  ElMessage.success('删除成功')
  loadList()
}

async function openPermission(row: Role) {
  perm.roleId = row.id
  perm.roleName = row.role_name
  perm.roleCode = row.role_code
  const res = await getRoleMenusApi(row.id)
  perm.checkedIds = res.menu_ids
  perm.visible = true
  // 等 DOM 加载后设置选中
  setTimeout(() => {
    treeRef.value?.setCheckedKeys(res.menu_ids)
  }, 100)
}

async function onSavePermission() {
  const checked = treeRef.value?.getCheckedKeys() || []
  // ⭐ 只保存完全勾选的，不保存半选父节点
  perm.saving = true
  try {
    await setRoleMenusApi(perm.roleId, checked)
    ElMessage.success('权限已保存')
    perm.visible = false
  } finally {
    perm.saving = false
  }
}

onMounted(() => {
  loadList()
  loadMenuTree()
})
</script>

<style scoped>
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.page-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 700; color: #0f2a4a; }
.page-sub { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 4px; }
.table-footer { padding-top: 12px; font-size: 12px; color: #94a3b8; }

.form-hint {
  font-size: 11px;
  color: #f59e0b;
  margin-top: 4px;
  line-height: 1.4;
}

.d-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #e5e7eb; }
.d-title { display: flex; align-items: center; gap: 8px; font-size: 15px; }
.d-title b { font-weight: 600; color: #0f2a4a; }
.d-sub { color: #94a3b8; font-size: 12px; font-weight: 400; }
.d-body { padding: 20px; overflow-y: auto; flex: 1; }
.d-hint { font-size: 12px; color: #64748b; background: #f0f7ff; padding: 10px 14px; border-radius: 6px; line-height: 1.7; }
.d-footer { padding: 12px 20px; border-top: 1px solid #e5e7eb; display: flex; justify-content: flex-end; gap: 8px; }
</style>