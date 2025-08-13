<template>
  <div v-if="visible" class="tool-indicator">
    <div class="tool-icon">
      <component :is="currentToolIcon" />
    </div>
    <div class="tool-text">
      <div class="tool-name">{{ currentTool?.name }}</div>
      <div class="tool-description">{{ currentTool?.description }}</div>
    </div>
    <div class="loading-dots">
      <span></span>
      <span></span>
      <span></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Tool {
  id: string
  name: string
  description: string
  icon: string
}

interface Props {
  visible: boolean
  toolId?: string
}

const props = defineProps<Props>()

const tools: Tool[] = [
  {
    id: 'search',
    name: '网络搜索',
    description: '正在搜索最新信息...',
    icon: 'SearchIcon'
  },
  {
    id: 'calculator',
    name: '计算器',
    description: '正在进行数学计算...',
    icon: 'CalcIcon'
  },
  {
    id: 'memory',
    name: '记忆系统',
    description: '正在回忆相关信息...',
    icon: 'MemoryIcon'
  },
  {
    id: 'reminder',
    name: '提醒工具',
    description: '正在设置提醒...',
    icon: 'ReminderIcon'
  }
]

const currentTool = computed(() => {
  return tools.find(tool => tool.id === props.toolId) || tools[0]
})

const currentToolIcon = computed(() => {
  const iconMap: Record<string, any> = {
    SearchIcon: 'svg',
    CalcIcon: 'svg', 
    MemoryIcon: 'svg',
    ReminderIcon: 'svg'
  }
  return iconMap[currentTool.value.icon] || 'svg'
})

// SVG图标组件
const SearchIcon = {
  template: `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <circle cx="11" cy="11" r="8"></circle>
      <path d="m21 21-4.35-4.35"></path>
    </svg>
  `
}

const CalcIcon = {
  template: `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <rect x="4" y="2" width="16" height="20" rx="2"></rect>
      <line x1="8" y1="6" x2="16" y2="6"></line>
      <line x1="8" y1="10" x2="16" y2="10"></line>
      <line x1="8" y1="14" x2="16" y2="14"></line>
      <line x1="8" y1="18" x2="16" y2="18"></line>
    </svg>
  `
}

const MemoryIcon = {
  template: `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14,2 14,8 20,8"></polyline>
      <line x1="16" y1="13" x2="8" y2="13"></line>
      <line x1="16" y1="17" x2="8" y2="17"></line>
      <polyline points="10,9 9,9 8,9"></polyline>
    </svg>
  `
}

const ReminderIcon = {
  template: `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <circle cx="12" cy="12" r="10"></circle>
      <polyline points="12,6 12,12 16,14"></polyline>
    </svg>
  `
}
</script>

<style scoped>
.tool-indicator {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  margin-bottom: 16px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.tool-icon {
  color: #667eea;
  margin-right: 12px;
  flex-shrink: 0;
}

.tool-text {
  flex: 1;
  margin-right: 12px;
}

.tool-name {
  font-weight: 600;
  color: #667eea;
  font-size: 14px;
  margin-bottom: 2px;
}

.tool-description {
  color: #666;
  font-size: 12px;
  opacity: 0.8;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background: #667eea;
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 60%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  30% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
