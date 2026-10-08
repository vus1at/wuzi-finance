<template>
  <el-container style="height: 100vh">
    <el-aside width="210px" class="sidebar">
      <div class="logo">
        <el-icon><Box /></el-icon>
        <span>物资财务</span>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        background-color="#0f2a4a"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#fff"
        class="side-menu"
      >
        <el-menu-item-group title="核心功能">
          <el-menu-item index="/dashboard">
            <el-icon><Odometer /></el-icon><span>看板统计</span>
          </el-menu-item>
          <el-menu-item index="/input">
            <el-icon><Upload /></el-icon><span>数据填报</span>
          </el-menu-item>
        </el-menu-item-group>

        <el-menu-item-group title="报表分析">
          <el-menu-item index="/report">
            <el-icon><PieChart /></el-icon><span>报表中心</span>
          </el-menu-item>
          <el-menu-item index="/debt">
            <el-icon><Tickets /></el-icon><span>债务概况</span>
          </el-menu-item>
          <el-menu-item index="/credit">
            <i class="fas fa-balance-scale menu-fa-icon"></i><span>债权概况</span>
          </el-menu-item>
        </el-menu-item-group>

        <el-menu-item-group title="系统管理">
          <el-menu-item index="/system/projects">
            <el-icon><OfficeBuilding /></el-icon><span>项目管理</span>
          </el-menu-item>
          <el-menu-item index="/system/suppliers">
            <el-icon><Connection /></el-icon><span>供应商管理</span>
          </el-menu-item>
          <el-menu-item index="/system/dicts">
            <el-icon><List /></el-icon><span>字典管理</span>
          </el-menu-item>
          <el-menu-item index="/system/users">
            <el-icon><UserFilled /></el-icon><span>用户权限</span>
          </el-menu-item>
          <el-menu-item index="/system/init">
            <el-icon><Upload /></el-icon><span>期初初始化</span>
          </el-menu-item>
        </el-menu-item-group>
      </el-menu>

      <!-- 底部用户栏 -->
      <div class="sidebar-footer">
        <el-icon><UserFilled /></el-icon>
        <span class="user-name">{{ store.user?.username || 'admin' }}</span>
        <span class="user-sep">·</span>
        <span class="user-role">{{ roleText }}</span>
        <span class="logout" @click="onLogout">
          <el-icon><SwitchButton /></el-icon> 退出
        </span>
      </div>
    </el-aside>

    <el-container>
      <el-header class="top-bar">
        <div class="breadcrumb">
          <span class="bc-link" @click="router.push('/dashboard')">首页</span>
          <span class="bc-sep">/</span>
          <span class="bc-current">{{ $route.meta.title || '看板统计' }}</span>
        </div>
        <div class="tagline">大表导入 + 手动填报</div>
      </el-header>
      <el-main style="background: #f0f2f6"><router-view :key="$route.fullPath" /></el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  Box, Odometer, Upload, PieChart, Tickets,
  OfficeBuilding, Connection, List, UserFilled, SwitchButton,
} from '@element-plus/icons-vue'

const store = useUserStore()
const router = useRouter()

const roleText = computed(() => {
  const map: Record<string, string> = { admin: '管理员', editor: '填报人', viewer: '查看人' }
  return map[store.user?.role || 'viewer'] || '用户'
})

function onLogout() {
  store.logout()
  router.replace('/login')
}
</script>

<style scoped>
.sidebar {
  background: #0f2a4a;
  color: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.side-menu {
  flex: 1;
  overflow-y: auto;
  border-right: none;
}

/* ============ 菜单项 ============ */
:deep(.el-menu-item) {
  height: 44px !important;
  line-height: 44px !important;
  font-size: 13px !important;
  margin: 0 !important;
  border-radius: 0 !important;
  border-left: 3px solid transparent;
}

/* 选中项：整行蓝底 + 左侧竖条 */
:deep(.el-menu-item.is-active) {
  background: rgba(37, 99, 235, 0.2) !important;
  border-left-color: #2563eb !important;
  color: #fff !important;
  font-weight: 600;
}

/* 悬浮态 */
:deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #fff !important;
}

/* 分组标题 */
:deep(.el-menu-item-group__title) {
  color: rgba(255, 255, 255, 0.3) !important;
  padding: 14px 0 4px 20px !important;
  font-size: 11px !important;
  letter-spacing: 1.5px;
  line-height: 1.2 !important;
}

/* Font Awesome 图标对齐 */
.menu-fa-icon {
  width: 24px;
  text-align: center;
  font-size: 14px;
  margin-right: 4px;
}

/* ============ 深色滚动条 ============ */
.side-menu::-webkit-scrollbar {
  width: 6px;
}
.side-menu::-webkit-scrollbar-track {
  background: #0a1e36;
}
.side-menu::-webkit-scrollbar-thumb {
  background: #566a85;
  border-radius: 3px;
}
.side-menu::-webkit-scrollbar-thumb:hover {
  background: #6b8099;
}
.side-menu {
  scrollbar-width: thin;
  scrollbar-color: #566a85 #0a1e36;
}

/* ============ 底部用户栏 ============ */
.sidebar-footer {
  flex-shrink: 0;
  height: 44px;
  padding: 0 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}
.sidebar-footer .user-name {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 500;
  max-width: 70px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.sidebar-footer .user-sep {
  color: rgba(255, 255, 255, 0.2);
}
.sidebar-footer .user-role {
  color: rgba(255, 255, 255, 0.45);
}
.sidebar-footer .logout {
  margin-left: auto;
  color: #60a5fa;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-weight: 500;
}
.sidebar-footer .logout:hover {
  color: #93c5fd;
}

/* ============ 顶栏 ============ */
.top-bar {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.breadcrumb {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.bc-link {
  color: #2563eb;
  cursor: pointer;
}
.bc-link:hover {
  text-decoration: underline;
}
.bc-sep {
  color: #cbd5e1;
}
.bc-current {
  color: #0f2a4a;
  font-weight: 600;
}

.tagline {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 500;
}
</style>