# 个人生活助理 Agent

一个智能的个人生活助理Agent，帮助用户处理日常生活事务，如天气查询、计算、提醒等。项目采用现代化的技术栈，提供友好的网页界面进行自然语言交互。

## 项目概述

### 🎯 目标
打造一个智能助手工具，通过自然语言交互帮助用户处理各种日常生活事务，提升生活效率和便利性。

### ✨ 核心功能
- **🌤️ 天气查询**: 获取实时天气信息和预报
- **🔢 数学计算**: 进行各种数学运算和计算
- **⏰ 提醒设置**: 设置和管理个人提醒事项
- **💬 对话历史**: 自动保存对话记录，支持会话切换和搜索
- **🧠 记忆功能**: 记录对话上下文，支持多轮交互
- **🔍 网络搜索**: 搜索最新信息和资料

### 🏗️ 系统架构

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐    LangChain    ┌─────────────────┐
│   Vue 3 前端    │ ◄─────────────────► │  FastAPI 后端   │ ◄─────────────► │  Agent + Tools  │
│   (聊天界面)    │                     │   (API服务)     │                 │  (智能工具链)   │
└─────────────────┘                     └─────────────────┘                 └─────────────────┘
```

## 技术栈

### 前端 (Vue 3)
- **Vue 3**: 现代化前端框架，采用Composition API
- **TypeScript**: 类型安全的JavaScript超集
- **Vite**: 快速的构建工具和开发服务器
- **CSS3**: 现代CSS特性，响应式设计

### 后端 (FastAPI + LangChain)
- **Python**: 主要编程语言
- **FastAPI**: 高性能异步Web框架
- **LangChain**: AI应用开发框架
- **Agent + Tools**: 智能工具链架构

## 项目结构

```
PersonalLifestyleAssistantAgent/
├── 设计文档.md                    # 项目设计文档
├── frontend/                     # Vue3前端应用
│   ├── src/
│   │   ├── components/          # Vue组件
│   │   │   ├── ChatInterface.vue      # 主聊天界面
│   │   │   ├── MessageBubble.vue      # 消息气泡组件
│   │   │   └── ToolIndicator.vue      # 工具指示器
│   │   ├── services/            # 服务层
│   │   │   └── chatService.ts         # API通信服务
│   │   ├── App.vue             # 应用根组件
│   │   └── main.ts             # 应用入口
│   ├── .env                    # 环境变量配置
│   ├── package.json           # 依赖配置
│   └── README.md              # 前端文档
├── backend/                   # FastAPI后端应用 (待开发)
│   ├── main.py               # FastAPI应用入口
│   ├── agents/               # LangChain Agent配置
│   ├── tools/                # 自定义工具实现
│   └── requirements.txt      # Python依赖
└── README.md                 # 项目主文档
```

## 快速开始

### 环境要求
- **Node.js** >= 16.0.0 (前端)
- **Python** >= 3.8 (后端)
- **npm** >= 7.0.0

### 1. 克隆项目
```bash
git clone <repository-url>
cd PersonalLifestyleAssistantAgent
```

### 2. 启动前端应用
```bash
cd frontend
npm install
npm run dev
```
前端将在 `http://localhost:5173` 启动

### 3. 启动后端服务 (开发中)
```bash
cd backend
pip install -r requirements.txt
python main.py
```
后端将在 `http://localhost:8000` 启动

### 4. 开始使用
访问前端地址，开始与AI助理聊天！

## 功能演示

### 🌤️ 天气查询
```
用户: 今天的天气怎么样？
助理: 今天北京天气晴朗，气温23°C，适合外出活动。建议您穿着舒适的春秋装。
```

### 🔢 数学计算
```
用户: 帮我计算 15 * 23 + 47
助理: 计算结果：392
```

### 💬 对话历史
```
系统功能：
- 自动保存每次对话到数据库
- 左侧边栏显示历史对话列表
- 点击任意历史对话快速切换
- 支持对话内容搜索
- 一键创建新对话会话
```

## 开发特性

### 🔄 热重载
开发环境支持实时热重载，修改代码即时生效

### 🎭 模拟模式
前端内置模拟响应，无需后端即可测试界面功能

### 🔍 类型安全
全面使用TypeScript，提供完整的类型检查

### 📱 响应式设计
完美适配桌面和移动设备

## 部署指南

### 前端部署
```bash
cd frontend
npm run build
# 将 dist/ 目录部署到静态服务器
```

### 后端部署
```bash
cd backend
# 使用 Docker 或直接部署到服务器
```

## 开发路线图

- [x] ✅ Vue3前端界面开发
- [x] ✅ 聊天界面和用户体验
- [x] ✅ 响应式设计和动画效果
- [ ] 🚧 FastAPI后端开发
- [ ] 🚧 LangChain Agent集成
- [ ] 🚧 工具链实现 (搜索、计算器等)
- [ ] 🚧 数据持久化
- [ ] 🚧 用户认证系统
- [ ] 🚧 部署和CI/CD

## 贡献指南

1. **Fork** 项目
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 **Pull Request**

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 📧 提交 Issue
- 💬 创建 Discussion
- 🔧 发送 Pull Request

---

<div align="center">

**🎉 感谢使用个人生活助理Agent！**

*让AI助手让您的生活更加便利和高效* ✨

</div>
