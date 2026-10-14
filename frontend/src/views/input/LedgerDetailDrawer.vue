<template>
  <el-drawer
    :model-value="modelValue"
    size="880px"
    :with-header="false"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="d-header">
      <div class="d-title">
        <el-icon color="#2563eb"><Document /></el-icon>
        <b>台账详情</b>
        <span v-if="row" class="d-sub">{{ row.project_name }} / {{ row.supplier_name }}</span>
      </div>
      <el-button link @click="emit('update:modelValue', false)">
        <el-icon :size="18"><Close /></el-icon>
      </el-button>
    </div>

    <div class="d-body" v-loading="loading">
      <template v-if="row">
        <div class="section-title">基本信息</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="期间">{{ row.period || '—' }}</el-descriptions-item>
          <el-descriptions-item label="合同主体">{{ row.contract_entity || '—' }}</el-descriptions-item>
          <el-descriptions-item label="管理类型">{{ row.management_type || '—' }}</el-descriptions-item>
          <el-descriptions-item label="供应类别">{{ row.supply_category || '—' }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">项目信息</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="项目">{{ row.project_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="项目类别">{{ row.project_category || '—' }}</el-descriptions-item>
          <el-descriptions-item label="项目状态">{{ row.project_status || '—' }}</el-descriptions-item>
          <el-descriptions-item label="子分公司">{{ row.subsidiary_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="项目地址" :span="2">{{ row.project_address || '—' }}</el-descriptions-item>
        </el-descriptions>

        <div class="section-title">供应商信息</div>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="供应商">{{ row.supplier_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="采购方式">{{ row.procurement_method || '—' }}</el-descriptions-item>
          <el-descriptions-item label="是否厂商">{{ row.is_manufacturer === 1 ? '厂商' : '非厂商' }}</el-descriptions-item>
          <el-descriptions-item label="物资种类">{{ row.material_category || '—' }}</el-descriptions-item>
          <el-descriptions-item label="付款模式">{{ row.payment_mode || '—' }}</el-descriptions-item>
          <el-descriptions-item label="债务分级">
            <el-tag :type="gradeTagColor(row.debt_grade)" effect="light">{{ row.debt_grade || '—' }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="既有风险类别" :span="2">
            <el-tag v-if="row.existing_risk_category" type="danger" effect="light">{{ row.existing_risk_category }}</el-tag>
            <span v-else>—</span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="section-title">本月采供</div>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="采购数量">{{ fmt(row.monthly_purchase_quantity) }}</el-descriptions-item>
          <el-descriptions-item label="采购金额">{{ fmt(row.monthly_purchase_amount) }}</el-descriptions-item>
          <el-descriptions-item label="实际支付">{{ fmt(row.monthly_purchase_actual_payment) }}</el-descriptions-item>
          <el-descriptions-item label="供应数量">{{ fmt(row.monthly_supply_quantity) }}</el-descriptions-item>
          <el-descriptions-item label="供应金额">{{ fmt(row.monthly_supply_amount) }}</el-descriptions-item>
          <el-descriptions-item label="实际回款">{{ fmt(row.monthly_supply_actual_collection) }}</el-descriptions-item>
          <el-descriptions-item label="利润/管理费" :span="3">
            <span class="up">{{ fmt(row.profit_management_fee) }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="section-title">上游债务</div>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="总债务金额">
            <span class="dn">{{ fmt(row.upstream_debt_total_amount) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="到期应付">{{ fmt(row.upstream_debt_due_payable) }}</el-descriptions-item>
          <el-descriptions-item label="预付款余额">{{ fmt(row.upstream_debt_prepayment_balance) }}</el-descriptions-item>
          <el-descriptions-item label="逾期3月以下">{{ fmt(row.upstream_debt_overdue_within_3m) }}</el-descriptions-item>
          <el-descriptions-item label="逾期3-6月">{{ fmt(row.upstream_debt_overdue_3_6m) }}</el-descriptions-item>
          <el-descriptions-item label="逾期6-12月">{{ fmt(row.upstream_debt_overdue_6_12m) }}</el-descriptions-item>
          <el-descriptions-item label="逾期1年以上">{{ fmt(row.upstream_debt_overdue_over_1y) }}</el-descriptions-item>
          <el-descriptions-item label="最长逾期天数" :span="2">
            <el-tag v-if="(row.upstream_debt_max_overdue_days || 0) > 0" type="danger">
              {{ row.upstream_debt_max_overdue_days }} 天
            </el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="section-title">下游债权</div>
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="应收债权">{{ fmt(row.downstream_receivable_amount) }}</el-descriptions-item>
          <el-descriptions-item label="逾期债权合计">
            <span class="dn">{{ fmt(row.downstream_overdue_receivable_total) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="预付款余额">{{ fmt(row.downstream_receivable_prepayment_balance) }}</el-descriptions-item>
          <el-descriptions-item label="逾期3月以下">{{ fmt(row.downstream_overdue_receivable_within_3m) }}</el-descriptions-item>
          <el-descriptions-item label="逾期3-6月">{{ fmt(row.downstream_overdue_receivable_3_6m) }}</el-descriptions-item>
          <el-descriptions-item label="逾期6-12月">{{ fmt(row.downstream_overdue_receivable_6_12m) }}</el-descriptions-item>
          <el-descriptions-item label="逾期1年以上">{{ fmt(row.downstream_overdue_receivable_over_1y) }}</el-descriptions-item>
          <el-descriptions-item label="最长逾期天数" :span="2">
            <el-tag v-if="(row.downstream_max_overdue_days || 0) > 0" type="danger">
              {{ row.downstream_max_overdue_days }} 天
            </el-tag>
            <el-tag v-else type="success">正常</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </template>

      <div v-else-if="!loading" class="empty">
        <el-icon :size="32" style="opacity:.3"><Document /></el-icon>
        <div style="margin-top:10px;color:#94a3b8">未找到数据</div>
      </div>
    </div>

    <div class="d-footer">
      <el-button @click="emit('update:modelValue', false)">关闭</el-button>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Document, Close } from '@element-plus/icons-vue'
import { getLedgerApi, type Ledger } from '@/api/ledger'

const props = defineProps<{ modelValue: boolean; ledgerId: number }>()
const emit = defineEmits<{ 'update:modelValue': [boolean] }>()

const row = ref<Ledger | null>(null)
const loading = ref(false)

function fmt(v?: number) {
  if (v === undefined || v === null) return '—'
  return Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function gradeTagColor(g?: string) {
  const map: Record<string, string> = {
    高风险: 'danger', 中风险: 'warning', 低风险: 'success',
    战略: 'primary', 既有: 'danger', 保供: 'info',
  }
  return (g && map[g]) || 'info'
}

async function loadDetail() {
  if (!props.ledgerId) { row.value = null; return }
  loading.value = true
  try {
    row.value = await getLedgerApi(props.ledgerId)
  } catch {
    row.value = null
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.modelValue, props.ledgerId] as const,
  ([visible]) => { if (visible) loadDetail() },
)
</script>

<style scoped>
.d-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #e5e7eb; }
.d-title { display: flex; align-items: center; gap: 8px; font-size: 15px; }
.d-title b { font-weight: 600; color: #0f2a4a; }
.d-sub { color: #94a3b8; font-size: 12px; font-weight: 400; }
.d-body { padding: 20px; overflow-y: auto; flex: 1; }
.d-footer { padding: 12px 20px; border-top: 1px solid #e5e7eb; display: flex; justify-content: flex-end; }

.section-title {
  font-size: 13px; font-weight: 600; color: #0f2a4a;
  padding-left: 8px; border-left: 3px solid #2563eb;
  margin: 20px 0 12px;
}
.section-title:first-child { margin-top: 0; }

.empty { text-align: center; padding: 60px 0; }

.up { color: #16a34a; font-weight: 500; }
.dn { color: #e5484d; font-weight: 500; }
</style>