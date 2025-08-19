import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatService, type Conversation, type Message } from '../services/chatService'

export const useConversationStore = defineStore('conversation', () => {
  // 状态
  const conversations = ref<Conversation[]>([])
  const currentSessionId = ref<string>('')
  const messages = ref<Message[]>([])
  const loading = ref(false)

  // 计算属性
  const currentConversation = computed(() => {
    return conversations.value.find(conv => conv.session_id === currentSessionId.value)
  })

  const hasConversations = computed(() => {
    return conversations.value.length > 0
  })

  // 方法
  const loadConversations = async () => {
    loading.value = true
    try {
      conversations.value = await chatService.getConversations()
    } catch (error) {
      console.error('加载对话列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const loadMessages = async (sessionId: string) => {
    loading.value = true
    try {
      messages.value = await chatService.getMessageHistory(sessionId)
    } catch (error) {
      console.error('加载消息历史失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const switchConversation = async (sessionId: string) => {
    if (sessionId === currentSessionId.value) return

    currentSessionId.value = sessionId
    chatService.switchSession(sessionId)
    await loadMessages(sessionId)
  }

  const createNewConversation = () => {
    const newSessionId = chatService.getCurrentSessionId()
    currentSessionId.value = newSessionId
    chatService.switchSession()
    messages.value = []
    
    // 重新加载对话列表以获取最新状态
    loadConversations()
  }

  const deleteConversation = async (sessionId: string) => {
    try {
      const success = await chatService.deleteConversation(sessionId)
      if (success) {
        // 从本地列表中移除
        conversations.value = conversations.value.filter(conv => conv.session_id !== sessionId)
        
        // 如果删除的是当前对话，创建新对话
        if (sessionId === currentSessionId.value) {
          createNewConversation()
        }
      }
      return success
    } catch (error) {
      console.error('删除对话失败:', error)
      throw error
    }
  }

  const searchMessages = async (query: string, sessionId?: string) => {
    try {
      return await chatService.searchMessages(query, sessionId)
    } catch (error) {
      console.error('搜索消息失败:', error)
      throw error
    }
  }

  const addMessage = (message: Message) => {
    messages.value.push(message)
  }

  const updateConversation = (sessionId: string, updates: Partial<Conversation>) => {
    const index = conversations.value.findIndex(conv => conv.session_id === sessionId)
    if (index !== -1) {
      conversations.value[index] = { ...conversations.value[index], ...updates }
    }
  }

  // 初始化
  const initialize = async () => {
    try {
      await loadConversations()
      
      // 如果没有对话历史，创建新对话
      if (conversations.value.length === 0) {
        createNewConversation()
      } else {
        // 使用最新的对话作为当前对话
        const latestConversation = conversations.value[0]
        await switchConversation(latestConversation.session_id)
      }
    } catch (error) {
      console.error('初始化对话状态失败:', error)
      // 即使加载失败也创建新对话
      createNewConversation()
    }
  }

  return {
    // 状态
    conversations,
    currentSessionId,
    messages,
    loading,

    // 计算属性
    currentConversation,
    hasConversations,

    // 方法
    loadConversations,
    loadMessages,
    switchConversation,
    createNewConversation,
    deleteConversation,
    searchMessages,
    addMessage,
    updateConversation,
    initialize
  }
})
