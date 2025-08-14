# Personal Lifestyle Assistant Agent - API 接口文档

## 📋 接口概览

本文档描述了个人生活助理Agent的前后端API接口规范。前端Vue3应用通过这些接口与FastAPI后端进行通信。

### 🏗️ 系统架构

```
Vue 3 前端 (http://localhost:5173)
    ↕ HTTP/JSON
FastAPI 后端 (http://localhost### 🔧 前端集成说明

### 会话管理

前端现在支持会话管理功能：

#### **会话ID生成规则**
```typescript
// 基于日期和时间戳的会话ID格式
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

### 2. 健康检查接口

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

### 3. 获取对话历史接口 (规划中)

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

### 4. 重置对话接口 (规划中)

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

| 工具ID | 工具名称 | 功能描述 | 触发关键词 |
|--------|----------|----------|------------|
| `search` | 网络搜索 | 搜索实时信息、天气查询 | 天气、搜索、查询 |
| `calculator` | 计算器 | 数学计算和表达式求值 | 计算、数字、运算符 |
| `memory` | 记忆系统 | 记录和回忆对话上下文 | 记住、之前、回忆 |
| `reminder` | 提醒工具 | 设置时间提醒和任务 | 提醒、闹钟、定时 |

### 工具使用流程

1. 用户发送消息
2. Agent分析消息内容
3. 选择合适的工具
4. 执行工具功能
5. 基于工具结果生成回复

---

## 🔧 前端集成说明

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
- **记账建议**: 提供预设的理财建议
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

### v1.0.0 (2025-08-13)
- 定义基础API接口规范
- 实现前端模拟响应机制
- 设计工具系统架构

### 未来版本计划
- v1.1.0: 用户认证系统
- v1.2.0: 对话历史管理
- v1.3.0: 高级工具集成
- v2.0.0: 多用户支持

---

## 🤝 联系方式

如有API相关问题，请通过以下方式联系：
- 提交 GitHub Issue
- 查看项目文档
- 参与项目讨论

---

*本文档随项目开发进度持续更新*
