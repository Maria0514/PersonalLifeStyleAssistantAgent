<template>
  <div class="chat-container">
    <!-- 头部标题 -->
    <header class="chat-header">
      <h1>个人生活助理 Agent</h1>
      <p>我可以帮您查询天气、进行计算、提供记账建议等各种生活事务</p>
    </header>

    <!-- 消息显示区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <!-- 工具使用指示器 -->
      <div v-if="isUsingTool" class="tool-indicator">
        <div class="tool-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8" v-if="currentToolId === 'search'"></circle>
            <path d="m21 21-4.35-4.35" v-if="currentToolId === 'search'"></path>
            <rect x="4" y="2" width="16" height="20" rx="2" v-if="currentToolId === 'calculator'"></rect>
            <line x1="8" y1="6" x2="16" y2="6" v-if="currentToolId === 'calculator'"></line>
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" v-if="currentToolId === 'memory'"></path>
            <circle cx="12" cy="12" r="10" v-if="currentToolId === 'reminder'"></circle>
          </svg>
        </div>
        <div class="tool-text">
          <div class="tool-name">{{ getToolName(currentToolId) }}</div>
          <div class="tool-description">{{ getToolDescription(currentToolId) }}</div>
        </div>
        <div class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <!-- 消息列表 -->
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message-bubble', `message-${message.type}`]"
      >
        <div v-if="message.type === 'bot'" class="avatar">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </div>
        
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.text)"></div>
          <div class="message-meta">
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
            <span v-if="message.type === 'user'" class="message-status">已发送</span>
            <!-- AI回复的metadata信息 -->
            <div v-if="message.type === 'bot' && message.metadata" class="ai-metadata">
              <span class="metadata-item">
                {{ message.metadata.tokens_used }} tokens
              </span>
              <span class="metadata-separator">•</span>
              <span class="metadata-item">
                {{ formatResponseTime(message.metadata.response_time) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 正在输入指示器 -->
      <div v-if="isTyping && !isUsingTool" class="message bot-message">
        <div class="message-content">
          <div class="typing-indicator">
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input-container">
      <div class="input-wrapper">
        <textarea
          v-model="currentMessage"
          @keydown.enter.prevent="sendMessage"
          placeholder="请输入您的问题..."
          rows="1"
          ref="messageInput"
          :disabled="isLoading"
          class="message-input"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!currentMessage.trim() || isLoading"
          class="send-button"
        >
          <svg
            v-if="!isLoading"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
          >
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22,2 15,22 11,13 2,9"></polygon>
          </svg>
          <div v-else class="loading-spinner"></div>
        </button>
      </div>

      <!-- 快捷功能按钮 -->
      <div class="quick-actions">
        <button
          v-for="action in quickActions"
          :key="action.text"
          @click="useQuickAction(action.text)"
          class="quick-action-btn"
        >
          {{ action.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, nextTick, onMounted } from 'vue'
import { chatService, type ChatMetadata } from '../services/chatService'

interface Message {
  id: number
  text: string
  type: 'user' | 'bot'
  timestamp: Date
  metadata?: ChatMetadata
}

interface QuickAction {
  label: string
  text: string
}

export default defineComponent({
  name: 'ChatInterface',
  setup() {

const messages = ref<Message[]>([])
const currentMessage = ref('')
const isLoading = ref(false)
const isTyping = ref(false)
const isUsingTool = ref(false)
const currentToolId = ref<string>('')
const messagesContainer = ref<HTMLElement>()
const messageInput = ref<HTMLTextAreaElement>()

const quickActions: QuickAction[] = [
  { label: '查询天气', text: '今天的天气怎么样？' },
  { label: '数学计算', text: '帮我计算 15 * 23 + 47' },
  { label: '记账建议', text: '请给我一些记账建议' },
  { label: '设置提醒', text: '帮我设置一个提醒' }
]

let messageIdCounter = 0

// 初始化欢迎消息
onMounted(() => {
  addBotMessage('您好！我是您的个人生活助理，可以帮您处理各种日常生活事务。请问有什么我可以帮助您的吗？')
})

// 发送消息
const sendMessage = async () => {
  const message = currentMessage.value.trim()
  if (!message || isLoading.value) return

  // 添加用户消息
  addUserMessage(message)
  currentMessage.value = ''

  // 调整输入框高度
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
  }

  try {
    isLoading.value = true
    
    // 模拟工具使用
    const toolId = detectToolNeeded(message)
    if (toolId) {
      isUsingTool.value = true
      currentToolId.value = toolId
      
      // 模拟工具处理时间
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      isUsingTool.value = false
    }
    
    isTyping.value = true

    // 调用后端API
    const response = await chatService.sendMessage(message)
    
    // 模拟打字效果
    setTimeout(() => {
      isTyping.value = false
      addBotMessage(response.message, response.metadata)
    }, 800)

  } catch (error) {
    isTyping.value = false
    isUsingTool.value = false
    addBotMessage('抱歉，我现在遇到了一些技术问题，请稍后再试。')
    console.error('发送消息失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 检测需要使用的工具
const detectToolNeeded = (message: string): string => {
  const lowerMessage = message.toLowerCase()
  
  if (lowerMessage.includes('天气') || lowerMessage.includes('搜索')) {
    return 'search'
  }
  
  if (lowerMessage.includes('计算') || /[\d+\-*/]/.test(message)) {
    return 'calculator'
  }
  
  if (lowerMessage.includes('记住') || lowerMessage.includes('之前')) {
    return 'memory'
  }
  
  if (lowerMessage.includes('提醒') || lowerMessage.includes('闹钟')) {
    return 'reminder'
  }
  
  return ''
}

// 使用快捷操作
const useQuickAction = (text: string) => {
  currentMessage.value = text
  sendMessage()
}

// 添加用户消息
const addUserMessage = (text: string) => {
  messages.value.push({
    id: ++messageIdCounter,
    text,
    type: 'user',
    timestamp: new Date()
  })
  scrollToBottom()
}

// 添加机器人消息
const addBotMessage = (text: string, metadata?: ChatMetadata) => {
  messages.value.push({
    id: ++messageIdCounter,
    text,
    type: 'bot',
    timestamp: new Date(),
    metadata
  })
  scrollToBottom()
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 格式化消息内容
const formatMessage = (text: string) => {
  return text.replace(/\n/g, '<br>')
}

// 格式化时间
const formatTime = (timestamp: Date) => {
  return timestamp.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化响应时间
const formatResponseTime = (responseTime: number) => {
  if (responseTime < 1) {
    return `${Math.round(responseTime * 1000)}ms`
  } else {
    return `${responseTime.toFixed(2)}s`
  }
}

// 获取工具名称
const getToolName = (toolId: string) => {
  const toolNames: Record<string, string> = {
    search: '网络搜索',
    calculator: '计算器',
    memory: '记忆系统',
    reminder: '提醒工具'
  }
  return toolNames[toolId] || '处理中'
}

// 获取工具描述
const getToolDescription = (toolId: string) => {
  const toolDescriptions: Record<string, string> = {
    search: '正在搜索最新信息...',
    calculator: '正在进行数学计算...',
    memory: '正在回忆相关信息...',
    reminder: '正在设置提醒...'
  }
  return toolDescriptions[toolId] || '正在处理您的请求...'
}

// 自动调整输入框高度
const adjustTextareaHeight = () => {
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
    messageInput.value.style.height = messageInput.value.scrollHeight + 'px'
  }
}

// 监听输入框内容变化
const handleInput = () => {
  adjustTextareaHeight()
}

    return {
      messages,
      currentMessage,
      isLoading,
      isTyping,
      isUsingTool,
      currentToolId,
      messagesContainer,
      messageInput,
      quickActions,
      sendMessage,
      useQuickAction,
      formatMessage,
      formatTime,
      formatResponseTime,
      getToolName,
      getToolDescription,
      handleInput
    }
  }
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: white;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
}

.chat-header h1 {
  margin-bottom: 8px;
  font-size: 24px;
}

.chat-header p {
  opacity: 0.9;
  font-size: 14px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

/* 工具指示器样式 */
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

/* 消息气泡样式 */
.message-bubble {
  display: flex;
  margin-bottom: 16px;
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-user {
  justify-content: flex-end;
}

.message-bot {
  justify-content: flex-start;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.message-user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-text {
  line-height: 1.4;
  word-wrap: break-word;
  margin-bottom: 4px;
}

.message-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  font-size: 12px;
  opacity: 0.7;
}

.message-time {
  margin-right: 8px;
}

.message-status {
  font-style: italic;
}

/* AI回复的metadata样式 */
.ai-metadata {
  display: flex;
  align-items: center;
  font-size: 11px;
  color: #999;
  margin-top: 2px;
  opacity: 0.8;
}

.metadata-item {
  font-weight: 500;
}

.metadata-separator {
  margin: 0 6px;
  color: #ccc;
}

.message {
  margin-bottom: 16px;
  display: flex;
}

.bot-message {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.bot-message .message-content {
  background: white;
  color: #333;
  border: 1px solid #e9ecef;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.typing-indicator {
  display: flex;
  align-items: center;
  height: 20px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  background: #999;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.chat-input-container {
  padding: 20px;
  background: white;
  border-top: 1px solid #e9ecef;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 12px;
}

.message-input {
  flex: 1;
  min-height: 44px;
  max-height: 120px;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 22px;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.4;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: #667eea;
}

.message-input:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

.send-button {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, opacity 0.2s;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-action-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background: white;
  color: #666;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.quick-action-btn:hover {
  background: #f8f9fa;
  border-color: #667eea;
  color: #667eea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    height: 100vh;
    margin: 0;
    border-radius: 0;
  }

  .message-content {
    max-width: 85%;
  }

  .chat-header {
    padding: 16px;
  }

  .chat-header h1 {
    font-size: 20px;
  }

  .chat-messages {
    padding: 16px;
  }

  .chat-input-container {
    padding: 16px;
  }

  .quick-actions {
    gap: 6px;
  }

  .quick-action-btn {
    font-size: 11px;
    padding: 6px 12px;
  }
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
