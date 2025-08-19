<template>
  <div class="conversation-history">
    <!-- 对话列表头部 -->
    <div class="history-header">
      <h3>
        <el-icon><ChatDotRound /></el-icon>
        对话历史
      </h3>
      <el-button 
        type="primary" 
        size="small" 
        @click="startNewConversation"
        :icon="Plus"
      >
        新对话
      </el-button>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="searchQuery"
        placeholder="搜索对话内容..."
        :prefix-icon="Search"
        @input="handleSearch"
        :loading="isSearching"
        clearable
      />
      <div class="search-mode-container">
        <span class="search-mode-label">搜索范围：</span>
        <el-radio-group v-model="searchMode" class="search-mode" size="small">
          <el-radio-button value="global">全局</el-radio-button>
          <el-radio-button value="current" :disabled="!currentSessionId">当前</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 对话列表 -->
    <div class="conversation-list" v-loading="loading || isSearching">
      <!-- 搜索结果详情 -->
      <div
        v-if="searchQuery && searchMessages.length > 0"
        class="search-results"
      >
        <div class="search-header">
          <h4>搜索结果</h4>
          <span class="result-count">共找到 {{ searchMessages.length }} 条消息</span>
        </div>
        
        <div class="results-list">
          <div 
            v-for="message in searchMessages" 
            :key="message.id"
            class="message-item"
            @click="handleJumpToConversation(message.session_id)"
          >
            <div class="message-header">
              <span class="message-role" :class="message.role">
                {{ message.role === 'user' ? '用户' : 'AI助手' }}
              </span>
              <span class="message-time">{{ formatMessageTime(message.timestamp) }}</span>
            </div>
            <div class="message-content">
              <span v-html="highlightSearchTerm(message.content)"></span>
            </div>
            <div class="message-session" v-if="searchMode === 'global'">
              来自对话：{{ getConversationTitle(message.session_id) }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 对话列表 -->
      <div
        v-for="conversation in filteredConversations"
        :key="conversation.session_id"
        class="conversation-item"
        :class="{ active: conversation.session_id === currentSessionId }"
        @click="selectConversation(conversation)"
      >
        <div class="conversation-header">
          <span class="conversation-title">{{ conversation.title }}</span>
          <el-dropdown @command="(command) => handleCommand(command, conversation)">
            <el-icon class="more-icon"><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="delete">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="conversation-meta">
          <span class="message-count">{{ conversation.message_count }} 条消息</span>
          <span class="time">{{ formatTime(conversation.updated_at) }}</span>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && filteredConversations.length === 0" class="empty-state">
        <el-empty description="暂无对话历史">
          <el-button type="primary" @click="startNewConversation">开始新对话</el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound, Plus, Search, MoreFilled } from '@element-plus/icons-vue'
import { chatService, type Conversation, type Message } from '../services/chatService'

// Props
interface Props {
  currentSessionId?: string
}

const props = withDefaults(defineProps<Props>(), {
  currentSessionId: ''
})

// Emits
const emit = defineEmits<{
  sessionChanged: [sessionId: string]
  newConversation: []
}>()

// 响应式数据
const conversations = ref<Conversation[]>([])
const searchQuery = ref('')
const loading = ref(false)
const searchResults = ref<Conversation[]>([])
const searchMessages = ref<Message[]>([])
const isSearching = ref(false)
const searchMode = ref<'global' | 'current'>('global')
let searchTimeout: number | null = null

// 计算属性
const filteredConversations = computed(() => {
  // 如果有搜索查询，显示搜索结果
  if (searchQuery.value && searchResults.value.length > 0) {
    return searchResults.value
  }
  
  // 如果没有搜索查询，显示所有对话
  if (!searchQuery.value) {
    return conversations.value
  }
  
  // 如果有搜索查询但没有结果，返回空数组
  return []
})

// 方法
const loadConversations = async () => {
  loading.value = true
  try {
    conversations.value = await chatService.getConversations()
  } catch (error) {
    console.error('加载对话历史失败:', error)
    ElMessage.error('加载对话历史失败')
  } finally {
    loading.value = false
  }
}

const selectConversation = (conversation: Conversation) => {
  emit('sessionChanged', conversation.session_id)
}

const startNewConversation = () => {
  emit('newConversation')
}

const handleSearch = async () => {
  // 清除之前的搜索延时
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  if (!searchQuery.value.trim()) {
    // 如果搜索框为空，清空搜索结果
    searchResults.value = []
    searchMessages.value = []
    isSearching.value = false
    return
  }

  // 添加防抖延时，500ms后执行搜索
  searchTimeout = window.setTimeout(async () => {
    isSearching.value = true
    try {
      let messages: Message[] = []
      
      // 根据搜索模式调用不同的接口
      if (searchMode.value === 'current' && props.currentSessionId) {
        // 在当前对话中搜索
        messages = await chatService.searchMessages(searchQuery.value, props.currentSessionId)
      } else {
        // 全局搜索
        messages = await chatService.searchMessages(searchQuery.value)
      }
      
      // 保存搜索到的消息
      searchMessages.value = messages
      
      // 根据搜索到的消息，提取相关的对话
      const sessionIds = [...new Set(messages.map(msg => msg.session_id))]
      
      // 过滤出包含搜索结果的对话
      searchResults.value = conversations.value.filter(conv => 
        sessionIds.includes(conv.session_id)
      )
      
      console.log(`搜索模式: ${searchMode.value}, 搜索到 ${messages.length} 条消息，涉及 ${searchResults.value.length} 个对话`)
    } catch (error) {
      console.error('搜索失败:', error)
      ElMessage.error('搜索失败，请稍后重试')
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }, 500)
}

const handleCommand = async (command: string, conversation: Conversation) => {
  if (command === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定要删除对话"${conversation.title}"吗？此操作无法撤销。`,
        '确认删除',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
      
      const success = await chatService.deleteConversation(conversation.session_id)
      if (success) {
        ElMessage.success('对话已删除')
        await loadConversations()
        
        // 如果删除的是当前对话，切换到新对话
        if (conversation.session_id === props.currentSessionId) {
          startNewConversation()
        }
      } else {
        ElMessage.error('删除失败')
      }
    } catch {
      // 用户取消删除
    }
  }
}

const handleJumpToConversation = (sessionId: string) => {
  // 清空搜索状态
  searchQuery.value = ''
  searchResults.value = []
  searchMessages.value = []
  
  // 跳转到指定对话
  emit('sessionChanged', sessionId)
}

const highlightSearchTerm = (content: string) => {
  if (!searchQuery.value) return content
  
  const regex = new RegExp(`(${searchQuery.value})`, 'gi')
  return content.replace(regex, '<mark>$1</mark>')
}

const formatMessageTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
  
  if (diffInHours < 1) {
    return '刚刚'
  } else if (diffInHours < 24) {
    return `${diffInHours}小时前`
  } else {
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays}天前`
  }
}

const getConversationTitle = (sessionId: string) => {
  const conversation = conversations.value.find(conv => conv.session_id === sessionId)
  return conversation?.title || '未知对话'
}

const formatTime = (timeStr: string) => {
  const time = new Date(timeStr)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) {
    return '刚刚'
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前`
  } else if (diffInMinutes < 24 * 60) {
    const hours = Math.floor(diffInMinutes / 60)
    return `${hours}小时前`
  } else {
    const days = Math.floor(diffInMinutes / (24 * 60))
    return `${days}天前`
  }
}

// 生命周期
onMounted(() => {
  loadConversations()
})

onUnmounted(() => {
  // 清理搜索定时器
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})

// 暴露方法给父组件
defineExpose({
  loadConversations
})
</script>

<style scoped>
.conversation-history {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.history-header {
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-box {
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.search-mode-container {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-mode-label {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
}

.search-mode {
  flex: 1;
  display: flex;
}

.search-mode :deep(.el-radio-button) {
  flex: 1;
}

.search-mode :deep(.el-radio-button__inner) {
  width: 100%;
  text-align: center;
  padding: 6px 8px;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-radius: 4px;
  min-width: 0;
}

.search-mode :deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.search-mode :deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.search-results {
  margin-bottom: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  max-height: 400px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.search-header {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.result-count {
  color: #909399;
  font-size: 12px;
}

.results-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.message-item {
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.message-item:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.message-role {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.message-role.user {
  background: #e1f3d8;
  color: #67c23a;
}

.message-role.assistant {
  background: #ecf5ff;
  color: #409eff;
}

.message-time {
  color: #909399;
  font-size: 12px;
}

.message-content {
  color: #606266;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.message-content :deep(mark) {
  background-color: #ffd04b;
  color: #606266;
  padding: 0 2px;
  border-radius: 2px;
}

.message-session {
  color: #909399;
  font-size: 12px;
  font-style: italic;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.conversation-item {
  padding: 12px 16px;
  margin: 0 8px 4px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
  border: 1px solid transparent;
}

.conversation-item:hover {
  background: #f0f9ff;
  border-color: #d1ecf1;
}

.conversation-item.active {
  background: #e1f5fe;
  border-color: #409eff;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.conversation-title {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-icon {
  font-size: 16px;
  color: #909399;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.more-icon:hover {
  background: #f5f7fa;
  color: #606266;
}

.conversation-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.message-count {
  flex: 1;
}

.time {
  flex-shrink: 0;
}

.empty-state {
  padding: 32px 16px;
  text-align: center;
}

/* 滚动条样式 */
.conversation-list::-webkit-scrollbar {
  width: 6px;
}

.conversation-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
