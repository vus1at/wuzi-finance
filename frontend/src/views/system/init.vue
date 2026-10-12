<template>
  <div>
    <!-- 顶部 -->
    <div class="page-header">
      <div class="page-title">
        <el-icon color="#2563eb"><Upload /></el-icon>
        <span>期初数据初始化</span>
        <span class="page-sub">首次上线需填写 · 后续系统自动累加</span>
      </div>
      <div class="page-actions">
        <el-button type="primary" :loading="saving" @click="onSave">
          <el-icon><Check /></el-icon> 保存
        </el-button>
      </div>
    </div>

    <!-- 说明 -->
    <div class="info-box">
      <b>说明</b>：「年累」和「开累」数据依赖年初至今的历史累计值。
      <br>首次上线需填写下方期初值，后续每月填报时系统自动累加。
      <br>⚠️ 期初数据的准确性直接影响年累/开累计算，请与财务部门确认后填写。
    </div>

    <el-card shadow="never" v-loading="loading">
      <!-- 年累分组 -->
      <div class="section-title">年累数据（截至上月底）</div>
      <div class="form-grid">
        <div class="form-item">
          <div class="label">年累采购金额（万）</div>
          <el-input-number
            v-model="form.ytd_purchase_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">年累供应金额（万）</div>
          <el-input-number
            v-model="form.ytd_supply_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">年累支付金额（万）</div>
          <el-input-number
            v-model="form.ytd_payment_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">年累回款金额（万）</div>
          <el-input-number
            v-model="form.ytd_receipt_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">年累利润（万）</div>
          <el-input-number
            v-model="form.ytd_profit_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">年累供应数量</div>
          <el-input-number
            v-model="form.ytd_supply_quantity"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
      </div>

      <!-- 开累分组 -->
      <div class="section-title">开累数据（全部历史）</div>
      <div class="form-grid">
        <div class="form-item">
          <div class="label">开累采购金额（万）</div>
          <el-input-number
            v-model="form.cum_purchase_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">开累供应金额（万）</div>
          <el-input-number
            v-model="form.cum_supply_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">开累付款金额（万）</div>
          <el-input-number
            v-model="form.cum_payment_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">开累回款金额（万）</div>
          <el-input-number
            v-model="form.cum_receipt_amount"
            :min="0"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">开累付款比例（%）</div>
          <el-input-number
            v-model="form.cum_payment_ratio"
            :min="0"
            :max="100"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
        <div class="form-item">
          <div class="label">开累回款比例（%）</div>
          <el-input-number
            v-model="form.cum_receipt_ratio"
            :min="0"
            :max="100"
            :precision="2"
            :controls="false"
            placeholder="请输入"
            style="width: 100%"
          />
        </div>
      </div>

      <div class="update-tip" v-if="form.updated_at">
        上次保存时间：{{ formatTime(form.updated_at) }}
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Check } from '@element-plus/icons-vue'
import {
  getInitialBalanceApi,
  updateInitialBalanceApi,
  type InitialBalance,
} from '@/api/sys-initial-balance'

const loading = ref(false)
const saving = ref(false)

const form = reactive<Omit<InitialBalance, 'id'> & { id?: number }>({
  ytd_purchase_amount: 0,
  ytd_supply_amount: 0,
  ytd_payment_amount: 0,
  ytd_receipt_amount: 0,
  ytd_profit_amount: 0,
  ytd_supply_quantity: 0,
  cum_purchase_amount: 0,
  cum_supply_amount: 0,
  cum_payment_amount: 0,
  cum_receipt_amount: 0,
  cum_payment_ratio: 0,
  cum_receipt_ratio: 0,
  updated_at: '',
})

function formatTime(t: string) {
  return t ? new Date(t).toLocaleString('zh-CN') : ''
}

async function loadData() {
  loading.value = true
  try {
    const data = await getInitialBalanceApi()
    Object.assign(form, data)
  } finally {
    loading.value = false
  }
}

async function onSave() {
  saving.value = true
  try {
    const payload = { ...form }
    delete (payload as any).id
    delete (payload as any).updated_at
    const res = await updateInitialBalanceApi(payload as any)
    Object.assign(form, res)
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
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

.info-box {
  background: #f0f7ff;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 14px;
  font-size: 12px;
  color: #1e40af;
  line-height: 1.8;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f2a4a;
  padding-left: 8px;
  border-left: 3px solid #2563eb;
  margin: 20px 0 14px;
}
.section-title:first-child {
  margin-top: 0;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.form-item .label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
  font-weight: 500;
}

.update-tip {
  margin-top: 20px;
  font-size: 11px;
  color: #94a3b8;
  text-align: right;
}
</style>