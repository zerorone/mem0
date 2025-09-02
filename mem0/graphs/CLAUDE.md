[根目录](../../CLAUDE.md) > [mem0](../) > **graphs**

# 图数据库模块

## 变更记录 (Changelog)

### 2025-09-02 12:28:50 - 深度补扫
- 完成图数据库模块的深入分析
- 发现支持 4 种图数据库：Neo4j、Memgraph、Neptune、Kuzu
- 识别出完整的图记忆管理工具链
- 分析了实体关系抽取和图更新机制

---

## 模块职责

提供图数据库集成能力，支持知识图谱的构建和查询，实现基于图结构的记忆存储和关系推理。

## 入口与启动

- **配置入口**: `configs.py` - 图数据库配置管理
- **工具定义**: `tools.py` - 图操作的函数调用工具
- **实用函数**: `utils.py` - 图更新和关系抽取提示词
- **Neptune 实现**: `neptune/` - AWS Neptune 图数据库支持

## 对外接口

### 支持的图数据库

**1. Neo4j** (开源图数据库领导者)
```python
Neo4jConfig:
    url: str          # 数据库连接 URL
    username: str     # 用户名  
    password: str     # 密码
    database: str     # 数据库名称 (可选)
    base_label: bool  # 是否使用基础实体标签
```

**2. Memgraph** (高性能图数据库)
```python
MemgraphConfig:
    url: str          # 数据库连接 URL
    username: str     # 用户名
    password: str     # 密码
```

**3. AWS Neptune** (云原生图数据库)
```python
NeptuneConfig:
    app_id: str = "Mem0"                    # 应用 ID
    endpoint: str                           # Neptune 端点
    # 格式: "neptune-graph://<graphid>"
    base_label: bool                        # 基础实体标签
    graph_identifier: str (自动生成)        # 图标识符
```

**4. Kuzu** (嵌入式图数据库)
```python
KuzuConfig:
    db: str = ":memory:"    # 数据库路径，默认内存模式
```

### 图操作工具 (`tools.py`)

#### 实体和关系管理
```python
# 添加图记忆
ADD_MEMORY_TOOL_GRAPH:
    source: str           # 源节点
    destination: str      # 目标节点  
    relationship: str     # 关系类型
    source_type: str      # 源节点类型
    destination_type: str # 目标节点类型

# 更新图记忆
UPDATE_MEMORY_TOOL_GRAPH:
    source: str           # 源节点 (不变)
    destination: str      # 目标节点 (不变)
    relationship: str     # 新的关系描述

# 删除图记忆
DELETE_MEMORY_TOOL_GRAPH:
    source: str           # 源节点
    relationship: str     # 要删除的关系
    destination: str      # 目标节点
```

#### 实体抽取工具
```python
# 抽取实体
EXTRACT_ENTITIES_TOOL:
    entities: List[{
        entity: str,       # 实体名称
        entity_type: str   # 实体类型
    }]

# 建立关系
RELATIONS_TOOL:
    entities: List[{
        source: str,       # 源实体
        relationship: str, # 关系描述
        destination: str   # 目标实体
    }]
```

## 关键依赖与配置

### 图数据库配置系统

```python
class GraphStoreConfig(BaseModel):
    provider: str = "neo4j"                    # 默认提供商
    config: Union[Neo4j, Memgraph, Neptune, Kuzu] # 提供商配置
    llm: Optional[LlmConfig] = None            # 图查询的 LLM 配置
    custom_prompt: Optional[str] = None        # 自定义实体抽取提示词
```

### LLM 集成

图模块依赖 LLM 进行：
- **实体抽取**: 从文本中识别实体和类型
- **关系推理**: 确定实体间的关系类型
- **图更新决策**: 判断是否需要更新/删除现有关系
- **图查询理解**: 将自然语言转换为图查询

## 数据模型

### 图记忆格式

```
source -- RELATIONSHIP -- destination

示例:
USER_ID -- loves_to_eat -- pizza
Alice -- professor -- Stanford_University
Python -- programming_language -- general_purpose
```

### 实体类型系统

- **USER_ID**: 用户自引用 ("我"、"我的" 等)
- **PERSON**: 人员实体
- **ORGANIZATION**: 组织机构
- **CONCEPT**: 概念和抽象事物
- **OBJECT**: 具体物品
- **LOCATION**: 地理位置
- **EVENT**: 事件和活动

### 关系更新策略

1. **识别**: 使用源节点和目标节点作为主要标识符
2. **冲突解决**:
   - 新信息更准确/更新时，更新现有关系
   - 相同类型关系但不同目标节点时，保持并存
3. **时间感知**: 优先考虑最新信息
4. **语义一致**: 维护图的整体语义结构

## 测试与质量

### Neptune 实现

`neptune/` 子模块提供了 AWS Neptune 的完整实现：
- `base.py` - Neptune 连接和基础操作
- `main.py` - 主要的图操作实现
- 支持 Neptune Analytics Graph (以 `g-` 开头的图标识符)

### 配置验证

- **端点格式检查**: 确保 Neptune 端点格式正确
- **连接参数验证**: 验证数据库连接所需的必要参数
- **类型安全**: Pydantic 模型确保配置类型正确

## 常见问题 (FAQ)

**Q: 如何选择合适的图数据库？**
A:
- **开发测试**: Kuzu (嵌入式，零配置)
- **生产环境**: Neo4j (成熟稳定，社区活跃)
- **高性能需求**: Memgraph (内存优化，流处理)
- **云原生**: AWS Neptune (托管服务，与 AWS 集成)

**Q: 图记忆与向量记忆有什么区别？**
A:
- **向量记忆**: 基于相似度的语义搜索
- **图记忆**: 基于关系的结构化知识推理
- **互补使用**: 向量用于内容检索，图用于关系推理

**Q: 如何处理关系冲突？**
A: 使用 `UPDATE_GRAPH_PROMPT` 系统提示词，通过 LLM 判断是否更新、删除或保持现有关系。

## 相关文件清单

### 核心配置文件
- `configs.py` - 图数据库配置管理 (104 行)
- `utils.py` - 图更新提示词和工具函数 (98 行)
- `tools.py` - 图操作的函数调用工具定义 (372 行)

### Neptune 实现
- `neptune/__init__.py` - Neptune 模块导出
- `neptune/base.py` - Neptune 基础连接实现
- `neptune/main.py` - Neptune 主要功能实现

### 提示词系统
- **UPDATE_GRAPH_PROMPT**: 图记忆更新决策提示词
- **EXTRACT_RELATIONS_PROMPT**: 实体关系抽取提示词  
- **DELETE_RELATIONS_SYSTEM_PROMPT**: 关系删除决策提示词

### 工具定义 (结构化/非结构化版本)
- 添加/更新/删除图记忆工具
- 实体抽取和关系建立工具
- 空操作 (NOOP) 工具

---

**模块特色**: 多图数据库支持，智能关系推理，LLM 驱动的图更新决策