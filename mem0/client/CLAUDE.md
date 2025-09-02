[根目录](../../CLAUDE.md) > [mem0](../) > **client**

# Client 模块 - API 客户端接口

> 提供与 Mem0 平台服务交互的客户端接口，支持项目管理和远程记忆服务

## 变更记录 (Changelog)

### 2025-09-02 12:23:11 - 模块初始化
- 分析客户端架构设计
- 识别同步/异步客户端接口
- 发现项目管理和工具函数

---

## 模块职责

Client 模块提供与 Mem0 平台服务的接口：
- 远程记忆服务的客户端封装
- 项目和组织管理功能
- 同步和异步 API 调用支持
- 认证和会话管理
- 工具函数和辅助功能

## 入口与启动

### 主要类
- **MemoryClient**: 同步记忆客户端
- **AsyncMemoryClient**: 异步记忆客户端
- **ProjectManager**: 项目管理类

### 关键文件
- `main.py`: 主要客户端实现
- `project.py`: 项目管理功能
- `utils.py`: 工具函数和辅助功能

## 对外接口

### 客户端初始化
```python
from mem0 import MemoryClient, AsyncMemoryClient

# 同步客户端
client = MemoryClient(api_key="your-api-key")

# 异步客户端  
async_client = AsyncMemoryClient(api_key="your-api-key")
```

### 核心功能
```python
# 记忆管理（与本地 Memory 类似的接口）
client.add(messages, user_id="user_1")
client.search(query="咖啡偏好", user_id="user_1")
client.get_all(user_id="user_1")
client.delete(memory_id)

# 项目管理
project_manager = ProjectManager()
projects = project_manager.list_projects()
project = project_manager.get_project(project_id)
```

## 关键依赖与配置

### 认证配置
- API 密钥认证
- 项目 ID 和组织管理
- 环境变量支持

### 网络配置
- HTTP/HTTPS 请求处理
- 异步请求支持
- 错误处理和重试机制

## 数据模型

### 客户端响应格式
与本地 Memory 类保持一致的 API 响应格式：
```python
{
    "results": [
        {
            "id": "memory_id",
            "memory": "记忆内容", 
            "score": 0.95,
            "created_at": "2025-09-02T12:23:11Z"
        }
    ]
}
```

### 项目管理模型
- Project: 项目信息
- Organization: 组织信息  
- Member: 成员管理

## 测试与质量

### 测试策略
- 模拟 API 响应测试
- 认证流程测试
- 异步操作测试
- 项目管理功能测试

### 错误处理
- 网络连接错误
- 认证失败处理
- API 限流和重试

## 常见问题 (FAQ)

### Q: 客户端和本地 Memory 的区别？
A: 客户端连接到 Mem0 云平台服务，本地 Memory 在本地运行。API 接口基本一致。

### Q: 如何配置 API 端点？
A: 通过环境变量或初始化参数指定 API 端点和认证信息。

### Q: 支持批量操作吗？
A: 支持，客户端提供了批量添加、删除等操作接口。

### Q: 异步客户端的性能优势？
A: 异步客户端可以并行处理多个 API 请求，适合高并发场景。

## 相关文件清单

### 核心实现
- `main.py`: 主要客户端实现
- `project.py`: 项目管理功能
- `utils.py`: 工具函数

### 配置支持
- 环境变量配置
- API 密钥管理
- 端点配置

---

*模块复杂度: 中 | 测试覆盖: 中 | 文档完整度: 中*