# 支持向量相似度的开源图数据库方案 2025

## 🎯 问题总结

Neo4j 和 Memgraph 社区版都缺少向量相似度功能：
- **Neo4j 社区版**: 缺少 `vector.similarity.cosine` 函数  
- **Memgraph 社区版**: 缺少 `node_similarity.cosine_pairwise` 函数

## ✅ 支持图+向量的开源数据库方案

### 1. FalkorDB ⭐⭐⭐⭐⭐ (强烈推荐)

**简介**: RedisGraph 的继任者，专门为 AI/GraphRAG 应用设计

**核心优势**:
- ✅ **完全免费开源** (Apache 2.0 License)
- ✅ **原生支持向量搜索** (余弦相似度、欧几里得距离)
- ✅ **图+向量混合查询** (GraphRAG 优化)
- ✅ **50x 性能提升** (相比传统图数据库)
- ✅ **完整的 Cypher 查询语言支持**

**技术特性**:
```cypher
// 创建向量索引
CREATE VECTOR INDEX FOR (n:Person) ON n.embedding

// 图+向量混合查询
MATCH (user:User {id: $userId})
CALL db.idx.vector.similarity('Person', 'embedding', $queryVector, 10) 
YIELD node, similarity
RETURN node, similarity
```

**部署方式**:
```bash
# Docker 部署
docker run -p 6379:6379 falkordb/falkordb:latest

# 或者使用 FalkorDB Cloud (免费层)
```

### 2. ArangoDB ⭐⭐⭐⭐

**简介**: 多模型数据库 (文档+图+向量)

**核心优势**:
- ✅ **开源社区版免费**
- ✅ **原生向量搜索支持**
- ✅ **图+文档+向量统一查询**
- ✅ **成熟的生态系统**
- ✅ **完整的 AQL 查询语言**

**技术特性**:
```aql
// AQL 图+向量查询示例
FOR doc IN NEAR('collection', @vector, 10, 'cosine')
  LET paths = (
    FOR v, e IN 1..3 OUTBOUND doc._id GRAPH 'myGraph'
    RETURN {vertex: v, edge: e}
  )
  RETURN {document: doc, paths: paths}
```

**部署方式**:
```bash
# Docker 部署
docker run -p 8529:8529 arangodb/arangodb:latest
```

### 3. PostgreSQL + pgvector + AGE ⭐⭐⭐⭐

**简介**: PostgreSQL 扩展组合方案

**核心优势**:
- ✅ **完全免费开源**
- ✅ **pgvector**: 向量相似度搜索
- ✅ **Apache AGE**: 图数据库扩展
- ✅ **SQL + Cypher 混合查询**
- ✅ **生产级稳定性**

**技术特性**:
```sql
-- 创建向量索引
CREATE INDEX ON embeddings USING ivfflat (vector vector_cosine_ops);

-- 图+向量混合查询
SELECT ag.*, v.similarity
FROM cypher('graph', $$
  MATCH (n:Person)-[r:KNOWS]->(m:Person)
  RETURN n, r, m
$$) AS ag(n agtype, r agtype, m agtype)
JOIN LATERAL (
  SELECT 1 - (embedding <=> $1::vector) AS similarity
  FROM embeddings WHERE id = (ag.n->>'id')::int
) v ON true
ORDER BY v.similarity DESC;
```

**部署方式**:
```bash
# Docker 部署
docker run -p 5432:5432 \
  -e POSTGRES_DB=graphdb \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  apache/age:latest
```

### 4. 混合方案: ChromaDB + 图数据库API层 ⭐⭐⭐

**简介**: 应用层组合 ChromaDB 和简单图数据库

**实现思路**:
```python
class HybridGraphVector:
    def __init__(self):
        self.vector_db = chromadb.Client()
        self.graph_db = simple_graph_db()  # 如 NetworkX + 持久化
    
    def hybrid_search(self, query_vector, graph_constraints):
        # 1. 向量搜索获得候选
        vector_results = self.vector_db.query(
            query_embeddings=[query_vector],
            n_results=100
        )
        
        # 2. 图约束过滤
        filtered_results = self.graph_db.filter_by_constraints(
            vector_results, graph_constraints
        )
        
        return filtered_results
```

## 📊 方案对比表

| 数据库 | 向量搜索 | 图遍历 | 查询语言 | 性能 | 部署难度 | 推荐度 |
|--------|----------|--------|----------|------|----------|---------|
| **FalkorDB** | ✅ 原生 | ✅ 原生 | Cypher | ⭐⭐⭐⭐⭐ | 极简 | ⭐⭐⭐⭐⭐ |
| **ArangoDB** | ✅ 原生 | ✅ 原生 | AQL | ⭐⭐⭐⭐ | 中等 | ⭐⭐⭐⭐ |
| **PG+pgvector+AGE** | ✅ 扩展 | ✅ 扩展 | SQL+Cypher | ⭐⭐⭐ | 复杂 | ⭐⭐⭐⭐ |
| **混合方案** | ✅ 外部 | ✅ 自建 | Python | ⭐⭐⭐ | 中等 | ⭐⭐⭐ |
| Neo4j 社区版 | ❌ | ✅ 原生 | Cypher | ⭐⭐⭐⭐ | 简单 | ⭐⭐ |
| Memgraph 社区版 | ❌ | ✅ 原生 | Cypher | ⭐⭐⭐⭐ | 简单 | ⭐⭐ |

## 🚀 推荐实施方案

### 方案 1: FalkorDB (首选)

**优势**:
- 专门为 GraphRAG 设计，完美匹配 Mem0 需求
- 部署最简单，性能最优
- 原生 Cypher 支持，易于迁移

**部署步骤**:
```bash
# 1. 启动 FalkorDB
docker run -d \
  --name mem0-falkordb \
  -p 6379:6379 \
  falkordb/falkordb:latest

# 2. 修改 Mem0 配置支持 FalkorDB
# (需要开发 FalkorDB 适配器)
```

### 方案 2: PostgreSQL + pgvector + AGE (稳妥选择)

**优势**:
- 企业级稳定性
- 丰富的生态系统
- 完全开源免费

**部署步骤**:
```bash
# 使用预构建的 AGE + pgvector 镜像
docker run -d \
  --name mem0-postgres-graph \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=mem0pass \
  apache/age:pg13-latest
```

## 🔧 Mem0 集成方案

### 为 FalkorDB 创建适配器

由于 Mem0 目前不支持 FalkorDB，需要创建自定义适配器：

```python
# mem0/graphs/falkordb/main.py
class FalkorDBMemory(MemoryGraphBase):
    def __init__(self, config):
        self.client = falkordb.FalkorDB(
            host=config.host,
            port=config.port
        )
        self.graph = self.client.select_graph('mem0_graph')
    
    def add(self, data, filters):
        # 实现向量+图的混合存储
        pass
    
    def search(self, query, **kwargs):
        # 实现向量相似度+图遍历查询
        cypher = """
        CALL db.idx.vector.query('embedding', $vector) 
        YIELD node, score
        MATCH (node)-[r]-(connected)
        RETURN node, r, connected, score
        """
        return self.graph.query(cypher, vector=query.embedding)
```

## 💡 立即行动建议

1. **快速验证**: 先部署 FalkorDB 进行功能测试
2. **性能测试**: 对比 FalkorDB vs 纯 ChromaDB 的性能
3. **开发适配器**: 为 Mem0 创建 FalkorDB 图存储适配器
4. **渐进迁移**: 从纯向量逐步迁移到混合模式

## 📞 获取帮助

- **FalkorDB 文档**: https://docs.falkordb.com/
- **ArangoDB 文档**: https://docs.arangodb.com/
- **Apache AGE 文档**: https://age.apache.org/

**结论**: FalkorDB 是目前最佳的开源图+向量数据库选择，专门为 GraphRAG 应用优化，完美解决 Neo4j/Memgraph 社区版的限制！