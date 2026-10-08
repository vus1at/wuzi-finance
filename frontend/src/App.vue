<template>
  <router-view />
</template>

<style>
/* 全局字体：微软雅黑优先 */
html,
body,
#app,
button,
input,
select,
textarea,
.el-button,
.el-input__inner,
.el-message,
.el-drawer,
.el-table,
.el-card {
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB',
               'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.el-table,
.num {
  font-variant-numeric: tabular-nums;
}

body {
  margin: 0;
  padding: 0;
  font-size: 14px;
  color: #1e293b;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

button,
input,
select,
textarea {
  font-family: inherit;
  font-size: inherit;
}
</style>