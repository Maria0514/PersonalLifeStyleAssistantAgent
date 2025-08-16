import { ElNotification, ElMessageBox } from 'element-plus'
import type { Reminder } from './chatService'
import type ChatService from './chatService'

export class ReminderService {
  private checkInterval: number = 60000 // 1分钟检查一次
  private timer: number | null = null
  private chatService: ChatService
  private isChecking: boolean = false
  private notifiedReminders: Set<number> = new Set() // 避免重复通知

  constructor(chatService: ChatService) {
    this.chatService = chatService
  }

  /**
   * 开始监控提醒
   */
  start() {
    if (this.timer) {
      clearInterval(this.timer)
    }
    
    this.timer = setInterval(() => {
      this.checkReminders()
    }, this.checkInterval)
    
    // 立即执行一次检查
    this.checkReminders()
    
    console.log('🔔 提醒监控已启动')
  }

  /**
   * 停止监控提醒
   */
  stop() {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
    console.log('🔕 提醒监控已停止')
  }

  /**
   * 检查即将到期的提醒
   */
  private async checkReminders() {
    if (this.isChecking) return
    
    this.isChecking = true
    
    try {
      // 检查未来5分钟内的提醒
      const upcomingReminders = await this.chatService.getUpcomingReminders(5)
      console.log('获取到的提醒数据:', upcomingReminders) // 调试日志
      
      upcomingReminders.forEach((reminder: Reminder) => {
        console.log('处理提醒:', reminder) // 调试日志
        this.processReminder(reminder)
      })
    } catch (error) {
      console.error('检查提醒失败:', error)
    } finally {
      this.isChecking = false
    }
  }

  /**
   * 处理单个提醒
   */
  private processReminder(reminder: Reminder) {
    // 数据验证 - 确保必要字段存在
    if (!reminder || !reminder.id || !reminder.title || !reminder.due_date) {
      console.warn('无效的提醒数据:', reminder)
      return
    }

    // 避免重复通知
    if (this.notifiedReminders.has(reminder.id)) {
      return
    }

    const now = new Date()
    const dueDate = new Date(reminder.due_date)
    const timeDiff = dueDate.getTime() - now.getTime()
    const minutesLeft = Math.floor(timeDiff / (1000 * 60))

    // 根据剩余时间确定是否需要提醒
    if (this.shouldNotify(minutesLeft)) {
      this.showReminderNotification(reminder, minutesLeft)
      this.notifiedReminders.add(reminder.id)
    }
  }

  /**
   * 判断是否应该发送通知
   */
  private shouldNotify(minutesLeft: number): boolean {
    // 提醒时机：1小时前、30分钟前、10分钟前、5分钟前、准时、过期
    const notifyTimes = [60, 30, 10, 5, 0, -10, -30, -60]
    return notifyTimes.some(time => Math.abs(minutesLeft - time) < 1)
  }

  /**
   * 显示提醒通知
   */
  private showReminderNotification(reminder: Reminder, minutesLeft: number) {
    const title = this.getNotificationTitle(minutesLeft)
    const type = this.getNotificationType(minutesLeft)

    // 确保描述字段处理
    const description = reminder.description || '无描述'
    
    // 创建一个安全的提醒对象副本
    const safeReminder = {
      id: reminder.id,
      title: reminder.title || '未知提醒',
      description: description,
      due_date: reminder.due_date,
      priority: reminder.priority || 'medium',
      status: reminder.status || 'pending'
    }

    console.log('显示提醒通知:', safeReminder) // 调试日志

    ElNotification({
      title,
      message: `📅 ${safeReminder.title}${description !== '无描述' ? '\n📝 ' + description : ''}`,
      type,
      duration: 0, // 不自动关闭
      dangerouslyUseHTMLString: false,
      showClose: true,
      position: 'bottom-right', // 修改为底部右侧，避免遮挡页面顶部
      customClass: 'reminder-notification',
      offset: 20, // 添加偏移量，确保不贴边
      onClick: () => {
        console.log('点击了提醒通知:', safeReminder) // 调试日志
        this.handleReminderClick(safeReminder)
      }
    })

    // 播放提醒声音（如果浏览器允许）
    this.playNotificationSound()
  }

  /**
   * 获取通知标题
   */
  private getNotificationTitle(minutesLeft: number): string {
    if (minutesLeft > 30) return '🕐 即将到期提醒'
    if (minutesLeft > 10) return '⏰ 30分钟内提醒'
    if (minutesLeft > 0) return '🚨 10分钟内提醒'
    if (minutesLeft === 0) return '⏱️ 时间到了！'
    return '🔴 逾期提醒'
  }

  /**
   * 获取通知类型
   */
  private getNotificationType(minutesLeft: number): 'info' | 'warning' | 'error' {
    if (minutesLeft > 10) return 'info'
    if (minutesLeft >= 0) return 'warning'
    return 'error'
  }

  /**
   * 处理提醒点击事件
   */
  private async handleReminderClick(reminder: Partial<Reminder> & { id: number; title: string }) {
    try {
      console.log('处理提醒点击:', reminder) // 调试日志
      
      const result = await ElMessageBox.confirm(
        `提醒：${reminder.title}\n${reminder.description || ''}\n\n您想要执行什么操作？`,
        '提醒处理',
        {
          confirmButtonText: '标记完成',
          cancelButtonText: '延迟10分钟',
          distinguishCancelAndClose: true,
          type: 'warning',
          center: true, // 居中显示
          closeOnClickModal: false, // 防止意外关闭
          closeOnPressEscape: true,
          showClose: true
        }
      )

      // 用户点击"标记完成"
      console.log('用户选择标记完成') // 调试日志
      const success = await this.chatService.completeReminder(reminder.id)
      if (success) {
        ElNotification.success({
          title: '操作成功',
          message: '提醒已标记为完成'
        })
        this.notifiedReminders.delete(reminder.id)
      } else {
        ElNotification.error({
          title: '操作失败',
          message: '无法标记提醒为完成'
        })
      }
    } catch (action) {
      console.log('用户操作:', action) // 调试日志
      // 处理用户的不同操作
      if (action === 'cancel') {
        // 用户点击"延迟10分钟"
        console.log('用户选择延迟10分钟') // 调试日志
        const success = await this.chatService.snoozeReminder(reminder.id, 10)
        if (success) {
          ElNotification.success({
            title: '操作成功',
            message: '提醒已延迟10分钟'
          })
          this.notifiedReminders.delete(reminder.id) // 允许重新通知
        } else {
          ElNotification.error({
            title: '操作失败',
            message: '无法延迟提醒'
          })
        }
      } else if (action === 'close') {
        // 用户点击关闭按钮或按ESC键，不做任何操作
        console.log('用户关闭了提醒对话框')
      }
      // 其他情况（如点击遮罩层）也不做处理
    }
  }

  /**
   * 播放通知声音
   */
  private playNotificationSound() {
    try {
      // 创建简单的提醒音
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)

      oscillator.frequency.value = 800
      oscillator.type = 'sine'

      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)

      oscillator.start(audioContext.currentTime)
      oscillator.stop(audioContext.currentTime + 0.3)
    } catch (error) {
      // 忽略音频播放错误
      console.debug('无法播放提醒声音:', error)
    }
  }

  /**
   * 清除通知记录（用于重置）
   */
  clearNotifiedReminders() {
    this.notifiedReminders.clear()
  }
}
