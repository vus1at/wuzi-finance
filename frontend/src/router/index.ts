import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ========== 登录页 ==========
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/index.vue'),
      meta: { public: true },
    },

    // ========== 主布局 ==========
    {
      path: '/',
      component: () => import('@/layouts/BasicLayout.vue'),
      redirect: '/dashboard',
      children: [
        // ----- 核心功能 -----
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/index.vue'),
          meta: { title: '看板统计' },
        },
        {
          path: 'input',
          name: 'Input',
          component: () => import('@/views/placeholder.vue'),
          meta: { title: '数据填报' },
        },

        // ----- 报表分析 -----
        {
          path: 'report',
          name: 'Report',
          component: () => import('@/views/placeholder.vue'),
          meta: { title: '报表中心' },
        },
        {
          path: 'debt',
          name: 'Debt',
          component: () => import('@/views/placeholder.vue'),
          meta: { title: '债务概况' },
        },
        {
          path: 'credit',
          name: 'Credit',
          component: () => import('@/views/placeholder.vue'),
          meta: { title: '债权概况' },
        },

        // ----- 系统管理 -----
        {
          path: 'system/projects',
          name: 'Projects',
          component: () => import('@/views/system/projects.vue'),
          meta: { title: '项目管理' },
        },
        {
          path: 'system/suppliers',
          name: 'Suppliers',
          component: () => import('@/views/system/suppliers.vue'),
          meta: { title: '供应商管理' },
        },
        {
          path: 'system/dicts',
          name: 'Dicts',
          component: () => import('@/views/system/dicts.vue'),
          meta: { title: '字典管理' },
        },
        {
          path: 'system/users',
          name: 'Users',
          component: () => import('@/views/system/users.vue'),
          meta: { title: '用户权限' },
        },
        {
          path: 'system/init',
          name: 'Init',
          component: () => import('@/views/placeholder.vue'),
          meta: { title: '期初初始化' },
        },
        {
          path: 'system/menus',
          name: 'Menus',
          component: () => import('@/views/system/menus.vue'),
          meta: { title: '菜单管理' },
        },
        { 
          path: 'system/roles', 
          name: 'Roles',
          component: () => import('@/views/system/roles.vue'),
          meta: { title: '角色管理' } 
        },
      ],
    },

    // ========== 404 兜底 ==========
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
})

// ========== 路由守卫 ==========
router.beforeEach(async (to) => {
  const store = useUserStore()

  // 公开页直接放行
  if (to.meta.public) return true

  // 未登录 → 跳登录页，带上 redirect
  if (!store.isLogin) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // 有 token 但还没拉过用户信息（刷新页面场景）→ 拉一次
  if (!store.user) {
    try {
      await store.fetchMe()
    } catch {
      store.logout()
      return { path: '/login' }
    }
  }

  return true
})

export default router