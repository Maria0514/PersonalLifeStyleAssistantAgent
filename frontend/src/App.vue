<script setup lang="ts">
// 直接导入组件，Vue 3会自动处理
import ChatInterface from './components/ChatInterface.vue'
import { onMounted, onUnmounted } from 'vue'
import { ReminderService } from './services/reminderService'
import { chatService } from './services/chatService'

// 提醒服务实例
let reminderService: ReminderService

onMounted(() => {
  // 初始化提醒服务
  reminderService = new ReminderService(chatService)
  reminderService.start()
})

onUnmounted(() => {
  // 清理提醒服务
  if (reminderService) {
    reminderService.stop()
  }
})
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
