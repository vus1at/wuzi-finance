<template>
  <div>
    <!-- 顶部 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><Menu /></el-icon>
        <span>菜单管理</span>
        <span class="page-sub">树形结构 · 支持新增/编辑/删除</span>
      </div>
      <div class="page-actions">
        <el-button type="primary" @click="openCreate(0)">
          <el-icon><Plus /></el-icon> 新增一级菜单
        </el-button>
      </div>
    </div>

    <!-- 树形表格 -->
    <el-card shadow="never">
      <el-table
        :data="tree"
        v-loading="loading"
        row-key="id"
        border
        default-expand-all
        :tree-props="{ children: 'children' }"
        style="width: 100%"
        :header-cell-style="{ background: '#f3f4f6', color: '#374151', fontWeight: 600 }"
      >
        <el-table-column prop="menu_name" label="菜单名称" min-width="180" />
        <el-table-column prop="icon" label="图标" width="100" align="center">
          <template #default="{ row }">
            <span style="font-size: 11px; color: #64748b">{{ row.icon || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="menu_type" label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="typeTagColor(row.menu_type)" effect="light" size="small">
              {{ typeName(row.menu_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="menu_code" label="权限编码" width="130" />
        <el-table-column prop="path" label="路由路径" min-width="160" />
        <el-table-column prop="sort_order" label="排序" width="70" align="center" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" effect="light" size="small">
              {{ row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.menu_type !== 3 && row.menu_type !== 4"
              link
              type="primary"
              @click="openCreate(row.id)"
            >
              新增子菜单
            </el-button>
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialog.visible"
      :title="dialog.isEdit ? '编辑菜单' : '新增菜单'"
      width="620px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="父菜单" prop="parent_id">
          <el-tree-select
            v-model="form.parent_id"
            :data="parentOptions"
            :props="{ label: 'menu_name', value: 'id', children: 'children' }"
            check-strictly
            :render-after-expand="false"
            placeholder="顶级菜单"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="菜单名称" prop="menu_name">
          <el-input v-model="form.menu_name" placeholder="如：看板统计" />
        </el-form-item>
        <el-form-item label="菜单类型" prop="menu_type">
          <el-radio-group v-model="form.menu_type">
            <el-radio :value="1">一级菜单（可点击）</el-radio>
            <el-radio :value="2">一级菜单（目录）</el-radio>
            <el-radio :value="3">二级菜单（页面）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="权限编码" prop="menu_code">
          <el-input v-model="form.menu_code" placeholder="如：dashboard（唯一标识）" />
        </el-form-item>
        <el-form-item label="路由路径" prop="path">
          <el-input v-model="form.path" placeholder="如：/dashboard" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="form.icon" placeholder="如：Odometer（Element Plus 图标名）" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" style="width: 140px" />
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
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Menu, Plus } from '@element-plus/icons-vue'
import {
  getMenuTreeApi, createMenuApi, updateMenuApi, deleteMenuApi, type Menu as MenuType,
} from '@/api/sys-menu'

const tree = ref<MenuType[]>([])
const loading = ref(false)
const saving = ref(false)

const dialog = reactive({ visible: false, isEdit: false, editingId: 0 })
const formRef = ref<FormInstance>()
const form = reactive({
  parent_id: 0 as number | null,
  menu_name: '',
  menu_code: '',
  path: '',
  component: '',
  icon: '',
  menu_type: 1,
  sort_order: 0,
  status: 1,
})

const rules: FormRules = {
  menu_name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
}

// 父菜单下拉选项：加一个虚拟的"顶级"
const parentOptions = computed(() => [
  { id: 0, menu_name: '顶级菜单', children: [] as any[] },
  ...tree.value,
])

function typeName(t: number) {
  return { 1: '一级-可点击', 2: '一级-目录', 3: '二级-页面', 4: '按钮权限' }[t] || '未知'
}
function typeTagColor(t: number) {
  return { 1: 'primary', 2: 'warning', 3: 'success', 4: 'info' }[t] || 'info'
}

async function loadTree() {
  loading.value = true
  try {
    tree.value = await getMenuTreeApi()
  } finally {
    loading.value = false
  }
}

function openCreate(parentId: number) {
  dialog.isEdit = false
  dialog.editingId = 0
  Object.assign(form, {
    parent_id: parentId,
    menu_name: '',
    menu_code: '',
    path: '',
    component: '',
    icon: '',
    menu_type: parentId === 0 ? 1 : 3,
    sort_order: 0,
    status: 1,
  })
  dialog.visible = true
}

function openEdit(row: MenuType) {
  dialog.isEdit = true
  dialog.editingId = row.id
  Object.assign(form, {
    parent_id: row.parent_id,
    menu_name: row.menu_name,
    menu_code: row.menu_code || '',
    path: row.path || '',
    component: row.component || '',
    icon: row.icon || '',
    menu_type: row.menu_type,
    sort_order: row.sort_order,
    status: row.status,
  })
  dialog.visible = true
}

async function onSubmit() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) return
  saving.value = true
  try {
    const payload = { ...form, parent_id: form.parent_id ?? 0 }
    if (dialog.isEdit) {
      await updateMenuApi(dialog.editingId, payload)
      ElMessage.success('修改成功')
    } else {
      await createMenuApi(payload)
      ElMessage.success('新增成功')
    }
    dialog.visible = false
    loadTree()
  } finally {
    saving.value = false
  }
}

async function onDelete(row: MenuType) {
  try {
    await ElMessageBox.confirm(`确定删除菜单"${row.menu_name}"？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await deleteMenuApi(row.id)
    ElMessage.success('删除成功')
    loadTree()
  } catch (e: any) {
    // 后端返回"请先删除子菜单"时，这里不用额外处理（拦截器已弹提示）
  }
}

onMounted(loadTree)
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
</style>