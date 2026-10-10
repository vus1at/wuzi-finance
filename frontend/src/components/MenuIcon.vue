<template>
  <!-- Font Awesome：数据库存 "fa:xxx" -->
  <i
    v-if="isFa"
    :class="['fas', faClass, 'menu-icon', 'menu-fa-icon']"
  ></i>

  <!-- Element Plus：数据库存 "Odometer" 等 -->
  <span v-else-if="icon" class="menu-icon menu-el-icon">
    <component :is="icon" />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ icon?: string }>()

const isFa = computed(() => (props.icon || '').startsWith('fa:'))
const faClass = computed(() => (props.icon || '').slice(3))
</script>

<style scoped>
.menu-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 8px;
  vertical-align: middle;
}
.menu-el-icon {
  font-size: 16px;
}
.menu-fa-icon {
  font-size: 15px;
}
</style>