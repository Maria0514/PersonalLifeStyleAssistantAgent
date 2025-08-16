<template>
  <div :class="['reminder-card', `priority-${reminder.priority}`, { 'completed': reminder.status === 'complete' }]">
    <div class="reminder-header">
      <div class="priority-indicator"></div>
      <h3 class="reminder-title">{{ reminder.title }}</h3>
      <div class="reminder-status">
        <el-tag
          :type="getStatusType(reminder.status)"
          size="small"
        >
          {{ getStatusText(reminder.status) }}
        </el-tag>
      </div>
    </div>

    <div v-if="reminder.description" class="reminder-description">
      {{ reminder.description }}
    </div>

    <div class="reminder-meta">
      <div class="reminder-time">
        <el-icon><Clock /></el-icon>
        <span>{{ formatDueDate(reminder.due_date) }}</span>
        <span v-if="isOverdue" class="overdue-indicator">已逾期</span>
      </div>
      <div class="reminder-priority">
        <el-tag
          :type="getPriorityType(reminder.priority)"
          size="small"
        >
          {{ getPriorityText(reminder.priority) }}
        </el-tag>
      </div>
    </div>

    <div v-if="showActions && reminder.status === 'pending'" class="reminder-actions">
      <el-button-group>
        <el-button
          type="success"
          size="small"
          @click="$emit('complete', reminder.id)"
        >
          <el-icon><Check /></el-icon>
          完成
        </el-button>
        <el-dropdown @command="handleSnoozeCommand">
          <el-button type="warning" size="small">
            <el-icon><Clock /></el-icon>
            延迟
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="5">延迟 5 分钟</el-dropdown-item>
              <el-dropdown-item command="10">延迟 10 分钟</el-dropdown-item>
              <el-dropdown-item command="30">延迟 30 分钟</el-dropdown-item>
              <el-dropdown-item command="60">延迟 1 小时</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-button-group>
    </div>

    <div v-if="reminder.completed_at" class="reminder-completed">
      <el-icon><Check /></el-icon>
      <span>已完成于 {{ formatTime(reminder.completed_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ElTag, ElButton, ElButtonGroup, ElDropdown, ElDropdownMenu, ElDropdownItem, ElIcon } from 'element-plus'
import { Clock, Check, ArrowDown } from '@element-plus/icons-vue'
import type { Reminder } from '../services/chatService'

// Props
interface Props {
  reminder: Reminder
  showActions?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showActions: true
})

// Emits
const emit = defineEmits<{
  complete: [id: number]
  snooze: [id: number, minutes: number]
}>()

// Computed
const isOverdue = computed(() => {
  if (props.reminder.status === 'complete') return false
  return new Date(props.reminder.due_date) < new Date()
})

// Methods
const getStatusType = (status: string) => {
  switch (status) {
    case 'complete': return 'success'
    case 'pending': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'complete': return '已完成'
    case 'pending': return '待完成'
    default: return '未知'
  }
}

const getPriorityType = (priority: string) => {
  switch (priority) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

const getPriorityText = (priority: string) => {
  switch (priority) {
    case 'high': return '高优先级'
    case 'medium': return '中优先级'
    case 'low': return '低优先级'
    default: return '未知'
  }
}

const formatDueDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMs < 0) {
    const absMinutes = Math.abs(diffMins)
    if (absMinutes < 60) {
      return `${absMinutes} 分钟前到期`
    } else if (absMinutes < 1440) {
      return `${Math.abs(diffHours)} 小时前到期`
    } else {
      return `${Math.abs(diffDays)} 天前到期`
    }
  }

  if (diffMins < 60) {
    return `${diffMins} 分钟后到期`
  } else if (diffHours < 24) {
    return `${diffHours} 小时后到期`
  } else if (diffDays < 7) {
    return `${diffDays} 天后到期`
  } else {
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

const formatTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleSnoozeCommand = (minutes: string) => {
  emit('snooze', props.reminder.id, parseInt(minutes))
}
</script>

<style scoped>
.reminder-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  transition: all 0.3s ease;
  position: relative;
}

.reminder-card:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.reminder-card.completed {
  opacity: 0.7;
  background: #f8f9fa;
}

.reminder-card.priority-high {
  border-left: 4px solid #f56c6c;
}

.reminder-card.priority-medium {
  border-left: 4px solid #e6a23c;
}

.reminder-card.priority-low {
  border-left: 4px solid #909399;
}

.reminder-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.priority-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.priority-high .priority-indicator {
  background: #f56c6c;
}

.priority-medium .priority-indicator {
  background: #e6a23c;
}

.priority-low .priority-indicator {
  background: #909399;
}

.reminder-title {
  flex: 1;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.reminder-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 12px;
}

.reminder-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 12px;
  color: #909399;
}

.reminder-time {
  display: flex;
  align-items: center;
  gap: 4px;
}

.overdue-indicator {
  color: #f56c6c;
  font-weight: 600;
}

.reminder-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.reminder-completed {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #67c23a;
  font-size: 12px;
}

.el-button-group .el-button {
  font-size: 12px;
}

.el-dropdown .el-button {
  font-size: 12px;
}
</style>
