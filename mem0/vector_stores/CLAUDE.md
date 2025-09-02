[根目录](../../CLAUDE.md) > [mem0](../) > **vector_stores**

# 向量存储模块

## 变更记录 (Changelog)

### 2025-09-02 12:28:50 - 深度补扫
- 深入分析了向量存储模块的完整架构
- 发现支持 22 种向量数据库提供商
- 识别出统一的抽象基类设计模式
- 分析了配置系统与自动验证机制

---

## 模块职责

提供统一的向量存储抽象层，支持多种向量数据库后端，实现记忆的向量化存储、检索和管理功能。

## 入口与启动

- **基础抽象类**: `base.py` - 定义 `VectorStoreBase` 接口
- **配置管理**: `configs.py` - 动态配置验证和提供商映射
- **主要入口**: 通过 `VectorStoreConfig` 类自动加载对应提供商

## 对外接口

### 核心抽象接口 (`VectorStoreBase`)

```python
# 集合管理
def create_col(self, name, vector_size, distance)  # 创建集合
def delete_col(self)                               # 删除集合
def list_cols(self)                                # 列出所有集合
def col_info(self)                                 # 获取集合信息
def reset(self)                                    # 重置集合

# 向量操作
def insert(self, vectors, payloads=None, ids=None) # 插入向量
def search(self, query, vectors, limit=5, filters=None)  # 搜索相似向量
def get(self, vector_id)                           # 根据 ID 获取向量
def update(self, vector_id, vector=None, payload=None)  # 更新向量
def delete(self, vector_id)                        # 删除向量
def list(self, filters=None, limit=None)           # 列出所有记忆
```

## 关键依赖与配置

### 支持的向量数据库 (22 种)

**本地/开源数据库:**
- **Qdrant**: 高性能向量搜索引擎
- **Chroma**: 轻量级嵌入数据库
- **FAISS**: Facebook 的相似性搜索库
- **Milvus**: 可扩展的向量数据库
- **Redis**: 基于内存的向量存储
- **PostgreSQL (pgvector)**: 关系型数据库的向量扩展

**云服务提供商:**
- **Pinecone**: 托管向量数据库服务
- **Azure AI Search**: 微软认知搜索服务
- **MongoDB Atlas**: 文档数据库的向量搜索
- **Elasticsearch**: 搜索引擎的向量支持
- **OpenSearch**: 开源搜索平台
- **AWS S3 Vectors**: S3 存储的向量实现
- **Supabase**: 开源 Firebase 替代方案
- **Upstash Vector**: 无服务器向量数据库

**企业级/特殊用途:**
- **Databricks**: 统一分析平台
- **Weaviate**: GraphQL 向量数据库
- **Google Vertex AI**: 谷歌云 AI 平台
- **Baidu VectorDB**: 百度云向量数据库
- **LangChain**: 通过 LangChain 接入其他向量存储

### 配置系统设计

```python
class VectorStoreConfig(BaseModel):
    provider: str = "qdrant"  # 默认提供商
    config: Optional[Dict] = None  # 提供商特定配置
    
    # 自动映射提供商到配置类
    _provider_configs: Dict[str, str] = {
        "qdrant": "QdrantConfig",
        "chroma": "ChromaDbConfig",
        "pinecone": "PineconeConfig",
        # ... 22 种提供商映射
    }
```

### 自动配置验证

- **动态加载**: 根据 `provider` 自动导入对应配置类
- **默认路径**: 本地存储自动创建 `/tmp/{provider}` 目录
- **类型安全**: Pydantic 模型确保配置正确性

## 数据模型

### 向量存储抽象

```python
# 向量插入
vectors: List[float]           # 向量数据
payloads: Optional[Dict]       # 元数据负载
ids: Optional[List[str]]       # 向量 ID

# 搜索参数
query: Union[str, List[float]] # 查询向量或文本
limit: int = 5                 # 返回结果数量
filters: Optional[Dict]        # 过滤条件

# 距离度量
Distance.COSINE               # 余弦距离（默认）
Distance.EUCLIDEAN           # 欧几里得距离
Distance.DOT                 # 点积距离
```

### 实现示例 (Qdrant)

```python
class Qdrant(VectorStoreBase):
    def __init__(self, collection_name, embedding_model_dims, 
                 client=None, host=None, port=None, path=None, 
                 url=None, api_key=None, on_disk=False):
        # 支持多种连接方式:
        # - 现有客户端实例
        # - 远程服务器 (host:port 或 URL)
        # - 本地文件系统存储
        # - 内存存储 (on_disk=False)
```

## 测试与质量

### 测试覆盖

- **单元测试**: `tests/vector_stores/` 目录包含各提供商测试
- **集成测试**: 跨模块功能验证
- **配置测试**: 配置验证和错误处理测试

### 质量保证

- **统一接口**: 所有提供商遵循相同的 `VectorStoreBase` 接口
- **错误处理**: 连接失败、配置错误的统一异常处理
- **性能优化**: 支持批量操作和异步处理

## 常见问题 (FAQ)

**Q: 如何选择合适的向量数据库？**
A: 
- **开发测试**: Chroma、FAISS (轻量级，无需额外部署)
- **生产环境**: Qdrant、Pinecone (高性能，可扩展)
- **云原生**: Azure AI Search、MongoDB Atlas (托管服务)
- **企业级**: Databricks、Vertex AI (集成度高)

**Q: 如何切换向量数据库提供商？**
A: 只需修改配置中的 `provider` 和 `config` 参数，代码无需改动。

**Q: 支持自定义向量数据库吗？**
A: 继承 `VectorStoreBase` 类并实现所有抽象方法即可。

## 相关文件清单

### 核心文件
- `base.py` - 抽象基类定义 (59 行)
- `configs.py` - 配置管理和提供商映射 (63 行)

### 数据库提供商实现 (22 个)
- `qdrant.py` - Qdrant 向量数据库支持
- `chroma.py` - ChromaDB 支持  
- `pinecone.py` - Pinecone 云服务支持
- `faiss.py` - Facebook FAISS 库支持
- `pgvector.py` - PostgreSQL 向量扩展支持
- `redis.py` - Redis 向量存储支持
- `mongodb.py` - MongoDB Atlas 向量搜索
- `elasticsearch.py` - Elasticsearch 向量支持
- `azure_ai_search.py` - Azure 认知搜索
- `supabase.py` - Supabase 向量支持
- `weaviate.py` - Weaviate GraphQL 数据库
- `milvus.py` - Milvus 向量数据库
- `opensearch.py` - OpenSearch 支持
- `upstash_vector.py` - Upstash 无服务器向量DB
- `databricks.py` - Databricks 统一分析平台
- `vertex_ai_vector_search.py` - Google Vertex AI
- `s3_vectors.py` - AWS S3 向量存储
- `baidu.py` - 百度云向量数据库
- `langchain.py` - LangChain 向量存储接入

### 配置文件 (对应提供商)
- `../configs/vector_stores/*.py` - 各提供商的 Pydantic 配置类

---

**模块特色**: 业界最全面的向量数据库支持，统一抽象接口设计，零配置切换提供商