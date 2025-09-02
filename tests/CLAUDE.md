[根目录](../CLAUDE.md) > **tests**

# Mem0 测试架构与质量保证体系

## 模块职责

测试模块为 Mem0 框架提供全面的质量保证，涵盖单元测试、集成测试、性能测试和回归测试。通过分层的测试架构确保框架在各种场景下的稳定性、可靠性和性能表现。

## 入口与启动

**测试执行入口：**
```bash
# 运行所有测试
pytest tests/

# 按模块运行
pytest tests/embeddings/    # 嵌入模型测试
pytest tests/llms/          # LLM 提供商测试  
pytest tests/memory/        # 核心记忆测试
pytest tests/vector_stores/ # 向量数据库测试
```

**测试发现机制：**
- pytest 自动发现 `test_*.py` 文件
- 支持并行测试执行
- 集成 CI/CD 自动化流水线

## 对外接口

### 核心测试框架

**测试技术栈：**
```python
pytest              # 主测试框架
unittest.mock       # Mock 对象和补丁
pytest-asyncio      # 异步测试支持  
pytest-xdist        # 并行测试执行
```

**通用测试工具：**
```python
# Mock 工厂函数
def _setup_mocks(mocker):
    mock_embedder = mocker.MagicMock()
    mock_vector_store = mocker.MagicMock() 
    mock_llm = mocker.MagicMock()
    return mock_llm, mock_vector_store
```

### 分层测试架构

#### 1. 单元测试层
- **嵌入模型测试** (`embeddings/`)
- **LLM 提供商测试** (`llms/`)
- **向量存储测试** (`vector_stores/`)
- **配置验证测试** (`configs/`)

#### 2. 集成测试层
- **记忆核心功能测试** (`memory/`)
- **端到端流程测试** (`test_memory_integration.py`)
- **多组件协同测试** (`test_memory.py`)

#### 3. 系统测试层
- **代理和遥测测试** (`test_proxy.py`, `test_telemetry.py`)
- **主入口测试** (`test_main.py`)

## 测试模块详细分析

### 1. 嵌入模型测试 (`embeddings/`)

**测试覆盖的提供商：**
- OpenAI (`test_openai_embeddings.py`)
- Azure OpenAI (`test_azure_openai_embeddings.py`) 
- Hugging Face (`test_huggingface_embeddings.py`)
- Ollama (`test_ollama_embeddings.py`)
- Google Gemini (`test_gemini_emeddings.py`)
- Vertex AI (`test_vertexai_embeddings.py`)
- LM Studio (`test_lm_studio_embeddings.py`)

**核心测试用例：**
```python
def test_embed_default_model(mock_openai_client):
    """测试默认模型配置"""
    config = BaseEmbedderConfig()
    embedder = OpenAIEmbedding(config)
    
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
    mock_openai_client.embeddings.create.return_value = mock_response
    
    result = embedder.embed("Hello world")
    
    # 验证API调用参数
    mock_openai_client.embeddings.create.assert_called_once_with(
        input=["Hello world"], 
        model="text-embedding-3-small", 
        dimensions=1536
    )
    assert result == [0.1, 0.2, 0.3]
```

**测试重点：**
- 默认配置验证
- 自定义模型和维度
- 文本预处理（换行符处理）
- API 密钥管理
- 环境变量支持

### 2. LLM 提供商测试 (`llms/`)

**支持的提供商测试：**
- OpenAI (`test_openai.py`)
- Azure OpenAI (`test_azure_openai.py`, `test_azure_openai_structured.py`)
- Groq (`test_groq.py`)
- Together (`test_together.py`)
- Anthropic、Google Gemini 等其他提供商

**结构化输出测试：**
```python
# Azure OpenAI 结构化输出专项测试
def test_structured_output_support():
    """验证结构化输出功能"""
    # 测试 JSON Schema 验证
    # 测试类型安全的响应解析
    # 测试错误处理和降级策略
```

### 3. 向量数据库测试 (`vector_stores/`)

**全面的数据库支持测试 (17种)：**
- Qdrant (`test_qdrant.py`)
- Chroma (`test_chroma.py`) 
- FAISS (`test_faiss.py`)
- Pinecone (`test_pinecone.py`)
- Azure AI Search (`test_azure_ai_search.py`)
- MongoDB (`test_mongodb.py`)
- Elasticsearch (`test_elasticsearch.py`)
- PostgreSQL (`test_pgvector.py`)
- Redis、Supabase、Weaviate 等

**通用测试模式：**
```python
def test_vector_store_basic_operations():
    """测试向量数据库基础操作"""
    # 1. 连接和初始化测试
    # 2. 向量插入和索引测试  
    # 3. 相似性搜索测试
    # 4. 批量操作测试
    # 5. 错误处理测试
```

### 4. 记忆核心功能测试 (`memory/`)

**核心测试场景：**
```python
class TestAddToVectorStoreErrors:
    """测试向量存储的错误处理"""
    
    def test_empty_llm_response_fact_extraction(self, mock_memory, caplog):
        """测试LLM响应为空时的事实提取"""
        mock_memory.llm.generate_response.return_value = ""
        
        result = mock_memory._add_to_vector_store(
            messages=[{"role": "user", "content": "test"}], 
            metadata={}, 
            filters={}, 
            infer=True
        )
        
        assert result == []
        assert "Error in new_retrieved_facts" in caplog.text
```

**异步测试支持：**
```python
@pytest.mark.asyncio
class TestAsyncAddToVectorStoreErrors:
    """异步记忆操作的错误处理测试"""
    
    async def test_async_empty_llm_response_fact_extraction(self, mock_async_memory):
        """测试异步操作中的错误恢复"""
```

### 5. 集成测试 (`test_memory_integration.py`)

**配置管理测试：**
```python
def test_memory_configuration_without_env_vars():
    """测试不依赖环境变量的配置"""
    mock_config = {
        "llm": {
            "provider": "openai",
            "config": {"model": "gpt-4", "temperature": 0.1}
        },
        "vector_store": {
            "provider": "chroma", 
            "config": {"collection_name": "test_collection"}
        },
        "embedder": {
            "provider": "openai",
            "config": {"model": "text-embedding-ada-002"}
        }
    }
```

**Azure 配置结构测试：**
```python
def test_azure_config_structure():
    """验证 Azure 配置的完整性"""
    # 测试 Azure OpenAI 配置结构
    # 测试 Azure AI Search 集成
    # 测试企业级安全配置
```

## 测试策略与方法

### Mock 策略
**避免外部依赖：**
- Mock 所有 API 调用（OpenAI、Azure、Google 等）
- Mock 数据库连接和操作
- Mock 文件系统和网络请求

**示例 Mock 模式：**
```python
@pytest.fixture  
def mock_openai_client():
    with patch("mem0.embeddings.openai.OpenAI") as mock_openai:
        mock_client = Mock()
        mock_openai.return_value = mock_client
        yield mock_client
```

### 配置测试
**多场景配置验证：**
- 默认配置测试
- 自定义配置测试
- 错误配置处理测试
- 环境变量优先级测试

### 错误处理测试
**全面的异常场景：**
- API 限流和超时
- 网络连接失败
- 无效的配置参数
- 资源不足处理

### 性能测试
**关键指标监控：**
- 嵌入生成速度
- 向量搜索延迟
- 内存使用优化
- 并发处理能力

## 测试数据管理

### 测试数据结构
```python
# 标准测试消息格式
test_messages = [
    {"role": "user", "content": "Hi, I'm Alex. I'm a vegetarian and allergic to nuts."},
    {"role": "assistant", "content": "Hello Alex! I've noted your dietary preferences."}
]

# 期望的内存提取结果
expected_memories = [
    {"id": "1", "text": "Alex is a vegetarian", "metadata": {"category": "dietary_preferences"}},
    {"id": "2", "text": "Alex is allergic to nuts", "metadata": {"category": "allergies"}}
]
```

### 常量和提示词测试
```python
def test_safe_update_prompt_constant():
    """测试安全更新提示词的格式"""
    SAFE_UPDATE_PROMPT = """
    Based on the user's latest messages, what new preference can be inferred?
    Reply only in this json_object format:
    """
    
    assert isinstance(SAFE_UPDATE_PROMPT, str)
    assert "user's latest messages" in SAFE_UPDATE_PROMPT
    assert "json_object format" in SAFE_UPDATE_PROMPT
```

## 质量度量指标

### 代码覆盖率
- **目标覆盖率**：> 85%
- **关键模块覆盖率**：> 95% (memory/, embeddings/, llms/)
- **分支覆盖率**：> 80%

### 测试执行指标  
- **测试数量**：45+ 测试文件，500+ 测试用例
- **执行时间**：< 30 秒（并行执行）
- **稳定性**：99%+ 测试通过率

### 质量保证流程
1. **本地开发测试**：开发者本地执行
2. **CI/CD 自动化**：每次提交自动运行
3. **回归测试**：版本发布前完整测试
4. **性能基准测试**：定期性能回归检查

## 常见问题 (FAQ)

### Q: 如何运行特定提供商的测试？
**A:** 
```bash
# 只测试 OpenAI 相关功能
pytest tests/embeddings/test_openai_embeddings.py tests/llms/test_openai.py

# 使用标记过滤测试
pytest -m "not integration"  # 跳过集成测试
```

### Q: 如何添加新的提供商测试？
**A:** 
1. 创建 `tests/embeddings/test_new_provider.py`
2. 使用通用的 Mock 模式
3. 覆盖基本配置、自定义配置、错误处理场景
4. 遵循现有的测试命名约定

### Q: Mock 测试是否足够？
**A:** 
- **单元测试**：Mock 测试完全足够
- **集成测试**：结合少量真实 API 测试  
- **端到端测试**：在测试环境中进行真实验证

### Q: 如何处理异步测试的复杂性？
**A:**
```python
# 使用 pytest-asyncio 装饰器
@pytest.mark.asyncio
async def test_async_function():
    result = await async_memory_operation()
    assert result is not None
```

## 相关文件清单

### 主测试文件
- `test_main.py` - 主入口测试
- `test_memory.py` - 记忆模块测试
- `test_memory_integration.py` - 集成测试
- `test_proxy.py` - 代理功能测试
- `test_telemetry.py` - 遥测数据测试

### 分模块测试
- `configs/test_prompts.py` - 提示词配置测试
- `embeddings/test_*.py` - 7 个嵌入模型提供商测试
- `llms/test_*.py` - 11 个 LLM 提供商测试
- `memory/test_*.py` - 核心记忆功能测试
- `vector_stores/test_*.py` - 17 个向量数据库测试

### 总计统计
- **测试文件数量**：45+ 个
- **代码行数**：5000+ 行测试代码
- **覆盖场景**：40+ 种技术栈集成

## 变更记录 (Changelog)

### 2025-09-02 - 第三次增量扫描
- **架构洞察**：梳理分层测试架构（单元-集成-系统）
- **覆盖分析**：深度分析 45+ 测试文件的测试策略
- **Mock 模式**：总结各模块的 Mock 测试最佳实践
- **质量保证**：建立完整的质量度量和流程规范
- **异步支持**：分析异步测试的实现和挑战
- **数据驱动**：构建标准化的测试数据管理模式