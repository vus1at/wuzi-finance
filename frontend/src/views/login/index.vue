<template>
  <div class="login-mask">
    <div class="login-box">
      <div class="login-logo">
        <i class="fas fa-cubes"></i>
      </div>
      <h1>物资公司财务管理系统</h1>
      <div class="login-sub">大表导入 · 一键出报表 · 数据驾驶舱</div>

      <div class="login-form" @keyup.enter="onSubmit">
        <div v-if="errorMsg" class="login-err">{{ errorMsg }}</div>

        <div class="lf">
          <i class="fas fa-user"></i>
          <input v-model="form.username" placeholder="请输入用户名" />
        </div>

        <div class="lf">
          <i class="fas fa-lock"></i>
          <input v-model="form.password" type="password" placeholder="请输入密码" />
        </div>

        <div class="login-opt">
          <label><input type="checkbox" v-model="remember" /> 记住我</label>
          <span class="lk" @click="onForget">忘记密码？</span>
        </div>

        <button class="login-btn" :disabled="loading" @click="onSubmit">
          {{ loading ? '登录中...' : '登 录' }}
        </button>

        <div class="login-hint">演示账号：admin / 123456</div>
      </div>
    </div>
    <div class="login-footer">物资公司财务管理系统 · v1.0</div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const form = reactive({ username: 'admin', password: '123456' })
const remember = ref(true)
const loading = ref(false)
const errorMsg = ref('')

const store = useUserStore()
const router = useRouter()
const route = useRoute()

async function onSubmit() {
  errorMsg.value = ''
  if (!form.username.trim() || !form.password.trim()) {
    errorMsg.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  try {
    await store.login({ username: form.username.trim(), password: form.password.trim() })
    ElMessage.success('登录成功')
    router.replace((route.query.redirect as string) || '/dashboard')
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '登录失败，请重试'
  } finally {
    loading.value = false
  }
}

function onForget() {
  alert('请联系管理员重置密码')
}
</script>

<style scoped>
/* ============ 背景遮罩 ============ */
.login-mask {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: linear-gradient(135deg, #0f2a4a 0%, #1b3a5f 50%, #2563eb 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  font-weight: 500;
}

.login-mask::after {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  top: -200px;
  right: -100px;
  pointer-events: none;
}
.login-mask::before {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  bottom: -150px;
  left: -80px;
  pointer-events: none;
}

/* ============ 卡片 ============ */
.login-box {
  position: relative;
  z-index: 2;
  width: 420px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.3);
  padding: 36px 36px 30px;
  text-align: center;
}

.login-logo {
  width: 56px;
  height: 56px;
  margin: 0 auto 14px;
  border-radius: 14px;
  background: linear-gradient(135deg, #2563eb, #0ea5e9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 26px;
}

.login-box h1 {
  font-size: 23px;
  color: #0f2a4a;
  font-weight: 800;   /* ⭐ 加粗到 800 */
  letter-spacing: 1px;
}

.login-sub {
  font-size: 12px;
  color: #94a3b8;
  margin: 6px 0 22px;
  font-weight: 500;   /* ⭐ 400 → 500 */
}

/* ============ 表单 ============ */
.login-form {
  text-align: left;
}

.lf {
  position: relative;
  margin-bottom: 14px;
}
.lf i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 13px;
  z-index: 2;
}
.lf input {
  width: 100%;
  height: 40px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 0 12px 0 36px;
  font-size: 14px;
  background: #f9fafb;
  transition: 0.15s;
  font-family: inherit;
  color: #1e293b;
  font-weight: 500;
  box-sizing: border-box;
}
.lf input:focus {
  outline: none;
  border-color: #2563eb;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}
.lf input::placeholder {
  color: #9ca3af;
  font-weight: 400;   /* placeholder 保持细一点，视觉更清爽 */
}

/* 记住我 + 忘记密码 */
.login-opt {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #475569;
  margin-bottom: 18px;
  font-weight: 500;   /* ⭐ 400 → 500 */
}
.login-opt label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  user-select: none;
}
.login-opt input[type='checkbox'] {
  accent-color: #2563eb;
  cursor: pointer;
  width: 14px;
  height: 14px;
}
.lk {
  color: #2563eb;
  cursor: pointer;
  font-weight: 600;   /* ⭐ 链接更重 */
}
.lk:hover {
  text-decoration: underline;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 44px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: #fff;
  font-size: 15px;
  font-weight: 700;   /* ⭐ 600 → 700 */
  letter-spacing: 6px;
  cursor: pointer;
  transition: 0.15s;
  font-family: inherit;
}
.login-btn:hover:not(:disabled) {
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4);
}
.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-hint {
  margin-top: 16px;
  text-align: center;
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;   /* ⭐ 400 → 500 */
}

/* 错误提示 */
.login-err {
  background: #fef2f2;
  color: #dc2626;
  font-size: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  border: 1px solid #fecaca;
  text-align: left;
  font-weight: 500;
}

/* 底部版权 */
.login-footer {
  position: relative;
  z-index: 2;
  margin-top: 18px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 1px;
  font-weight: 500;
}
</style>