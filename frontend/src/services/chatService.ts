// API配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 提醒接口定义
export interface Reminder {
  id: number
  title: string
  description?: string
  due_date: string
  priority: 'high' | 'medium' | 'low'
  status: 'pending' | 'complete'
  created_at: string
  updated_at: string
  completed_at?: string
}

// 元数据接口定义
export interface ChatMetadata {
  tokens_used: number
  response_time: number
  confidence?: number
}

// 响应接口定义
export interface ChatResponse {
  message: string
  success: boolean
  metadata?: ChatMetadata
  error?: string
}

// 对话会话接口定义
export interface Conversation {
  id: number
  session_id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

// 消息接口定义
export interface Message {
  id: number
  session_id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  tool_used?: string
}

// 聊天服务类
class ChatService {
  private baseUrl: string
  private sessionId: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
    // 生成基于日期的会话ID，页面刷新前保持不变
    this.sessionId = this.generateSessionId()
  }

  /**
   * 生成会话ID
   * @returns 基于日期的会话ID
   */
  private generateSessionId(): string {
    const now = new Date()
    const dateStr = now.toISOString().split('T')[0] // YYYY-MM-DD
    const timeStr = now.getTime().toString().slice(-6) // 取时间戳后6位
    return `session_${dateStr}_${timeStr}`
  }

  /**
   * 获取当前会话ID
   * @returns 当前会话ID
   */
  getSessionId(): string {
    return this.sessionId
  }

  /**
   * 重置会话（生成新的会话ID）
   */
  resetSession(): void {
    this.sessionId = this.generateSessionId()
  }

  /**
   * 获取即将到期的提醒
   * @param minutesAhead 提前多少分钟检查
   * @returns Promise<Reminder[]>
   */
  async getUpcomingReminders(minutesAhead: number = 60): Promise<Reminder[]> {
    try {
      const response = await fetch(`${this.baseUrl}/reminders/upcoming?minutes_ahead=${minutesAhead}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.upcoming || []
    } catch (error) {
      console.error('获取即将到期提醒失败:', error)
      
      // 在开发环境中返回模拟数据
      if (import.meta.env.DEV) {
        return this.getMockReminders(minutesAhead)
      }
      
      return []
    }
  }

  /**
   * 标记提醒为完成
   * @param reminderId 提醒ID
   * @returns Promise<boolean>
   */
  async completeReminder(reminderId: number): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/reminders/${reminderId}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      return response.ok
    } catch (error) {
      console.error('完成提醒失败:', error)
      
      // 在开发环境中模拟成功
      if (import.meta.env.DEV) {
        console.log(`模拟完成提醒 ID: ${reminderId}`)
        return true
      }
      
      return false
    }
  }

  /**
   * 延迟提醒
   * @param reminderId 提醒ID
   * @param minutes 延迟分钟数
   * @returns Promise<boolean>
   */
  async snoozeReminder(reminderId: number, minutes: number = 10): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/reminders/${reminderId}/snooze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ minutes })
      })
      return response.ok
    } catch (error) {
      console.error('延迟提醒失败:', error)
      
      // 在开发环境中模拟成功
      if (import.meta.env.DEV) {
        console.log(`模拟延迟提醒 ID: ${reminderId}, 延迟 ${minutes} 分钟`)
        return true
      }
      
      return false
    }
  }

  /**
   * 发送消息到后端
   * @param message 用户输入的消息
   * @returns Promise<ChatResponse>
   */
  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          timestamp: new Date().toISOString(),
          session_id: this.sessionId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      return {
        message: data.response || data.message || '抱歉，我没有理解您的问题。',
        success: true,
        metadata: data.metadata ? {
          tokens_used: data.metadata.tokens_used || 0,
          response_time: data.metadata.response_time || 0,
          confidence: data.metadata.confidence
        } : undefined
      }
    } catch (error) {
      console.error('发送消息失败:', error)
      
      // 在开发环境中，返回模拟响应
      if (import.meta.env.DEV) {
        return this.getMockResponse(message)
      }
      
      return {
        message: '抱歉，连接服务器失败，请检查网络连接或稍后再试。',
        success: false,
        error: error instanceof Error ? error.message : '未知错误'
      }
    }
  }

  /**
   * 开发环境模拟响应
   * @param message 用户消息
   * @returns 模拟的响应
   */
  private getMockResponse(message: string): ChatResponse {
    const lowerMessage = message.toLowerCase()
    
    // 天气查询模拟
    if (lowerMessage.includes('天气')) {
      return {
        message: '今天北京天气晴朗，气温23°C，适合外出活动。建议您穿着舒适的春秋装。',
        success: true
      }
    }
    
    // 计算器模拟
    if (lowerMessage.includes('计算') || /[\d+\-*/]/.test(message)) {
      // 简单的数学表达式计算
      try {
        const result = this.calculateExpression(message)
        return {
          message: `计算结果：${result}`,
          success: true
        }
      } catch {
        return {
          message: '抱歉，我无法理解这个计算请求。请提供更清晰的数学表达式，例如：15 + 23 或者 100 * 0.8',
          success: true
        }
      }
    }
    
    // 提醒设置模拟
    if (lowerMessage.includes('提醒')) {
      return {
        message: '我已经帮您记录了这个提醒需求。不过目前提醒功能还在开发中，建议您先使用手机自带的提醒功能或者日历应用来设置重要提醒。',
        success: true
      }
    }
    
    // 默认响应
    const responses = [
      '我理解您的问题。作为您的个人生活助理，我可以帮您查询天气、进行数学计算、设置提醒等。请告诉我具体需要什么帮助？',
      '很高兴为您服务！我可以协助处理各种日常生活事务，比如天气查询、计算问题、提醒管理等。有什么我可以帮您的吗？',
      '感谢您的提问！我是您的智能生活助理，擅长处理实用的生活问题。请告诉我您需要什么类型的帮助？'
    ]
    
    const randomResponse = responses[Math.floor(Math.random() * responses.length)]
    
    return {
      message: randomResponse,
      success: true
    }
  }

  /**
   * 开发环境模拟提醒数据
   * @param minutesAhead 提前多少分钟检查
   * @returns 模拟的提醒数据
   */
  private getMockReminders(minutesAhead: number): Reminder[] {
    const now = new Date()
    const mockReminders: Reminder[] = []

    // 创建一些测试提醒
    const testReminders = [
      {
        title: '喝水提醒',
        description: '记得多喝水，保持身体健康',
        minutesFromNow: 5,
        priority: 'medium' as const
      },
      {
        title: '会议提醒',
        description: '下午3点的项目讨论会议',
        minutesFromNow: 15,
        priority: 'high' as const
      },
      {
        title: '运动时间',
        description: '今天的健身计划：30分钟跑步',
        minutesFromNow: 30,
        priority: 'medium' as const
      },
      {
        title: '买菜提醒',
        description: '下班路上去超市买菜',
        minutesFromNow: 45,
        priority: 'low' as const
      }
    ]

    testReminders.forEach((reminder, index) => {
      if (reminder.minutesFromNow <= minutesAhead) {
        const dueDate = new Date(now.getTime() + reminder.minutesFromNow * 60 * 1000)
        
        mockReminders.push({
          id: index + 1,
          title: reminder.title,
          description: reminder.description,
          due_date: dueDate.toISOString(),
          priority: reminder.priority,
          status: 'pending',
          created_at: now.toISOString(),
          updated_at: now.toISOString()
        })
      }
    })

    return mockReminders
  }

  /**
   * 简单的数学表达式计算
   * @param message 包含数学表达式的消息
   * @returns 计算结果
   */
  private calculateExpression(message: string): string {
    // 提取数字和运算符
    const mathExpression = message.match(/[\d+\-*/.() ]+/g)?.[0]?.trim()
    
    if (!mathExpression) {
      throw new Error('No valid expression found')
    }
    
    // 安全的数学表达式求值
    try {
      // 简单的四则运算支持
      const sanitized = mathExpression.replace(/[^0-9+\-*/.() ]/g, '')
      
      // 使用Function构造器进行安全计算
      const result = Function(`"use strict"; return (${sanitized})`)()
      
      if (typeof result === 'number' && isFinite(result)) {
        return result.toString()
      } else {
        throw new Error('Invalid calculation result')
      }
    } catch {
      throw new Error('Calculation failed')
    }
  }

  /**
   * 健康检查
   * @returns Promise<boolean>
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        timeout: 5000
      } as RequestInit)
      
      return response.ok
    } catch {
      return false
    }
  }

  // ================== 对话历史相关方法 ==================

  /**
   * 获取当前会话ID
   * @returns 当前会话ID
   */
  getCurrentSessionId(): string {
    return this.sessionId
  }

  /**
   * 切换到新的会话
   * @param sessionId 可选的会话ID，不提供则生成新的
   */
  switchSession(sessionId?: string): void {
    this.sessionId = sessionId || this.generateSessionId()
  }

  /**
   * 获取所有对话会话列表
   * @returns Promise<Conversation[]>
   */
  async getConversations(): Promise<Conversation[]> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch conversations')
      }

      const data = await response.json()
      return data.conversations || []
    } catch (error) {
      console.error('获取对话列表失败:', error)
      
      // 在开发环境中返回模拟数据
      if (import.meta.env.DEV) {
        return [
          {
            id: 1,
            session_id: 'session_2025-08-16_123456',
            title: '天气查询和提醒设置',
            created_at: '2025-08-16T10:30:00.000Z',
            updated_at: '2025-08-16T11:45:00.000Z',
            message_count: 8
          },
          {
            id: 2,
            session_id: 'session_2025-08-15_654321',
            title: '数学计算和记账建议',
            created_at: '2025-08-15T14:20:00.000Z',
            updated_at: '2025-08-15T15:30:00.000Z',
            message_count: 12
          }
        ]
      }
      
      return []
    }
  }

  /**
   * 获取特定会话的消息历史
   * @param sessionId 会话ID
   * @param limit 返回消息数量限制，默认50
   * @param offset 偏移量，用于分页，默认0
   * @returns Promise<Message[]>
   */
  async getMessageHistory(sessionId: string, limit: number = 50, offset: number = 0): Promise<Message[]> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations/${sessionId}/messages?limit=${limit}&offset=${offset}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch message history')
      }

      const data = await response.json()
      return data.messages || []
    } catch (error) {
      console.error('获取消息历史失败:', error)
      
      // 在开发环境中返回模拟数据
      if (import.meta.env.DEV && sessionId === 'session_2025-08-16_123456') {
        return [
          {
            id: 1,
            session_id: sessionId,
            role: 'user',
            content: '今天天气怎么样？',
            timestamp: '2025-08-16T10:30:00.000Z'
          },
          {
            id: 2,
            session_id: sessionId,
            role: 'assistant',
            content: '今天北京天气晴朗，气温25°C，适合外出活动。',
            timestamp: '2025-08-16T10:30:15.000Z',
            tool_used: 'weather'
          },
          {
            id: 3,
            session_id: sessionId,
            role: 'user',
            content: '帮我设置一个下午3点的会议提醒',
            timestamp: '2025-08-16T11:40:00.000Z'
          },
          {
            id: 4,
            session_id: sessionId,
            role: 'assistant',
            content: '好的，我已经为您设置了今天下午3点的会议提醒。',
            timestamp: '2025-08-16T11:40:10.000Z',
            tool_used: 'reminder'
          }
        ]
      }
      
      return []
    }
  }

  /**
   * 删除对话会话
   * @param sessionId 会话ID
   * @returns Promise<boolean>
   */
  async deleteConversation(sessionId: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      return response.ok
    } catch (error) {
      console.error('删除对话失败:', error)
      
      // 在开发环境中模拟成功
      if (import.meta.env.DEV) {
        console.log(`模拟删除对话: ${sessionId}`)
        return true
      }
      
      return false
    }
  }

  /**
   * 搜索消息历史
   * @param query 搜索关键词
   * @param sessionId 可选的会话ID，不提供则搜索所有会话
   * @returns Promise<Message[]>
   */
  async searchMessages(query: string, sessionId?: string): Promise<Message[]> {
    try {
      const url = sessionId 
        ? `${this.baseUrl}/conversations/${sessionId}/search?q=${encodeURIComponent(query)}`
        : `${this.baseUrl}/messages/search?q=${encodeURIComponent(query)}`
        
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error('Failed to search messages')
      }

      const data = await response.json()
      return data.messages || []
    } catch (error) {
      console.error('搜索消息失败:', error)
      
      // 在开发环境中返回模拟搜索结果
      if (import.meta.env.DEV) {
        return [
          {
            id: 1,
            session_id: 'session_2025-08-16_123456',
            role: 'user',
            content: query.includes('天气') ? '今天天气怎么样？' : '相关消息内容',
            timestamp: '2025-08-16T10:30:00.000Z'
          }
        ]
      }
      
      return []
    }
  }
}

// 导出单例实例
export const chatService = new ChatService()

// 导出类型和服务
export default ChatService
