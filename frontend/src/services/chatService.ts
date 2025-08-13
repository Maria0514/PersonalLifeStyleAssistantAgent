// API配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 响应接口定义
export interface ChatResponse {
  message: string
  success: boolean
  error?: string
}

// 聊天服务类
class ChatService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
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
          timestamp: new Date().toISOString()
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      return {
        message: data.response || data.message || '抱歉，我没有理解您的问题。',
        success: true
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
    
    // 记账建议模拟
    if (lowerMessage.includes('记账')) {
      return {
        message: `记账建议：
1. 建议使用分类记账法，将支出分为必需品、娱乐、投资等类别
2. 每天记录支出，养成良好的财务习惯
3. 设定月度预算，控制各类支出在合理范围内
4. 定期回顾财务状况，调整消费计划
5. 考虑使用记账APP来简化记录过程`,
        success: true
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
      '我理解您的问题。作为您的个人生活助理，我可以帮您查询天气、进行数学计算、提供记账建议等。请告诉我具体需要什么帮助？',
      '很高兴为您服务！我可以协助处理各种日常生活事务，比如天气查询、计算问题、理财建议等。有什么我可以帮您的吗？',
      '感谢您的提问！我是您的智能生活助理，擅长处理实用的生活问题。请告诉我您需要什么类型的帮助？'
    ]
    
    const randomResponse = responses[Math.floor(Math.random() * responses.length)]
    
    return {
      message: randomResponse,
      success: true
    }
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
}

// 导出单例实例
export const chatService = new ChatService()

// 导出类型和服务
export default ChatService
