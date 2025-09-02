[根目录](../../CLAUDE.md) > [mem0](../) > **configs**

# Configs 模块 - 配置管理系统

> 基于 Pydantic 的类型安全配置管理，支持所有组件的灵活配置

## 变更记录 (Changelog)

### 2025-09-02 12:23:11 - 模块初始化
- 分析配置系统架构
- 识别多层级配置结构
- 发现枚举和提示管理机制

---

## 模块职责

Configs 模块负责整个 Mem0 框架的配置管理：
- 核心配置模型定义（MemoryConfig、MemoryItem）
- LLM 提供商配置（OpenAI、Anthropic、Google 等）
- 嵌入模型配置（OpenAI、HuggingFace 等）
- 向量数据库配置（Qdrant、Chroma、Pinecone 等）
- 系统级配置和环境管理
- 提示模板管理

## 入口与启动

### 主要配置类
- **MemoryConfig**: 核心记忆系统配置
- **MemoryItem**: 记忆数据项模型
- **AzureConfig**: Azure 服务配置

### 关键文件
- `base.py`: 基础配置类和数据模型
- `enums.py`: 枚举定义
- `prompts.py`: 提示模板管理

## 对外接口

### 核心配置
```python
from mem0.configs.base import MemoryConfig, MemoryItem

# 基础配置
config = MemoryConfig(
    vector_store=VectorStoreConfig(),
    llm=LlmConfig(),
    embedder=EmbedderConfig(),
    history_db_path="~/.mem0/history.db",
    version="v1.1"
)

# 自定义提示
config = MemoryConfig(
    custom_fact_extraction_prompt="自定义事实提取提示",
    custom_update_memory_prompt="自定义记忆更新提示"
)
```

### 配置结构
```python
class MemoryConfig(BaseModel):
    vector_store: VectorStoreConfig     # 向量存储配置
    llm: LlmConfig                     # LLM 配置  
    embedder: EmbedderConfig           # 嵌入模型配置
    history_db_path: str               # 历史数据库路径
    graph_store: GraphStoreConfig      # 图存储配置
    version: str = "v1.1"              # API 版本
    custom_fact_extraction_prompt: Optional[str]
    custom_update_memory_prompt: Optional[str]
```

## 关键依赖与配置

### 子模块配置
- `llms/`: LLM 提供商配置
  - `openai.py`, `anthropic.py`, `azure.py`
  - `ollama.py`, `deepseek.py`, `lmstudio.py`
  - `vllm.py` 等
- `embeddings/`: 嵌入模型配置
  - `base.py`: 基础嵌入配置
- `vector_stores/`: 向量数据库配置
  - `chroma.py`, `qdrant.py`, `pinecone.py`
  - `elasticsearch.py`, `weaviate.py`
  - `azure_ai_search.py`, `pgvector.py` 等

### 环境变量支持
- `MEM0_DIR`: Mem0 数据目录（默认 `~/.mem0`）
- 各提供商 API 密钥环境变量

## 数据模型

### MemoryItem 模型
```python
class MemoryItem(BaseModel):
    id: str = Field(..., description="唯一标识符")
    memory: str = Field(..., description="从文本数据推断的记忆") 
    hash: Optional[str] = Field(None, description="记忆的哈希值")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")
    score: Optional[float] = Field(None, description="相关性评分")
    created_at: Optional[str] = Field(None, description="创建时间戳")
    updated_at: Optional[str] = Field(None, description="更新时间戳")
```

### Azure 配置
```python  
class AzureConfig(BaseModel):
    api_key: str = Field(description="Azure API 密钥")
    azure_deployment: str = Field(description="Azure 部署名称") 
    azure_endpoint: str = Field(description="Azure 服务端点")
    api_version: str = Field(description="Azure API 版本")
    default_headers: Optional[Dict[str, str]] = Field(description="默认请求头")
```

## 测试与质量

### 配置验证
- 使用 Pydantic 进行类型验证和数据校验
- 支持配置字典到模型的自动转换
- 提供详细的验证错误信息

### 测试覆盖
- `test_prompts.py`: 提示模板测试

## 常见问题 (FAQ)

### Q: 如何自定义配置？
A: 通过创建相应的配置对象并传递给 Memory 类：
```python
config = MemoryConfig(
    llm=LlmConfig(provider="openai", config={"model": "gpt-4"}),
    vector_store=VectorStoreConfig(provider="qdrant")
)
memory = Memory(config=config)
```

### Q: 支持哪些环境变量？
A: 主要包括 `MEM0_DIR` 和各提供商的 API 密钥变量，具体参见各提供商配置文件。

### Q: 如何添加新的 LLM 提供商？
A: 在 `llms/` 目录添加新的配置文件，并在工厂类中注册。

## 相关文件清单

### 核心配置
- `base.py`: 基础配置类 (86 行)
- `enums.py`: 枚举定义
- `prompts.py`: 提示模板

### LLM 配置
- `llms/base.py`: LLM 基础配置
- `llms/openai.py`: OpenAI 配置
- `llms/anthropic.py`: Anthropic 配置
- `llms/azure.py`: Azure OpenAI 配置
- 其他 10+ 个 LLM 提供商配置

### 其他配置
- `embeddings/base.py`: 嵌入配置基类
- `vector_stores/`: 20+ 个向量数据库配置

---

*模块复杂度: 中 | 测试覆盖: 低 | 文档完整度: 高*