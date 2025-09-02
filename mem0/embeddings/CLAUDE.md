[根目录](../../CLAUDE.md) > [mem0](../CLAUDE.md) > **embeddings**

# Mem0 嵌入模型模块

## 模块职责

嵌入模型模块是 Mem0 框架的核心组件，负责将文本转换为高维向量表示，为记忆的存储和检索提供语义基础。该模块通过统一的抽象层支持多种嵌入模型提供商，确保灵活性和可扩展性。

## 入口与启动

**主要入口点：**
- `embeddings/__init__.py` - 模块初始化（空文件，通过工厂模式动态创建）
- `embeddings/base.py` - 抽象基类定义
- `embeddings/configs.py` - 配置验证和提供商映射

**核心架构：**
```python
# 通过工厂模式创建嵌入器实例
from mem0.utils.factory import EmbedderFactory
embedder = EmbedderFactory.create(config)
```

## 对外接口

### 核心抽象接口

**EmbeddingBase (基类)：**
```python
class EmbeddingBase(ABC):
    def __init__(self, config: Optional[BaseEmbedderConfig] = None)
    
    @abstractmethod
    def embed(self, text: str, memory_action: Optional[Literal["add", "search", "update"]]) -> List[float]
```

**配置管理：**
```python
class EmbedderConfig(BaseModel):
    provider: str = "openai"  # 提供商名称
    config: Optional[dict] = {}  # 特定配置
```

### 支持的提供商 (10种)

#### 商业云服务
1. **OpenAI** (`openai.py`)
   - 模型：text-embedding-3-small (默认)、text-embedding-3-large
   - 维度：1536 (可配置)
   - 特性：高质量、API 稳定

2. **Azure OpenAI** (`azure_openai.py`)
   - Azure 托管的 OpenAI 服务
   - 支持 Azure AD 认证
   - 企业级安全保障

3. **Google Gemini** (`gemini.py`)
   - 模型：text-embedding-004
   - 维度：768 (可配置)
   - Google AI 平台集成

4. **AWS Bedrock** (`aws_bedrock.py`)
   - 亚马逊托管的嵌入服务
   - 企业级云原生支持

5. **Vertex AI** (`vertexai.py`)
   - Google Cloud 的企业 AI 平台
   - 与 GCP 生态深度集成

6. **Together** (`together.py`)
   - 专注于开源模型的云服务
   - 高性价比选择

#### 本地化部署
7. **Ollama** (`ollama.py`)
   - 模型：nomic-embed-text (默认)
   - 维度：512
   - 本地运行，数据隐私保护
   - 自动模型下载和管理

8. **Hugging Face** (`huggingface.py`)
   - 模型：multi-qa-MiniLM-L6-cos-v1 (默认)
   - 支持本地和 API 两种模式
   - 开源模型生态

9. **LM Studio** (`lmstudio.py`)
   - 本地模型服务器
   - 用户友好的界面

#### 集成框架
10. **Langchain** (`langchain.py`)
    - 与 Langchain 生态集成
    - 复用现有嵌入器配置

## 关键依赖与配置

### 核心依赖
```python
# 必需依赖
from abc import ABC, abstractmethod
from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

# 提供商特定依赖
openai              # OpenAI 和 Azure
google-genai        # Google Gemini
sentence_transformers  # Hugging Face
ollama              # Ollama 客户端
```

### 配置示例

**OpenAI 配置：**
```python
config = {
    "provider": "openai",
    "config": {
        "model": "text-embedding-3-small",
        "api_key": "your-api-key",
        "embedding_dims": 1536
    }
}
```

**本地 Ollama 配置：**
```python
config = {
    "provider": "ollama", 
    "config": {
        "model": "nomic-embed-text",
        "ollama_base_url": "http://localhost:11434",
        "embedding_dims": 512
    }
}
```

**Azure 配置：**
```python
config = {
    "provider": "azure_openai",
    "config": {
        "model": "text-embedding-ada-002",
        "azure_kwargs": {
            "azure_deployment": "your-deployment",
            "azure_endpoint": "https://your-service.openai.azure.com/",
            "api_version": "2023-12-01-preview"
        }
    }
}
```

## 数据模型

### 输入数据结构
```python
# 嵌入请求
text: str                    # 待嵌入文本
memory_action: Optional[Literal["add", "search", "update"]]  # 内存操作类型
```

### 输出数据结构  
```python
# 嵌入结果
embedding: List[float]       # 向量表示，维度取决于模型
```

### 配置数据结构
```python
class BaseEmbedderConfig:
    model: Optional[str]           # 模型名称
    embedding_dims: Optional[int]  # 嵌入维度
    api_key: Optional[str]         # API 密钥
    # ... 其他提供商特定配置
```

## 测试与质量

### 测试覆盖
- **单元测试**：`tests/embeddings/` 目录
  - `test_openai_embeddings.py` - OpenAI 嵌入器测试
  - `test_azure_openai_embeddings.py` - Azure 嵌入器测试
  - `test_huggingface_embeddings.py` - HuggingFace 测试
  - `test_ollama_embeddings.py` - Ollama 测试
  - 等其他提供商测试

### 测试策略
- **Mock 测试**：避免真实 API 调用
- **配置验证**：测试各种配置组合
- **错误处理**：API 失败、网络异常等场景
- **维度一致性**：确保输出向量维度正确

### 质量保证
- **类型提示**：完整的 Python 类型注解
- **文档字符串**：详细的方法说明
- **异常处理**：优雅的错误恢复
- **日志记录**：调试和监控支持

## 常见问题 (FAQ)

### Q: 如何选择合适的嵌入模型？
**A:** 考虑以下因素：
- **性能需求**：OpenAI 质量最高，Ollama 本地运行
- **成本考虑**：开源模型成本更低
- **数据隐私**：本地部署避免数据传输
- **语言支持**：多语言场景选择对应优化模型

### Q: 如何配置自定义嵌入维度？
**A:** 在配置中设置 `embedding_dims` 参数：
```python
config = {
    "provider": "openai",
    "config": {
        "embedding_dims": 1024  # 自定义维度
    }
}
```

### Q: 嵌入模型可以热切换吗？
**A:** 不建议在生产中热切换，因为：
- 不同模型的向量空间不兼容
- 需要重新构建整个向量数据库
- 建议在系统初始化时确定模型

### Q: 如何处理嵌入API限流？
**A:** 
- 实现指数退避重试机制
- 配置合适的请求速率限制
- 考虑使用批处理减少API调用

### Q: Ollama 模型如何自动下载？
**A:** Ollama 嵌入器会自动检查本地模型：
```python
def _ensure_model_exists(self):
    local_models = self.client.list()["models"]
    if not any(model.get("name") == self.config.model for model in local_models):
        self.client.pull(self.config.model)  # 自动下载
```

## 相关文件清单

### 核心文件
- `base.py` - 抽象基类和接口定义
- `configs.py` - 配置管理和验证
- `__init__.py` - 模块入口（空文件）

### 提供商实现
- `openai.py` - OpenAI 嵌入模型
- `azure_openai.py` - Azure OpenAI 服务
- `huggingface.py` - Hugging Face 模型
- `ollama.py` - Ollama 本地服务
- `gemini.py` - Google Gemini
- `vertexai.py` - Google Vertex AI
- `aws_bedrock.py` - AWS Bedrock
- `together.py` - Together AI
- `lmstudio.py` - LM Studio
- `langchain.py` - Langchain 集成
- `mock.py` - 测试用模拟器

### 测试文件
- `tests/embeddings/test_*.py` - 各提供商单元测试

## 变更记录 (Changelog)

### 2025-09-02 - 第三次增量扫描
- **新增功能**：
  - 完成 10 种嵌入模型提供商的深度分析
  - 详细梳理配置管理和验证机制
  - 分析本地部署和云服务的区别
- **架构洞察**：
  - 统一抽象层设计支持灵活扩展
  - 自动模型管理（Ollama）和批处理优化
  - 企业级安全（Azure AD）和隐私保护（本地部署）
- **质量保证**：
  - 全面的单元测试覆盖
  - Mock 测试避免真实 API 调用
  - 类型提示和异常处理完备