<template>
  <div style="padding: 40px; text-align: center; color: #94a3b8">
    <el-icon :size="48" style="margin-bottom: 16px"><Tools /></el-icon>
    <h2 style="color: #64748b; margin-bottom: 8px">{{ title }}</h2>
    <p>该模块正在开发中，敬请期待</p>
  </div>
</template>

<script setup lang="ts">
import { Tools } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = (route.meta.title as string) || '功能模块'
</script>