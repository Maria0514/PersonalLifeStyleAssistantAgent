# Personal Lifestyle Assistant Agent - API 接口文档

## 📋 接口概览

本文档描述了个人生活助理Agent的前后端API接口规范。前端Vue3应用通过这些接口与FastAPI后端进行通信。

### 🏗️ 系统架构

```
Vue 3 前端 (http://localhost:5173)
    ↕ HTTP/JSON
FastAPI 后端 (http://localhost:8000)
    ↕ 
LangChain Agent + Tools
```

### 🌟 核心功能

- ✅ **智能对话**: 基于LangChain的AI助理对话
- ✅ **工具集成**: 计算器、搜索、记忆、提醒等多种工具
- ✅ **会话管理**: 支持多会话和上下文保持
- ⭐ **提醒系统**: 完整的任务提醒和通知功能
- 🔧 **开发友好**: 完善的模拟数据和测试支持

### 📊 当前状态

| 功能模块 | 状态 | 版本 | 说明 |
|---------|------|------|------|
| 基础对话 | ✅ 完成 | v1.0.0 | 支持多轮对话 |
| 会话管理 | ✅ 完成 | v1.1.0 | 会话ID和上下文 |
| 提醒功能 | ⭐ 新增 | v1.2.0 | 完整提醒系统 |
| 工具系统 | ✅ 完成 | v1.0.0+ | 4种核心工具 |
const session### 📊 性能指标

### 会话管理性能

- **会话创建时间**: <### 📝 更新日志

### v1.1.0 (2025-08-14)
- ✅ 添加会话管理功能
- ✅ 前端支持会话ID自动生成和管理
- ✅ 支持新建会话功能
- ✅ 优化对话上下文保持
- 🔧 修复会话断续问题

### v1.0.0 (2025-08-13)ms
- **会话切换响应**: < 50ms
- **内存中同时维护的会话数**: 建议 < 1000个
- **单个会话最大消息数**: 建议 < 500条

### API 性能指标= `session_${YYYY-MM-DD}_${timestamp_suffix}`
// 示例：session_2025-08-14_456789
```

#### **会话生命周期**
- **页面加载时**：自动生成新的会话ID
- **对话期间**：所有消息使用相同的会话ID
- **新建会话**：用户主动点击"新对话"按钮生成新会话ID
- **页面刷新**：生成新的会话ID，之前的对话上下文会丢失

#### **前端会话管理接口**
```typescript
// 获取当前会话ID
const currentSessionId = chatService.getSessionId()

// 重置会话（生成新会话ID）
chatService.resetSession()

// 发送消息（自动包含会话ID）
const response = await chatService.sendMessage(message)
```

### 环境配置00)
    ↕ 
LangChain Agent + Tools
```

---

## 🌐 基础信息

- **Base URL**: `http://localhost:8000` (开发环境)
- **Content-Type**: `application/json`
- **响应格式**: JSON
- **字符编码**: UTF-8

---

## 📡 API 接口列表

### 1. 发送消息接口

与AI助理进行对话的核心接口。

**接口地址**: `POST /message`

**请求参数**:
```json
{
  "message": "string",      // 用户输入的消息内容
  "timestamp": "string",    // ISO 8601格式的时间戳 (可选)
  "session_id": "string"    // 会话ID，用于维持对话上下文 (可选)
}
```

**请求示例**:
```json
{
  "message": "今天的天气怎么样？",
  "timestamp": "2025-08-14T12:30:00.000Z",
  "session_id": "session_2025-08-14_456789"
}
```

**响应格式**:
```json
{
  "message": "string",      // AI助理的回复内容
  "success": true,          // 请求是否成功
  "tool_used": "string",    // 使用的工具ID (可选)
  "metadata": {             // 元数据 (可选)
    "tokens_used": 150,
    "response_time": 1.23,
  }
}
```

**成功响应示例**:
```json
{
  "message": "今天北京天气晴朗，气温23°C，适合外出活动。建议您穿着舒适的春秋装。",
  "success": true,
  "tool_used": ["search_online"],
  "metadata": {
    "tokens_used": 45,
    "response_time": 0.85
  }
}
```

**错误响应示例**:
```json
{
  "message": "抱歉，我现在无法处理您的请求，请稍后再试。",
  "success": false,
  "error": "Internal server error",
  "error_code": "SERVER_ERROR"
}
```

**状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `429`: 请求频率过高
- `500`: 服务器内部错误

---

---

### 2. 对话历史管理接口

用于管理和获取对话历史记录的接口组。

#### 2.1 获取对话会话列表

**接口地址**: `GET /conversations`

**请求参数**: 无

**响应格式**:
```json
{
  "conversations": [
    {
      "id": 1,
      "session_id": "string",
      "title": "string",
      "created_at": "string",
      "updated_at": "string", 
      "message_count": 10
    }
  ],
  "total": 5
}
```

**响应示例**:
```json
{
  "conversations": [
    {
      "id": 1,
      "session_id": "session_2025-08-16_123456",
      "title": "天气查询和提醒设置",
      "created_at": "2025-08-16T10:30:00.000Z",
      "updated_at": "2025-08-16T11:45:00.000Z",
      "message_count": 8
    }
  ],
  "total": 1
}
```

#### 2.2 获取消息历史

**接口地址**: `GET /conversations/{session_id}/messages`

**请求参数**:
- `session_id` (path): 会话ID
- `limit` (query): 返回消息数量限制，默认50
- `offset` (query): 偏移量，用于分页，默认0

**响应格式**:
```json
{
  "messages": [
    {
      "id": 1,
      "session_id": "string",
      "role": "user|assistant",
      "content": "string",
      "timestamp": "string",
      "tool_used": "string"
    }
  ],
  "total": 100,
  "has_more": true
}
```

**响应示例**:
```json
{
  "messages": [
    {
      "id": 1,
      "session_id": "session_2025-08-16_123456",
      "role": "user",
      "content": "今天天气怎么样？",
      "timestamp": "2025-08-16T10:30:00.000Z"
    },
    {
      "id": 2,
      "session_id": "session_2025-08-16_123456", 
      "role": "assistant",
      "content": "今天北京天气晴朗，气温25°C，适合外出活动。",
      "timestamp": "2025-08-16T10:30:15.000Z",
      "tool_used": "weather"
    }
  ],
  "total": 8,
  "has_more": false
}
```

#### 2.3 删除对话会话

**接口地址**: `DELETE /conversations/{session_id}`

**请求参数**:
- `session_id` (path): 会话ID

**响应格式**:
```json
{
  "success": true,
  "message": "对话已删除"
}
```

#### 2.4 搜索消息

**接口地址**: `GET /conversations/{session_id}/search` 或 `GET /messages/search`

**请求参数**:
- `session_id` (path, 可选): 会话ID，如果提供则只在该会话中搜索
- `q` (query): 搜索关键词

**响应格式**:
```json
{
  "messages": [
    {
      "id": 1,
      "session_id": "string",
      "role": "user|assistant", 
      "content": "string",
      "timestamp": "string",
      "tool_used": "string"
    }
  ],
  "total": 5
}
```

---

### 3. 健康检查接口

检查服务器运行状态和各组件健康状况。

**接口地址**: `GET /health`

**请求参数**: 无

**响应格式**:
```json
{
  "status": "string",       // 服务状态: "healthy" | "degraded" | "unhealthy"
  "timestamp": "string",    // 检查时间戳
  "version": "string",      // 服务版本
  "components": {           // 各组件状态
    "database": "healthy",
    "langchain": "healthy",
    "tools": {
      "search": "healthy",
      "calculator": "healthy",
      "memory": "healthy",
      "reminder": "healthy"
    }
  },
  "uptime": 3600           // 服务运行时间(秒)
}
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-13T12:30:00.000Z",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "langchain": "healthy",
    "tools": {
      "search": "healthy",
      "calculator": "healthy", 
      "memory": "healthy",
      "reminder": "healthy"
    }
  },
  "uptime": 3600
}
```

**状态码**:
- `200`: 服务健康
- `503`: 服务不可用

---

### 4. 获取即将到期提醒接口 ⭐ 新增

获取用户即将到期的提醒列表，支持时间范围筛选。

**接口地址**: `GET /reminders/upcoming`

**请求参数**:
- `minutes_ahead`: 提前多少分钟检查 (可选，默认60分钟)

**请求示例**:
```http
GET /reminders/upcoming?minutes_ahead=60
```

**响应格式**:
```json
{
  "upcoming": [
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "due_date": "2025-08-15T14:30:00.000Z",
      "priority": "high|medium|low",
      "status": "pending|complete",
      "created_at": "2025-08-15T12:00:00.000Z",
      "updated_at": "2025-08-15T12:00:00.000Z",
      "completed_at": "2025-08-15T13:00:00.000Z"
    }
  ],
  "count": 3,
  "total_upcoming": 5
}
```

**成功响应示例**:
```json
{
  "upcoming": [
    {
      "id": 1,
      "title": "喝水提醒",
      "description": "记得多喝水，保持身体健康",
      "due_date": "2025-08-15T14:35:00.000Z",
      "priority": "medium",
      "status": "pending",
      "created_at": "2025-08-15T12:00:00.000Z",
      "updated_at": "2025-08-15T12:00:00.000Z"
    },
    {
      "id": 2,
      "title": "会议提醒",
      "description": "下午3点的项目讨论会议",
      "due_date": "2025-08-15T15:00:00.000Z",
      "priority": "high",
      "status": "pending",
      "created_at": "2025-08-15T12:00:00.000Z",
      "updated_at": "2025-08-15T12:00:00.000Z"
    }
  ],
  "count": 2,
  "total_upcoming": 2
}
```

**状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

---

### 5. 完成提醒接口 ⭐ 新增

标记指定提醒为已完成状态。

**接口地址**: `POST /reminders/{reminder_id}/complete`

**路径参数**:
- `reminder_id`: 提醒ID (必需)

**请求示例**:
```http
POST /reminders/1/complete
```

**响应格式**:
```json
{
  "success": true,
  "message": "提醒已标记为完成",
  "reminder": {
    "id": 1,
    "title": "string",
    "status": "complete",
    "completed_at": "2025-08-15T14:30:00.000Z"
  }
}
```

**错误响应示例**:
```json
{
  "success": false,
  "error": "提醒不存在或已完成",
  "error_code": "REMINDER_NOT_FOUND"
}
```

**状态码**:
- `200`: 成功
- `404`: 提醒不存在
- `400`: 提醒已完成
- `500`: 服务器内部错误

---

### 6. 延迟提醒接口 ⭐ 新增

延迟指定提醒的到期时间。

**接口地址**: `POST /reminders/{reminder_id}/snooze`

**路径参数**:
- `reminder_id`: 提醒ID (必需)

**请求参数**:
```json
{
  "minutes": 10        // 延迟分钟数 (默认10分钟)
}
```

**请求示例**:
```http
POST /reminders/1/snooze

{
  "minutes": 15
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "提醒已延迟15分钟",
  "reminder": {
    "id": 1,
    "title": "string",
    "due_date": "2025-08-15T14:45:00.000Z",
    "updated_at": "2025-08-15T14:30:00.000Z"
  }
}
```

**错误响应示例**:
```json
{
  "success": false,
  "error": "提醒不存在或已完成",
  "error_code": "REMINDER_NOT_AVAILABLE"
}
```

**状态码**:
- `200`: 成功
- `404`: 提醒不存在
- `400`: 请求参数错误或提醒已完成
- `500`: 服务器内部错误

---

### 6. 获取对话历史接口 (规划中)

获取用户的历史对话记录。

**接口地址**: `GET /conversations`

**请求参数**:
- `limit`: 返回记录数量 (可选，默认20)
- `offset`: 分页偏移量 (可选，默认0)
- `session_id`: 会话ID (可选)

**响应格式**:
```json
{
  "conversations": [
    {
      "id": "string",
      "user_message": "string",
      "bot_response": "string", 
      "timestamp": "string",
      "tool_used": "string"
    }
  ],
  "total": 100,
  "has_more": true
}
```

---

### 7. 重置对话接口 (规划中)

清除当前会话的记忆和上下文。

**接口地址**: `POST /reset`

**请求参数**:
```json
{
  "session_id": "string"   // 会话ID (可选)
}
```

**响应格式**:
```json
{
  "success": true,
  "message": "对话历史已重置"
}
```

---

## 🛠️ 工具系统

AI助理支持以下工具，会根据用户输入自动选择使用：

### 工具列表

| 工具ID | 工具名称 | 功能描述 | 触发关键词 | 状态 |
|--------|----------|----------|------------|------|
| `search` | 网络搜索 | 搜索实时信息、天气查询 | 天气、搜索、查询 | ✅ 已实现 |
| `calculator` | 计算器 | 数学计算和表达式求值 | 计算、数字、运算符 | ✅ 已实现 |
| `memory` | 记忆系统 | 记录和回忆对话上下文 | 记住、之前、回忆 | ⚠️ 开发中 |
| `reminder` | 提醒工具 | 设置时间提醒和任务管理 | 提醒、闹钟、定时、任务 | ⭐ 新增 |

### 提醒工具详细说明 ⭐

提醒工具支持以下功能：

#### **添加提醒**
- 支持自然语言解析时间
- 支持优先级设置（高/中/低）
- 支持描述信息添加

#### **查询提醒**
- 按时间范围查询
- 按优先级筛选
- 按状态筛选

#### **提醒管理**
- 标记完成
- 延迟提醒
- 修改提醒内容

#### **智能通知**
- 多时间点提醒（1小时前、30分钟前、10分钟前、准时）
- 逾期提醒
- 声音提醒

### 工具使用流程

1. 用户发送消息
2. Agent分析消息内容
3. 选择合适的工具
4. 执行工具功能
5. 基于工具结果生成回复

### 提醒工具使用示例

**用户输入**: "提醒我明天下午3点开会"
**工具调用**: `reminder.add_reminder`
**参数**: 
```json
{
  "title": "开会",
  "due_date": "2025-08-16T15:00:00.000Z",
  "priority": "medium"
}
```
**AI回复**: "好的，我已经为您设置了明天下午3点的开会提醒。"

---

## 🔧 前端集成说明

### 提醒功能集成 ⭐ 新增

前端已集成完整的提醒功能系统：

#### **提醒服务架构**
```typescript
import { ReminderService } from '@/services/reminderService'
import { chatService } from '@/services/chatService'

// 初始化提醒服务
const reminderService = new ReminderService(chatService)

// 启动自动监控
reminderService.start()
```

#### **提醒功能特性**
- ✅ **自动监控**: 每60秒检查即将到期的提醒
- ✅ **智能通知**: 1小时前、30分钟前、10分钟前、准时、逾期多时间点提醒
- ✅ **ElementPlus集成**: 美观的通知UI和交互对话框
- ✅ **声音提醒**: Web Audio API生成的提醒音效
- ✅ **防重复通知**: 避免同一提醒重复弹出
- ✅ **用户交互**: 点击通知可完成或延迟提醒

#### **前端提醒接口**
```typescript
// 获取即将到期的提醒
const upcomingReminders = await chatService.getUpcomingReminders(60)

// 完成提醒
const success = await chatService.completeReminder(reminderId)

// 延迟提醒
const success = await chatService.snoozeReminder(reminderId, 10)

// 手动检查提醒（点击头部提醒徽章）
reminderService.checkReminders()
```

#### **通知样式定制**
```typescript
// 提醒通知配置
ElNotification({
  title: '⏰ 即将到期提醒',
  message: '📅 会议提醒\n📝 下午3点的项目讨论会议',
  type: 'warning',
  duration: 0,          // 不自动关闭
  position: 'top-right',
  showClose: true,
  onClick: () => handleReminderClick(reminder)
})
```

#### **开发测试支持**
```typescript
// 模拟提醒数据（开发环境）
const mockReminders = [
  {
    title: "喝水提醒",
    description: "记得多喝水，保持身体健康",
    minutesFromNow: 5,
    priority: "medium"
  },
  // ... 更多测试数据
]
```

### 环境配置

前端通过环境变量配置API地址：

```bash
# .env
VITE_API_BASE_URL=http://localhost:8000
```

### 错误处理

前端具备完善的错误处理机制：

1. **网络错误**: 自动重试机制
2. **服务器错误**: 显示友好错误信息
3. **超时处理**: 设置合理的请求超时时间
4. **降级处理**: 开发环境提供模拟响应

### 模拟模式

开发环境下，如果后端服务不可用，前端会使用内置的模拟响应：

- **天气查询**: 返回模拟天气信息
- **数学计算**: 执行简单的数学运算
- **默认回复**: 通用的助理回复

---

## 🚀 后端实现指南

### 技术栈

- **框架**: FastAPI
- **AI框架**: LangChain
- **工具**: 自定义Tool实现
- **部署**: Uvicorn

### 最小实现

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Personal Lifestyle Assistant")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message: str
    timestamp: str = None

class MessageResponse(BaseModel):
    message: str
    success: bool = True
    tool_used: str = None

@app.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    # TODO: 集成LangChain Agent
    return MessageResponse(
        message="这是来自后端的回复",
        success=True
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

---

## 📊 性能指标

### 期望性能

- **响应时间**: < 2秒 (95%的请求)
- **吞吐量**: > 100 请求/分钟
- **可用性**: > 99.9%
- **并发支持**: 50+ 并发用户

### 监控指标

- API响应时间
- 错误率
- 工具调用成功率
- 内存和CPU使用率

---

## 🔒 安全考虑

### 当前实现

- CORS配置限制前端访问
- 输入验证和清理
- 错误信息不暴露敏感信息

### 未来增强

- API密钥认证
- 请求频率限制
- 输入内容过滤
- 审计日志记录

---

## 📝 更新日志

### v1.2.0 (2025-08-15) ⭐ 当前版本
- ✅ **提醒功能完整实现**
  - 新增获取即将到期提醒接口 `GET /reminders/upcoming`
  - 新增完成提醒接口 `POST /reminders/{id}/complete`
  - 新增延迟提醒接口 `POST /reminders/{id}/snooze`
- ✅ **前端提醒系统集成**
  - 自动监控和智能通知系统
  - ElementPlus UI组件集成
  - 声音提醒和用户交互功能
  - 开发环境模拟数据支持
- ✅ **API文档完善**
  - 详细的提醒接口说明
  - 前端集成指南
  - 完整的示例代码

### v1.1.0 (2025-08-14)
- ✅ 添加会话管理功能
- ✅ 前端支持会话ID自动生成和管理
- ✅ 支持新建会话功能
- ✅ 优化对话上下文保持
- 🔧 修复会话断续问题

### v1.0.0 (2025-08-13)
- ✅ 定义基础API接口规范
- ✅ 实现前端模拟响应机制
- ✅ 设计工具系统架构

### 未来版本计划
- v1.3.0: 提醒管理页面（创建、编辑、删除）
- v1.4.0: 重复提醒和提醒分类
- v1.5.0: 用户认证系统
- v2.0.0: 多用户支持和数据同步

---

## 🤝 联系方式

如有API相关问题，请通过以下方式联系：
- 提交 GitHub Issue
- 查看项目文档
- 参与项目讨论

---

*本文档随项目开发进度持续更新*
