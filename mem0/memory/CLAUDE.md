[根目录](../../CLAUDE.md) > [mem0](../) > **memory**

# Memory 模块 - 核心记忆管理

> Mem0 框架的核心模块，提供同步和异步的记忆管理功能

## 变更记录 (Changelog)

### 2025-09-02 12:23:11 - 模块初始化
- 分析核心记忆管理逻辑
- 识别同步/异步双接口设计
- 发现多层级记忆管理能力

---

## 模块职责

Memory 模块是 Mem0 框架的核心，负责：
- 智能记忆的存储、检索、更新和删除
- 多层级记忆管理（用户、代理、运行会话）
- 向量化检索和语义搜索
- 记忆生命周期管理和历史追踪
- 程序化记忆创建

## 入口与启动

### 主要类
- **Memory**: 同步记忆管理类
- **AsyncMemory**: 异步记忆管理类
- **MemoryBase**: 基础抽象类

### 关键文件
- `main.py`: 核心实现 (1,868 行代码)
- `base.py`: 基础抽象类定义
- `setup.py`: 初始化配置
- `storage.py`: SQLite 存储管理
- `utils.py`: 工具函数
- `telemetry.py`: 遥测数据收集

## 对外接口

### 核心 API
```python
# 记忆操作
memory.add(messages, user_id="user_1")           # 添加记忆
memory.search(query, user_id="user_1")           # 搜索记忆  
memory.get(memory_id)                            # 获取指定记忆
memory.get_all(user_id="user_1")                 # 获取所有记忆
memory.update(memory_id, data)                   # 更新记忆
memory.delete(memory_id)                         # 删除记忆
memory.delete_all(user_id="user_1")              # 删除用户所有记忆
memory.history(memory_id)                        # 获取记忆历史
memory.reset()                                   # 重置所有记忆
```

### 会话作用域
支持三种会话标识符：
- `user_id`: 用户级记忆
- `agent_id`: 代理级记忆  
- `run_id`: 运行级记忆

### API 版本
- **v1.0**: 传统格式（将弃用）
- **v1.1**: 新格式，返回 `{"results": [...]}` 结构

## 关键依赖与配置

### 依赖组件
- **EmbedderFactory**: 嵌入模型工厂
- **VectorStoreFactory**: 向量存储工厂
- **LlmFactory**: LLM 工厂
- **GraphStoreFactory**: 图存储工厂（可选）

### 配置管理
```python
from mem0.configs.base import MemoryConfig

config = MemoryConfig(
    vector_store=VectorStoreConfig(...),
    llm=LlmConfig(...),
    embedder=EmbedderConfig(...),
    graph_store=GraphStoreConfig(...)  # 可选
)
```

## 数据模型

### MemoryItem 结构
```python
class MemoryItem(BaseModel):
    id: str                          # 唯一标识符
    memory: str                      # 记忆内容
    hash: Optional[str]              # 内容哈希
    metadata: Optional[Dict]         # 额外元数据
    score: Optional[float]           # 相关性评分
    created_at: Optional[str]        # 创建时间
    updated_at: Optional[str]        # 更新时间
```

### 会话过滤器
```python
def _build_filters_and_metadata(
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None, 
    run_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    input_metadata: Optional[Dict] = None,
    input_filters: Optional[Dict] = None
) -> Tuple[Dict, Dict]:
```

## 测试与质量

### 测试覆盖
- `test_main.py`: 主要功能测试
- `test_kuzu.py`: Kuzu 图数据库测试
- `test_neo4j_cypher_syntax.py`: Neo4j 语法测试
- `test_neptune_memory.py`: Neptune 图数据库测试

### 记忆类型支持
- **事实记忆**: 基于对话内容提取的事实
- **程序化记忆**: 基于对话流程创建的操作记忆
- **多模态记忆**: 支持图像等多媒体内容

## 常见问题 (FAQ)

### Q: 同步和异步版本的区别？
A: AsyncMemory 使用 `asyncio.to_thread` 包装同步操作，适合异步应用场景。API 接口完全一致。

### Q: 如何启用图数据库功能？
A: 在配置中添加 `graph_store` 配置即可启用，支持 Neo4j、Neptune 等。

### Q: 记忆如何进行向量化检索？
A: 使用配置的嵌入模型将查询和记忆内容转换为向量，通过余弦相似度进行检索。

### Q: 支持哪些记忆推理功能？
A: 支持 ADD（添加）、UPDATE（更新）、DELETE（删除）、NONE（无操作）四种智能推理操作。

## 相关文件清单

### 核心实现
- `main.py`: 主要实现逻辑
- `base.py`: 抽象基类
- `storage.py`: SQLite 存储层
- `utils.py`: 工具函数集合

### 支持文件
- `setup.py`: 环境初始化
- `telemetry.py`: 使用情况统计

---

*模块复杂度: 高 | 测试覆盖: 中 | 文档完整度: 高*