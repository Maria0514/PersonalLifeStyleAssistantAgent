<script setup lang="ts">
// 直接导入组件，Vue 3会自动处理
import ChatInterface from './components/ChatInterface.vue'
</script>

<template>
  <div id="app">
    <ChatInterface />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: #f5f5f5;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
