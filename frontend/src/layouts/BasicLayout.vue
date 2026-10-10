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
        <template v-for="group in menuGroups" :key="group.name">
          <el-menu-item-group :title="group.name">
            <template v-for="menu in group.items" :key="menu.id">
              <!-- 有子菜单 -->
              <el-sub-menu
                v-if="menu.children && menu.children.length"
                :index="'sub-' + menu.id"
              >
                <template #title>
                  <MenuIcon :icon="menu.icon" />
                  <span>{{ menu.menu_name }}</span>
                </template>
                <el-menu-item
                  v-for="child in menu.children"
                  :key="child.id"
                  :index="child.path"
                >
                  <MenuIcon :icon="child.icon" />
                  <span>{{ child.menu_name }}</span>
                </el-menu-item>
              </el-sub-menu>

              <!-- 无子菜单 -->
              <el-menu-item v-else :index="menu.path">
                <MenuIcon :icon="menu.icon" />
                <span>{{ menu.menu_name }}</span>
              </el-menu-item>
            </template>
          </el-menu-item-group>
        </template>
      </el-menu>

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
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { Box, UserFilled, SwitchButton } from '@element-plus/icons-vue'
import { getMyMenuTreeApi, type Menu } from '@/api/sys-menu'
import MenuIcon from '@/components/MenuIcon.vue'

const store = useUserStore()
const router = useRouter()

const roleText = computed(() => {
  const map: Record<string, string> = { ADMIN: '管理员', EDITOR: '填报人', VIEWER: '查看人' }
  const first = (store.user?.roles || [])[0] || 'VIEWER'
  return map[first] || '用户'
})

const menuTree = ref<Menu[]>([])

/**
 * 分组映射：把顶级菜单按"业务分类"归组
 * 数据库暂时没有"分组"字段，前端写死映射，等以后扩展再加
 */
const GROUP_MAP: Record<string, string> = {
  dashboard: '核心功能',
  input: '核心功能',
  report: '报表分析',
  debt: '报表分析',
  credit: '报表分析',
  system: '系统管理',
}
const GROUP_ORDER = ['核心功能', '报表分析', '系统管理', '其他']

const menuGroups = computed(() => {
  const groups: Record<string, Menu[]> = {}
  for (const m of menuTree.value) {
    const g = GROUP_MAP[m.menu_code || ''] || '其他'
    if (!groups[g]) groups[g] = []
    groups[g].push(m)
  }
  return GROUP_ORDER
    .filter((name) => groups[name] && groups[name].length > 0)
    .map((name) => ({ name, items: groups[name] }))
})

async function loadMenus() {
  try {
    menuTree.value = await getMyMenuTreeApi()
  } catch (e) {
    console.error('加载菜单失败', e)
  }
}

function onLogout() {
  store.logout()
  router.replace('/login')
}

onMounted(loadMenus)
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

:deep(.el-menu-item) {
  height: 44px !important;
  line-height: 44px !important;
  font-size: 13px !important;
  margin: 0 !important;
  border-radius: 0 !important;
  border-left: 3px solid transparent;
}
:deep(.el-menu-item.is-active) {
  background: rgba(37, 99, 235, 0.2) !important;
  border-left-color: #2563eb !important;
  color: #fff !important;
  font-weight: 600;
}
:deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #fff !important;
}
:deep(.el-sub-menu__title) {
  height: 44px !important;
  line-height: 44px !important;
  font-size: 13px !important;
  border-left: 3px solid transparent;
}
:deep(.el-sub-menu__title:hover) {
  background: rgba(255, 255, 255, 0.05) !important;
  color: #fff !important;
}
:deep(.el-menu-item-group__title) {
  color: rgba(255, 255, 255, 0.3) !important;
  padding: 14px 0 4px 20px !important;
  font-size: 11px !important;
  letter-spacing: 1.5px;
  line-height: 1.2 !important;
}

.side-menu::-webkit-scrollbar { width: 6px; }
.side-menu::-webkit-scrollbar-track { background: #0a1e36; }
.side-menu::-webkit-scrollbar-thumb { background: #566a85; border-radius: 3px; }
.side-menu::-webkit-scrollbar-thumb:hover { background: #6b8099; }
.side-menu { scrollbar-width: thin; scrollbar-color: #566a85 #0a1e36; }

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
.sidebar-footer .user-sep { color: rgba(255, 255, 255, 0.2); }
.sidebar-footer .user-role { color: rgba(255, 255, 255, 0.45); }
.sidebar-footer .logout {
  margin-left: auto;
  color: #60a5fa;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-weight: 500;
}
.sidebar-footer .logout:hover { color: #93c5fd; }

.top-bar {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.breadcrumb { font-size: 13px; display: flex; align-items: center; gap: 8px; }
.bc-link { color: #2563eb; cursor: pointer; }
.bc-link:hover { text-decoration: underline; }
.bc-sep { color: #cbd5e1; }
.bc-current { color: #0f2a4a; font-weight: 600; }
.tagline { font-size: 11px; color: #94a3b8; font-weight: 500; }
</style>