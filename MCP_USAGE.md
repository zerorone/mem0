# Mem0-GLM MCP 集成指南

> 📅 **更新时间**: 2025-09-02  
> 🎯 **版本**: Mem0 + GLM v1.0  
> 📖 **目标**: 详细介绍如何配置和使用 Mem0-GLM MCP 服务器

## 📋 目录

- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [工具清单](#工具清单)
- [Docker 数据库](#docker-数据库)
- [MCP 客户端配置](#mcp-客户端配置)
- [故障排除](#故障排除)

## 🚀 快速开始

### 1. 一键设置

```bash
# 运行快速设置脚本
chmod +x scripts/setup_mcp.sh
./scripts/setup_mcp.sh
```

### 2. 启动数据库服务

```bash
# 启动所有数据库服务
docker-compose up -d

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 下载嵌入模型

```bash
# 下载 Ollama 嵌入模型
docker-compose exec ollama ollama pull bge-m3

# 或者本地安装 Ollama
ollama pull bge-m3
```

### 4. 启动 MCP 服务器

```bash
# 启动服务器
./scripts/start_mcp_server.sh

# 或直接运行
/opt/miniconda3/envs/memos_py311/bin/python mcp_server/server.py
```

## ⚙️ 配置说明

### 📁 配置文件优先级

1. `~/.claude/mem0-glm-config.json` (Claude 专用)
2. `config/development.json` (开发配置)
3. `config/.env.json` (环境配置)
4. 环境变量

### 🔧 配置文件示例

#### `config/development.json`
```json
{
  "glm_api_key": "your_glm_api_key_here",
  "glm_base_url": "https://open.bigmodel.cn/api/paas/v4",
  "glm_model": "glm-4.5",
  "enable_thinking": true,
  
  "vector_store_provider": "chroma",
  "vector_store_config": {
    "collection_name": "mem0_memories",
    "path": "./chroma_db"
  },
  
  "embedding_provider": "ollama",
  "embedding_config": {
    "model": "bge-m3",
    "base_url": "http://localhost:11434"
  },
  
  "log_level": "INFO"
}
```

#### Claude Desktop 配置 `~/.claude/mcp_settings.json`
```json
{
  "mcpServers": {
    "mem0-glm": {
      "command": "/opt/miniconda3/envs/memos_py311/bin/python",
      "args": [
        "/Users/xiao/Documents/BaiduNetSyncDownload/ToolCode/mem0/mcp_server/server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/xiao/Documents/BaiduNetSyncDownload/ToolCode/mem0"
      }
    }
  }
}
```

## 🛠️ MCP 工具清单

### ✅ 可用工具 (8个)

| 工具名称 | 功能描述 | 参数说明 | 使用场景 |
|---------|----------|----------|----------|
| `add_memory` | 添加新记忆 | `content`, `user_id`, `metadata` | 保存重要信息 |
| `search_memories` | 搜索记忆 | `query`, `user_id`, `limit` | 查找相关信息 |
| `get_all_memories` | 获取所有记忆 | `user_id` | 查看用户记忆 |
| `update_memory` | 更新记忆 | `memory_id`, `content`, `user_id` | 修改记忆内容 |
| `delete_memory` | 删除记忆 | `memory_id`, `user_id` | 移除记忆 |
| `chat_with_memory` | 基于记忆对话 | `message`, `user_id`, `include_memories` | 智能对话 |
| `memory_stats` | 获取统计信息 | `user_id` | 查看使用情况 |
| `health_check` | 健康检查 | 无参数 | 服务状态检查 |

### 🎯 工具使用示例

#### 1. 添加记忆
```python
# 添加简单记忆
add_memory(
    content="用户喜欢使用 Python 进行数据分析",
    user_id="john_doe"
)

# 添加带元数据的记忆
add_memory(
    content="项目使用 React + TypeScript 技术栈",
    user_id="developer_team",
    metadata={"category": "tech_stack", "importance": "high"}
)
```

#### 2. 搜索记忆
```python
# 搜索编程相关记忆
search_memories(
    query="编程语言偏好",
    user_id="john_doe",
    limit=5
)
```

#### 3. 智能对话
```python
# 基于记忆的对话
chat_with_memory(
    message="我应该用什么技术栈开发新项目？",
    user_id="developer_team",
    include_memories=True
)
```

## 🐳 Docker 数据库配置

### 📊 支持的数据库

| 服务 | 端口 | 用途 | 默认凭据 |
|------|------|------|----------|
| ChromaDB | 8000 | 向量数据库 | 无 |
| Qdrant | 6333 | 向量数据库（备选） | 无 |
| Neo4j | 7474/7687 | 图数据库 | neo4j/mem0password |
| Ollama | 11434 | 本地 LLM/嵌入 | 无 |
| Redis | 6379 | 缓存 | 无 |

### 🧠 BGE-M3 嵌入模型优势

BGE-M3（BAAI General Embedding Multilingual-M3）是专为中文优化的高性能嵌入模型：

**核心优势:**
- **中文友好**: 专门为中文文本优化，语义理解更准确
- **高精度**: 在中文语义搜索任务中表现优异
- **1024维度**: 提供丰富的语义表示能力
- **多语言支持**: 支持100+种语言，中英文效果最佳
- **检索优化**: 专门针对检索任务训练，适合记忆搜索

**性能对比:**
| 模型 | 中文精度 | 维度 | 大小 | 适用场景 |
|------|----------|------|------|----------|
| BGE-M3 | ★★★★★ | 1024 | ~2.3GB | 生产环境，中文为主 |
| nomic-embed-text | ★★★☆☆ | 768 | ~550MB | 英文为主，轻量化 |

**特别适用于:**
- 中文技术文档记忆管理
- 中英文混合内容搜索
- 需要高精度语义匹配的场景

### 🔧 数据库管理命令

```bash
# 启动所有服务
docker-compose up -d

# 启动特定服务
docker-compose up -d chromadb ollama

# 停止服务
docker-compose down

# 清理数据
docker-compose down -v
rm -rf chroma_data qdrant_data neo4j_data ollama_data

# 查看日志
docker-compose logs -f chromadb
```

### 🔍 服务健康检查

```bash
# Chroma 健康检查
curl http://localhost:8000/api/v1/heartbeat

# Qdrant 健康检查
curl http://localhost:6333/health

# Neo4j Web 界面
open http://localhost:7474

# Ollama 版本检查
curl http://localhost:11434/api/version

# Redis 连接检查
redis-cli ping
```

## 🎛️ 高级配置

### 🚀 性能优化

#### 1. 向量存储选择
```json
{
  "vector_store_provider": "qdrant",  // 高性能
  "vector_store_config": {
    "host": "localhost",
    "port": 6333,
    "collection_name": "mem0_memories"
  }
}
```

#### 2. 嵌入模型配置
```json
{
  "embedding_provider": "openai",  // 高质量
  "embedding_config": {
    "model": "text-embedding-3-small",
    "api_key": "your_openai_key"
  }
}
```

#### 3. GLM 模型选择
```json
{
  "glm_model": "glm-4.5-pro",  // 支持深度思考
  "enable_thinking": true
}
```

### 🔐 安全配置

#### 1. API 密钥管理
```bash
# 使用环境变量
export GLM_API_KEY="secure_api_key"
export OPENAI_API_KEY="openai_key"

# 或使用 .env 文件
echo "GLM_API_KEY=secure_key" > config/.env
```

#### 2. 网络安全
```yaml
# docker-compose.yml 网络配置
networks:
  mem0-network:
    driver: bridge

services:
  chromadb:
    networks:
      - mem0-network
    # 限制外部访问
    ports:
      - "127.0.0.1:8000:8000"
```

## 🎯 MCP 客户端使用

### 📱 Claude Desktop

1. 复制配置到 Claude Desktop 配置目录
2. 重启 Claude Desktop
3. 验证工具可用性

### 🔧 自定义客户端

```python
from mcp import Client

# 连接到 MCP 服务器
client = Client("stdio", command=[
    "/opt/miniconda3/envs/memos_py311/bin/python",
    "mcp_server/server.py"
])

# 使用工具
result = await client.call_tool("add_memory", {
    "content": "重要信息",
    "user_id": "test_user"
})
```

## 🐛 故障排除

### ❌ 常见错误

#### 1. Python 环境问题
```
❌ Python 环境不存在: /opt/miniconda3/envs/memos_py311/bin/python
```
**解决方案**：
```bash
# 创建 conda 环境
conda create -n memos_py311 python=3.11 -y
conda activate memos_py311
pip install fastmcp mem0ai
```

#### 2. 依赖缺失
```
❌ FastMCP 未安装
```
**解决方案**：
```bash
pip install fastmcp httpx
```

#### 3. 数据库连接失败
```
❌ Mem0 实例初始化失败: Connection refused
```
**解决方案**：
```bash
# 启动数据库服务
docker-compose up -d chromadb
# 等待服务启动
sleep 10
```

#### 4. GLM API 错误
```
❌ GLM API 错误 401: Unauthorized
```
**解决方案**：
```bash
# 检查 API 密钥
export GLM_API_KEY="correct_api_key"
# 或更新配置文件
```

### 🔍 调试技巧

#### 1. 启用详细日志
```json
{
  "log_level": "DEBUG",
  "enhanced_logging": true
}
```

#### 2. 测试连接
```bash
# 测试 GLM API
curl -H "Authorization: Bearer your_api_key" \
     https://open.bigmodel.cn/api/paas/v4/chat/completions

# 测试向量数据库
curl http://localhost:8000/api/v1/heartbeat
```

#### 3. 健康检查脚本
```python
import asyncio
import json

async def test_health():
    # 这里应该调用 health_check 工具
    print("运行健康检查...")
    # 实际实现需要调用 MCP 工具

asyncio.run(test_health())
```

### 📊 监控和维护

#### 1. 日志监控
```bash
# 查看服务器日志
tail -f mem0_mcp_server.log

# 查看 Docker 日志
docker-compose logs -f
```

#### 2. 性能监控
```python
# 获取内存使用统计
memory_stats(user_id="system")

# 检查数据库大小
du -sh chroma_data/
```

#### 3. 备份和恢复
```bash
# 备份数据
tar -czf mem0_backup_$(date +%Y%m%d).tar.gz \
    chroma_data/ qdrant_data/ neo4j_data/

# 恢复数据
tar -xzf mem0_backup_20250902.tar.gz
```

## 📚 使用示例

### 🎯 完整工作流程

```python
# 1. 添加记忆
add_memory(
    content="客户 John 喜欢简洁的用户界面设计",
    user_id="project_alpha"
)

# 2. 搜索相关记忆
search_memories(
    query="用户界面设计偏好",
    user_id="project_alpha"
)

# 3. 基于记忆的智能对话
chat_with_memory(
    message="我们应该如何设计新的登录页面？",
    user_id="project_alpha"
)

# 4. 更新记忆
update_memory(
    memory_id="mem_123",
    content="客户 John 特别喜欢深色主题的简洁界面",
    user_id="project_alpha"
)

# 5. 获取统计信息
memory_stats(user_id="project_alpha")
```

---

## 🎉 总结

Mem0-GLM MCP 集成提供了强大的智能记忆管理能力：

- ✅ **完整的记忆生命周期管理**
- ✅ **基于 GLM 的中文优化 AI 对话**
- ✅ **Docker 化的数据库服务**
- ✅ **灵活的配置和部署选项**
- ✅ **丰富的 MCP 工具集**

现在您可以在 Claude Desktop 或其他 MCP 客户端中享受智能记忆管理的强大功能！