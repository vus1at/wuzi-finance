<template>
  <el-drawer
    :model-value="modelValue"
    size="900px"
    :with-header="false"
    :close-on-click-modal="false"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="d-header">
      <div class="d-title">
        <el-icon color="#2563eb"><EditPen /></el-icon>
        <b>{{ mode === 'create' ? '新增台账记录' : '编辑台账记录' }}</b>
        <span v-if="mode === 'edit'" class="d-sub">ID: {{ editId }}</span>
      </div>
      <el-button link @click="close">
        <el-icon :size="18"><Close /></el-icon>
      </el-button>
    </div>

    <div class="d-body">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-tabs v-model="activeTab">
          <!-- ========== Tab 1: 基本信息 & 项目 ========== -->
          <el-tab-pane label="基本信息" name="basic">
            <div class="section-title">基本信息</div>
            <div class="form-grid">
              <el-form-item label="合同主体" prop="contract_entity">
                <el-select v-model="form.contract_entity" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['物资分公司','恒源隧','华阳分公司']" :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
              <el-form-item label="管理类型" prop="management_type">
                <el-select v-model="form.management_type" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['A类材料厂','集采中心','收尾材料厂','华阳分公司']" :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
              <el-form-item label="供应类别" prop="supply_category">
                <el-select v-model="form.supply_category" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['区域集采','内供集采','三方供应','自产','外购']" :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
            </div>

            <div class="section-title">下游项目信息</div>
            <div class="form-grid">
              <el-form-item label="项目" prop="project_id">
                <el-select v-model="form.project_id" placeholder="请选择" filterable style="width:100%">
                  <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="项目类别">
                <el-select v-model="form.project_category" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['铁路','公路','市政','水利']" :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
              <el-form-item label="项目状态">
                <el-select v-model="form.project_status" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['在供','停供']" :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
              <el-form-item label="子分公司">
                <el-select v-model="form.subsidiary_id" placeholder="请选择" style="width:100%">
                  <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="项目地址">
                <el-input v-model="form.project_address" placeholder="如：云南大理" />
              </el-form-item>
            </div>
          </el-tab-pane>

          <!-- ========== Tab 2: 供应商 ========== -->
          <el-tab-pane label="供应商" name="supplier">
            <div class="section-title">上游供应商信息</div>
            <div class="form-grid">
              <el-form-item label="供应商" prop="supplier_id">
                <el-select v-model="form.supplier_id" placeholder="请选择" filterable style="width:100%">
                  <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
                </el-select>
              </el-form-item>
              <el-form-item label="采购方式">
                <el-select v-model="form.procurement_method" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['战略采购','框架采购','公开招标','公开谈判','线下谈判','询价采购','单一来源','鲁班商城','股份集采']"
                    :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
              <el-form-item label="是否厂商">
                <el-radio-group v-model="form.is_manufacturer">
                  <el-radio :value="1">厂商</el-radio>
                  <el-radio :value="0">非厂商</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="物资种类" prop="material_category">
                <el-select v-model="form.material_category" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['建材','型材','钢绞线','水泥','水泥运输','粉煤灰','外加剂','柴油','商砼','木材','防水材料','土工材料','槽道','管片','锚具','其他']"
                    :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
              <el-form-item label="付款模式">
                <el-select v-model="form.payment_mode" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['第四月付第一月80%','月结70%','月结80%','先款后货','预付款+尾款','季度结算','按月结算']"
                    :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
              <el-form-item label="债务分级" prop="debt_grade">
                <el-select v-model="form.debt_grade" placeholder="请选择" style="width:100%">
                  <el-option v-for="v in ['既有','战略','保供','低风险','中风险','高风险']" :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
              <el-form-item label="既有风险类别">
                <el-select v-model="form.existing_risk_category" placeholder="请选择" clearable style="width:100%">
                  <el-option v-for="v in ['两拖欠','诉讼']" :key="v" :label="v" :value="v" />
                </el-select>
              </el-form-item>
            </div>
          </el-tab-pane>

          <!-- ========== Tab 3: 本月采供 ========== -->
          <el-tab-pane label="本月采供" name="monthly">
            <div class="section-title">分期付款计划</div>
            <div class="form-grid">
              <el-form-item label="合计(万)">
                <el-input-number v-model="form.installment_plan_total" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="本月(万)">
                <el-input-number v-model="form.installment_plan_current_month" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="下月(万)">
                <el-input-number v-model="form.installment_plan_next_month" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
            </div>

            <div class="section-title">本月采购</div>
            <div class="form-grid">
              <el-form-item label="采购数量">
                <el-input-number v-model="form.monthly_purchase_quantity" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="采购金额(万)" prop="monthly_purchase_amount">
                <el-input-number v-model="form.monthly_purchase_amount" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="签认逾期费用">
                <el-input-number v-model="form.monthly_purchase_confirmed_overdue_fee" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="签认贴息费用">
                <el-input-number v-model="form.monthly_purchase_confirmed_interest_subsidy_fee" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="合计(万)">
                <el-input-number v-model="form.monthly_purchase_total" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="实际支付(万)">
                <el-input-number v-model="form.monthly_purchase_actual_payment" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="下月支付计划">
                <el-input-number v-model="form.next_month_payment_plan" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
            </div>

            <div class="section-title">本月供应</div>
            <div class="form-grid">
              <el-form-item label="供应数量">
                <el-input-number v-model="form.monthly_supply_quantity" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="供应金额(万)" prop="monthly_supply_amount">
                <el-input-number v-model="form.monthly_supply_amount" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="预付款供应金额">
                <el-input-number v-model="form.monthly_supply_prepayment_amount" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="签认逾期费用">
                <el-input-number v-model="form.monthly_supply_confirmed_overdue_fee" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="签认贴息费用">
                <el-input-number v-model="form.monthly_supply_confirmed_interest_subsidy_fee" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="合计(万)">
                <el-input-number v-model="form.monthly_supply_total" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="实际回款(万)">
                <el-input-number v-model="form.monthly_supply_actual_collection" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="利润/管理费(万)">
                <el-input-number v-model="form.profit_management_fee" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="下月供应计划">
                <el-input-number v-model="form.next_month_supply_plan" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="下月回款计划">
                <el-input-number v-model="form.next_month_collection_plan" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
            </div>
          </el-tab-pane>

          <!-- ========== Tab 4: 债务 & 债权 ========== -->
          <el-tab-pane label="债务债权" name="debt">
            <div class="section-title">上游债务</div>
            <div class="form-grid">
              <el-form-item label="预付款余额">
                <el-input-number v-model="form.upstream_debt_prepayment_balance" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="总债务金额(万)" prop="upstream_debt_total_amount">
                <el-input-number v-model="form.upstream_debt_total_amount" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="到期应付">
                <el-input-number v-model="form.upstream_debt_due_payable" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="预期债务合计">
                <el-input-number v-model="form.upstream_debt_expected_total" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期3月以下">
                <el-input-number v-model="form.upstream_debt_overdue_within_3m" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期3-6月">
                <el-input-number v-model="form.upstream_debt_overdue_3_6m" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期6-12月">
                <el-input-number v-model="form.upstream_debt_overdue_6_12m" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期1年以上">
                <el-input-number v-model="form.upstream_debt_overdue_over_1y" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="最长逾期天数">
                <el-input-number v-model="form.upstream_debt_max_overdue_days" :controls="false" :min="0" style="width:100%" />
              </el-form-item>
            </div>

            <div class="section-title">下游债权</div>
            <div class="form-grid">
              <el-form-item label="预付款余额">
                <el-input-number v-model="form.downstream_receivable_prepayment_balance" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="应收债权">
                <el-input-number v-model="form.downstream_receivable_amount" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期债权合计">
                <el-input-number v-model="form.downstream_overdue_receivable_total" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期3月以下">
                <el-input-number v-model="form.downstream_overdue_receivable_within_3m" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期3-6月">
                <el-input-number v-model="form.downstream_overdue_receivable_3_6m" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期6-12月">
                <el-input-number v-model="form.downstream_overdue_receivable_6_12m" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="逾期1年以上">
                <el-input-number v-model="form.downstream_overdue_receivable_over_1y" :controls="false" :precision="2" style="width:100%" />
              </el-form-item>
              <el-form-item label="最长逾期天数">
                <el-input-number v-model="form.downstream_max_overdue_days" :controls="false" :min="0" style="width:100%" />
              </el-form-item>
            </div>

            <div class="section-title">期间</div>
            <div class="form-grid">
              <el-form-item label="期间">
                <el-select v-model="form.period" placeholder="请选择" style="width:100%">
                  <el-option label="2026年9月" value="2026-09" />
                  <el-option label="2026年8月" value="2026-08" />
                </el-select>
              </el-form-item>
              <el-form-item label="单据日期">
                <el-date-picker v-model="form.document_date" type="date" format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD" style="width:100%" />
              </el-form-item>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </div>

    <div class="d-footer">
      <el-button @click="close">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSubmit">
        <el-icon><Check /></el-icon> {{ mode === 'create' ? '确认新增' : '保存修改' }}
      </el-button>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { EditPen, Close, Check } from '@element-plus/icons-vue'
import {
  getLedgerApi, createLedgerApi, updateLedgerApi, type Ledger,
} from '@/api/ledger'
import request from '@/utils/request'

const props = defineProps<{
  modelValue: boolean
  mode: 'create' | 'edit'
  editId: number
  projects: { id: number; name: string }[]
  suppliers: { id: number; name: string }[]
}>()
const emit = defineEmits<{ 'update:modelValue': [boolean]; saved: [] }>()

interface Dept { id: number; name: string }
const departments = ref<Dept[]>([])

const formRef = ref<FormInstance>()
const saving = ref(false)
const activeTab = ref('basic')

function emptyForm() {
  return {
    period: '2026-09',
    contract_entity: '物资分公司',
    management_type: 'A类材料厂',
    supply_category: '内供集采',
    project_id: undefined as number | undefined,
    project_category: '铁路',
    project_status: '在供',
    subsidiary_id: undefined as number | undefined,
    project_address: '',
    supplier_id: undefined as number | undefined,
    procurement_method: '公开招标',
    is_manufacturer: 1,
    material_category: '',
    payment_mode: '按月结算',
    debt_grade: '低风险',
    existing_risk_category: '',
    installment_plan_total: 0,
    installment_plan_current_month: 0,
    installment_plan_next_month: 0,
    monthly_purchase_quantity: 0,
    monthly_purchase_amount: 0,
    monthly_purchase_confirmed_overdue_fee: 0,
    monthly_purchase_confirmed_interest_subsidy_fee: 0,
    monthly_purchase_total: 0,
    monthly_purchase_actual_payment: 0,
    next_month_payment_plan: 0,
    monthly_supply_quantity: 0,
    monthly_supply_amount: 0,
    monthly_supply_prepayment_amount: 0,
    monthly_supply_confirmed_overdue_fee: 0,
    monthly_supply_confirmed_interest_subsidy_fee: 0,
    monthly_supply_total: 0,
    monthly_supply_actual_collection: 0,
    profit_management_fee: 0,
    next_month_supply_plan: 0,
    next_month_collection_plan: 0,
    upstream_debt_prepayment_balance: 0,
    upstream_debt_total_amount: 0,
    upstream_debt_due_payable: 0,
    upstream_debt_expected_total: 0,
    upstream_debt_overdue_within_3m: 0,
    upstream_debt_overdue_3_6m: 0,
    upstream_debt_overdue_6_12m: 0,
    upstream_debt_overdue_over_1y: 0,
    upstream_debt_max_overdue_days: 0,
    downstream_receivable_prepayment_balance: 0,
    downstream_receivable_amount: 0,
    downstream_overdue_receivable_total: 0,
    downstream_overdue_receivable_within_3m: 0,
    downstream_overdue_receivable_3_6m: 0,
    downstream_overdue_receivable_6_12m: 0,
    downstream_overdue_receivable_over_1y: 0,
    downstream_max_overdue_days: 0,
    document_date: '',
  }
}

const form = reactive(emptyForm())

const rules: FormRules = {
  contract_entity: [{ required: true, message: '请选择合同主体', trigger: 'change' }],
  management_type: [{ required: true, message: '请选择管理类型', trigger: 'change' }],
  supply_category: [{ required: true, message: '请选择供应类别', trigger: 'change' }],
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  material_category: [{ required: true, message: '请选择物资种类', trigger: 'change' }],
  debt_grade: [{ required: true, message: '请选择债务分级', trigger: 'change' }],
  monthly_purchase_amount: [{ required: true, message: '请填采购金额', trigger: 'blur' }],
  monthly_supply_amount: [{ required: true, message: '请填供应金额', trigger: 'blur' }],
  upstream_debt_total_amount: [{ required: true, message: '请填总债务金额', trigger: 'blur' }],
}

async function loadDepartments() {
  try {
    departments.value = await request.get<any, Dept[]>('/projects/meta/departments')
  } catch { departments.value = [] }
}

async function loadDetail() {
  if (props.mode !== 'edit' || !props.editId) return
  const row = await getLedgerApi(props.editId)
  Object.assign(form, emptyForm(), row)
}

function close() {
  emit('update:modelValue', false)
}

async function onSubmit() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) {
    ElMessage.warning('请检查必填项')
    return
  }
  saving.value = true
  try {
    const payload = { ...form } as Partial<Ledger>

    const proj = props.projects.find((p) => p.id === form.project_id)
    if (proj) payload.project_name = proj.name

    const sup = props.suppliers.find((s) => s.id === form.supplier_id)
    if (sup) payload.supplier_name = sup.name

    const dept = departments.value.find((d) => d.id === form.subsidiary_id)
    if (dept) payload.subsidiary_name = dept.name

    if (props.mode === 'edit') {
      await updateLedgerApi(props.editId, payload)
      ElMessage.success('修改成功')
    } else {
      await createLedgerApi(payload)
      ElMessage.success('新增成功')
    }
    emit('saved')
    close()
  } finally {
    saving.value = false
  }
}

watch(
  () => props.modelValue,
  (v) => {
    if (v) {
      Object.assign(form, emptyForm())
      activeTab.value = 'basic'
      if (props.mode === 'edit') loadDetail()
    }
  }
)

onMounted(loadDepartments)
</script>

<style scoped>
.d-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #e5e7eb; }
.d-title { display: flex; align-items: center; gap: 8px; font-size: 15px; }
.d-title b { font-weight: 600; color: #0f2a4a; }
.d-sub { color: #94a3b8; font-size: 12px; font-weight: 400; }
.d-body { padding: 20px; overflow-y: auto; flex: 1; }
.d-footer { padding: 12px 20px; border-top: 1px solid #e5e7eb; display: flex; justify-content: flex-end; gap: 8px; }

.section-title {
  font-size: 13px; font-weight: 600; color: #0f2a4a;
  padding-left: 8px; border-left: 3px solid #2563eb;
  margin: 16px 0 12px;
}
.section-title:first-child { margin-top: 0; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0 20px;
}
</style>