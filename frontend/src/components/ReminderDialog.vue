<template>
  <el-dialog
    v-model="visible"
    title="提醒管理"
    width="600px"
    :before-close="handleClose"
    class="reminder-dialog"
  >
    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="reminder-tabs">
      <!-- 即将到期的提醒 -->
      <el-tab-pane label="即将到期" name="upcoming">
        <div v-if="upcomingReminders.length === 0" class="empty-state">
          <el-empty description="暂无即将到期的提醒">
            <el-button type="primary" @click="activeTab = 'all'">查看所有提醒</el-button>
          </el-empty>
        </div>
        
        <div v-else class="reminder-list">
          <div
            v-for="reminder in upcomingReminders"
            :key="reminder.id"
            class="reminder-item"
          >
            <h4>{{ reminder.title }}</h4>
            <p v-if="reminder.description">{{ reminder.description }}</p>
            <p>到期时间: {{ new Date(reminder.due_date).toLocaleString('zh-CN') }}</p>
            <p>优先级: {{ reminder.priority }}</p>
            <div v-if="reminder.status === 'pending'">
              <el-button 
                type="success" 
                size="small" 
                @click="handleCompleteReminder(reminder.id)"
              >
                完成
              </el-button>
              <el-button 
                type="warning" 
                size="small" 
                @click="handleSnoozeReminder(reminder.id, 10)"
              >
                延迟10分钟
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 所有提醒 -->
      <el-tab-pane label="所有提醒" name="all">
        <div class="reminder-filters">
          <el-select v-model="statusFilter" placeholder="按状态筛选" clearable style="width: 120px">
            <el-option label="待完成" value="pending" />
            <el-option label="已完成" value="complete" />
          </el-select>
          <el-select v-model="priorityFilter" placeholder="按优先级筛选" clearable style="width: 120px">
            <el-option label="高优先级" value="high" />
            <el-option label="中优先级" value="medium" />
            <el-option label="低优先级" value="low" />
          </el-select>
          <el-button type="primary" @click="refreshAllReminders" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <div v-if="filteredAllReminders.length === 0" class="empty-state">
          <el-empty description="暂无提醒数据">
            <el-button type="primary" @click="createReminderViaChat">通过对话创建提醒</el-button>
          </el-empty>
        </div>
        
        <div v-else class="reminder-list">
          <div
            v-for="reminder in filteredAllReminders"
            :key="reminder.id"
            class="reminder-item"
          >
            <h4>{{ reminder.title }}</h4>
            <p v-if="reminder.description">{{ reminder.description }}</p>
            <p>到期时间: {{ new Date(reminder.due_date).toLocaleString('zh-CN') }}</p>
            <p>优先级: {{ reminder.priority }} | 状态: {{ reminder.status }}</p>
            <div v-if="reminder.status === 'pending'">
              <el-button 
                type="success" 
                size="small" 
                @click="handleCompleteReminder(reminder.id)"
              >
                完成
              </el-button>
              <el-button 
                type="warning" 
                size="small" 
                @click="handleSnoozeReminder(reminder.id, 10)"
              >
                延迟10分钟
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="createReminderViaChat">
          <el-icon><Plus /></el-icon>
          创建新提醒
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElDialog, ElTabs, ElTabPane, ElEmpty, ElButton, ElSelect, ElOption, ElIcon, ElMessage } from 'element-plus'
import { Refresh, Plus } from '@element-plus/icons-vue'
import type { Reminder } from '../services/chatService'
import { chatService } from '../services/chatService'
// import ReminderCard from './ReminderCard.vue'

// Props
interface Props {
  modelValue: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'create-reminder': []
}>()

// Reactive data
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const activeTab = ref('upcoming')
const loading = ref(false)
const upcomingReminders = ref<Reminder[]>([])
const allReminders = ref<Reminder[]>([])
const statusFilter = ref<string>('')
const priorityFilter = ref<string>('')

// Computed
const filteredAllReminders = computed(() => {
  let filtered = allReminders.value

  if (statusFilter.value) {
    filtered = filtered.filter(r => r.status === statusFilter.value)
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(r => r.priority === priorityFilter.value)
  }

  return filtered.sort((a, b) => {
    // 按优先级和到期时间排序
    const priorityOrder = { high: 3, medium: 2, low: 1 }
    const aPriority = priorityOrder[a.priority] || 0
    const bPriority = priorityOrder[b.priority] || 0
    
    if (aPriority !== bPriority) {
      return bPriority - aPriority
    }
    
    return new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
  })
})

// Methods
const loadUpcomingReminders = async () => {
  try {
    loading.value = true
    upcomingReminders.value = await chatService.getUpcomingReminders(60) // 1小时内
  } catch (error) {
    console.error('加载即将到期提醒失败:', error)
    ElMessage.error('加载提醒失败')
  } finally {
    loading.value = false
  }
}

const loadAllReminders = async () => {
  try {
    loading.value = true
    // 使用 getUpcomingReminders 获取较长时间范围内的提醒
    allReminders.value = await chatService.getUpcomingReminders(7 * 24 * 60) // 7天内的提醒
  } catch (error) {
    console.error('加载所有提醒失败:', error)
    ElMessage.error('加载提醒失败')
  } finally {
    loading.value = false
  }
}

const refreshAllReminders = async () => {
  await loadAllReminders()
  await loadUpcomingReminders()
}

const handleCompleteReminder = async (reminderId: number) => {
  try {
    const success = await chatService.completeReminder(reminderId)
    if (success) {
      ElMessage.success('提醒已完成')
      await refreshAllReminders()
    } else {
      ElMessage.error('完成提醒失败')
    }
  } catch (error) {
    console.error('完成提醒失败:', error)
    ElMessage.error('完成提醒失败')
  }
}

const handleSnoozeReminder = async (reminderId: number, minutes: number = 10) => {
  try {
    const success = await chatService.snoozeReminder(reminderId, minutes)
    if (success) {
      ElMessage.success(`提醒已延迟 ${minutes} 分钟`)
      await refreshAllReminders()
    } else {
      ElMessage.error('延迟提醒失败')
    }
  } catch (error) {
    console.error('延迟提醒失败:', error)
    ElMessage.error('延迟提醒失败')
  }
}

const createReminderViaChat = () => {
  emit('create-reminder')
  handleClose()
}

const handleClose = () => {
  visible.value = false
}

// Watch for dialog visibility changes
watch(visible, async (newVisible) => {
  if (newVisible) {
    await loadUpcomingReminders()
    if (activeTab.value === 'all') {
      await loadAllReminders()
    }
  }
})

// Watch for tab changes
watch(activeTab, async (newTab) => {
  if (newTab === 'all' && allReminders.value.length === 0) {
    await loadAllReminders()
  }
})

// Lifecycle
onMounted(() => {
  if (visible.value) {
    loadUpcomingReminders()
  }
})
</script>

<style scoped>
.reminder-dialog .reminder-tabs {
  min-height: 400px;
}

.reminder-dialog .reminder-filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.reminder-dialog .reminder-list {
  max-height: 400px;
  overflow-y: auto;
}

.reminder-dialog .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.reminder-dialog .dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reminder-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background: white;
}

.reminder-item h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.reminder-item p {
  margin: 4px 0;
  color: #606266;
  font-size: 14px;
}

.reminder-item .el-button {
  margin-right: 8px;
}
</style>
