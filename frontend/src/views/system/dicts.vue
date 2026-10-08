<template>
  <div>
    <!-- 顶部标题 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><List /></el-icon>
        <span>字典管理</span>
        <span class="page-sub">系统下拉选项统一维护 · 共 {{ dicts.length }} 个字典</span>
      </div>
    </div>

    <!-- 说明 -->
    <div class="info-box">
      <b>什么是字典管理？</b>字典是系统中所有下拉选项的"数据源头"，如"管理类型""采购方式""物资种类"等。
      <br>在字典管理中修改选项后，<b>数据填报等模块的下拉选择将同步更新</b>。
    </div>

    <!-- 字典卡片网格 -->
    <div class="dict-grid" v-loading="loading">
      <div
        v-for="d in dicts"
        :key="d.key"
        class="dict-card"
        @click="openEdit(d)"
      >
        <div class="card-header">
          <div class="card-title">
            <el-icon color="#2563eb" :size="12"><CaretRight /></el-icon>
            <span>{{ d.label }}</span>
          </div>
          <div class="card-tag">
            {{ d.group }} · {{ d.items.length }}项
            <el-icon :size="10" style="margin-left: 4px"><EditPen /></el-icon>
          </div>
        </div>
        <div class="card-desc">{{ d.desc }}</div>
        <div class="card-items">
          <span v-for="item in d.items" :key="item" class="item-chip">{{ item }}</span>
        </div>
        <div class="card-footer">
          <el-button link type="primary" size="small" @click.stop="openEdit(d)">
            <el-icon><EditPen /></el-icon> 编辑此项
          </el-button>
        </div>
      </div>
    </div>

    <!-- 编辑抽屉 -->
    <el-drawer v-model="drawer.visible" size="560px" :with-header="false">
      <div class="d-header">
        <div class="d-title">
          <el-icon color="#2563eb"><EditPen /></el-icon>
          <b>编辑字典：{{ drawer.label }}</b>
          <span class="d-sub">{{ editItems.length }}项</span>
        </div>
        <el-button link @click="drawer.visible = false">
          <el-icon :size="18"><Close /></el-icon>
        </el-button>
      </div>

      <div class="d-body">
        <div class="d-hint">点击「编辑」修改选项值，点 ✕ 删除，点「+ 新增项」添加新选项。</div>

        <div v-for="(item, i) in editItems" :key="i" class="d-item-row">
          <span class="d-item-no">{{ i + 1 }}</span>
          <el-input v-model="editItems[i]" placeholder="输入选项值" />
          <el-button link type="danger" @click="removeItem(i)">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>

        <div class="d-add-row">
          <el-button link type="primary" @click="addItem">
            <el-icon><Plus /></el-icon> 新增项
          </el-button>
        </div>
      </div>

      <div class="d-footer">
        <el-button @click="drawer.visible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">
          <el-icon><Check /></el-icon> 保存字典
        </el-button>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  List, CaretRight, EditPen, Close, Plus, Check,
} from '@element-plus/icons-vue'
import { listDictsApi, updateDictApi, type DictData } from '@/api/dict'

const dicts = ref<DictData[]>([])
const loading = ref(false)
const saving = ref(false)

const drawer = reactive({
  visible: false,
  key: '',
  label: '',
})
const editItems = ref<string[]>([])

async function loadDicts() {
  loading.value = true
  try {
    dicts.value = await listDictsApi()
  } finally {
    loading.value = false
  }
}

function openEdit(d: DictData) {
  drawer.key = d.key
  drawer.label = d.label
  editItems.value = [...d.items]
  drawer.visible = true
}

function addItem() {
  editItems.value.push('')
}

function removeItem(i: number) {
  editItems.value.splice(i, 1)
}

async function onSave() {
  // 清洗：去空、去重
  const cleaned: string[] = []
  const seen = new Set<string>()
  for (const item of editItems.value) {
    const v = (item || '').trim()
    if (v && !seen.has(v)) {
      seen.add(v)
      cleaned.push(v)
    }
  }
  if (cleaned.length === 0) {
    ElMessage.warning('字典至少保留 1 项有效值')
    return
  }
  saving.value = true
  try {
    await updateDictApi(drawer.key, cleaned)
    ElMessage.success('保存成功')
    drawer.visible = false
    loadDicts()
  } finally {
    saving.value = false
  }
}

onMounted(loadDicts)
</script>

<style scoped>
.page-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
.page-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 16px; font-weight: 700; color: #0f2a4a;
}
.page-sub { font-size: 12px; color: #94a3b8; font-weight: 400; margin-left: 4px; }

.info-box {
  background: #f0f7ff;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 14px;
  font-size: 12px;
  color: #1e40af;
  line-height: 1.7;
}

.dict-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.dict-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px 16px;
  cursor: pointer;
  transition: 0.15s;
}
.dict-card:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.card-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  font-weight: 600;
  color: #0f2a4a;
}
.card-tag {
  font-size: 10px;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
}

.card-desc {
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 10px;
}

.card-items {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.item-chip {
  padding: 2px 8px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 11px;
  color: #374151;
}

.card-footer {
  text-align: right;
  margin-top: 6px;
}

/* 抽屉 */
.d-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
}
.d-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
}
.d-title b { font-weight: 600; color: #0f2a4a; }
.d-sub { color: #94a3b8; font-size: 12px; font-weight: 400; }

.d-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}
.d-hint {
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 14px;
  background: #f9fafb;
  padding: 8px 12px;
  border-radius: 6px;
}

.d-item-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.d-item-no {
  min-width: 24px;
  font-size: 11px;
  color: #94a3b8;
  text-align: right;
}

.d-add-row {
  margin-top: 12px;
  text-align: left;
}

.d-footer {
  padding: 12px 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>