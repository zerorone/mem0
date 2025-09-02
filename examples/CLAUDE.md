[根目录](../CLAUDE.md) > **examples**

# 示例与演示模块

## 变更记录 (Changelog)

### 2025-09-02 12:28:50 - 深度补扫
- 完成示例模块的全面分析
- 发现 4 大类示例：图数据库、交互演示、多模态、多代理
- 识别出完整的应用场景和最佳实践
- 分析了前端集成和实时交互能力

---

## 模块职责

提供 Mem0 框架的实际应用示例，涵盖不同使用场景和技术栈集成，帮助开发者快速上手和理解最佳实践。

## 入口与启动

### 示例分类结构

```
examples/
├── graph-db-demo/          # 图数据库集成演示
├── mem0-demo/              # Next.js 交互式演示应用
├── multimodal-demo/        # React 多模态演示应用  
├── multiagents/            # 多代理系统示例
└── misc/                   # 各种应用场景示例
```

## 对外接口

### 1. 图数据库演示 (`graph-db-demo/`)

**支持的图数据库:**
- **Neo4j**: 业界标准图数据库演示
- **Memgraph**: 高性能图数据库集成
- **AWS Neptune**: 云原生图数据库示例
- **Kuzu**: 嵌入式图数据库演示

**演示内容:**
```python
# Neo4j 示例配置
config = {
    "embedder": {
        "provider": "openai",
        "config": {"model": "text-embedding-3-large", "embedding_dims": 1536},
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password",
        },
    },
}

# 记忆存储和检索
m = Memory.from_config(config_dict=config)
result = m.add(messages, user_id="alice")
memories = m.search("what does alice love?", user_id="alice")
```

**可视化效果:**
- Alice 的记忆关系图谱
- Neptune 可视化界面截图
- 实体关系网络展示

### 2. 交互式演示应用 (`mem0-demo/`)

**技术栈:**
- **Next.js 14**: React 框架
- **TypeScript**: 类型安全开发
- **Tailwind CSS**: 样式框架
- **Assistant UI**: 对话界面组件

**核心功能:**
```typescript
// API 路由示例 (app/api/chat/route.ts)
export async function POST(req: Request) {
  // 处理对话请求
  // 调用 Mem0 API
  // 返回流式响应
}

// 记忆指示器组件
<MemoryIndicator memories={memories} />

// 对话线程管理
<ThreadList threads={threads} />
```

**特色功能:**
- 实时记忆更新显示
- 对话历史管理
- 主题切换支持
- 响应式设计

### 3. 多模态演示 (`multimodal-demo/`)

**技术栈:**
- **React + Vite**: 现代前端工具链
- **TypeScript**: 类型安全
- **Tailwind CSS + shadcn/ui**: UI 组件库

**多模态支持:**
- **文本输入**: 自然语言对话
- **文件上传**: PDF、图片处理
- **语音输入**: 语音转文字 (计划)
- **视频处理**: 视频内容分析 (计划)

**核心组件:**
```typescript
// 文件处理钩子
const { handleFileUpload, isUploading } = useFileHandler();

// 聊天功能钩子  
const { messages, sendMessage, isLoading } = useChat();

// 认证管理
const { user, login, logout } = useAuth();
```

### 4. 多代理系统 (`multiagents/`)

**LlamaIndex 学习系统:**
```python
# 学习代理示例
from llama_index import ServiceContext, VectorStoreIndex
from mem0 import Memory

class LearningAgent:
    def __init__(self):
        self.memory = Memory()
        self.index = VectorStoreIndex(...)
    
    def learn_from_document(self, doc):
        # 文档理解和记忆存储
        pass
    
    def answer_question(self, question, user_id):
        # 基于记忆的问答
        pass
```

### 5. 应用场景示例 (`misc/`)

**个人助手类:**
- `personal_assistant_agno.py` - Agno 框架集成的个人助手
- `study_buddy.py` - AI 学习伙伴，支持 PDF 上传和记忆
- `diet_assistant_voice_cartesia.py` - 语音饮食助手 (Cartesia TTS)
- `voice_assistant_elevenlabs.py` - ElevenLabs 语音助手

**专业应用:**
- `healthcare_assistant_google_adk.py` - 医疗助手 (Google ADK)
- `fitness_checker.py` - 健身追踪助手
- `movie_recommendation_grok3.py` - 电影推荐系统 (Grok3)
- `personalized_search.py` - 个性化搜索引擎

**技术集成:**
- `multillm_memory.py` - 多 LLM 记忆系统
- `vllm_example.py` - vLLM 高性能推理集成

## 关键依赖与配置

### 环境变量配置

```bash
# 基础 API 密钥
export OPENAI_API_KEY="your_openai_api_key"
export MEM0_API_KEY="your_mem0_api_key"

# 其他服务集成
export ANTHROPIC_API_KEY="your_anthropic_key"
export GROQ_API_KEY="your_groq_key"
export ELEVEN_LABS_API_KEY="your_elevenlabs_key"
```

### Docker 环境支持

**Neo4j 快速启动:**
```bash
docker run \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5
```

**前端应用启动:**
```bash
# mem0-demo
cd examples/mem0-demo
npm install && npm run dev

# multimodal-demo  
cd examples/multimodal-demo
npm install && npm run dev
```

## 数据模型

### 学习伙伴示例数据流

```python
# PDF 上传和处理
def upload_pdf(pdf_url: str, user_id: str):
    pdf_message = {
        "role": "user", 
        "content": {
            "type": "pdf_url", 
            "pdf_url": {"url": pdf_url}
        }
    }
    client.add([pdf_message], user_id=user_id)

# 上下文记忆检索
memories = client.search(f"{topic}", user_id=user_id)
memory_context = "\n".join(f"- {m['memory']}" for m in memories)
```

### 多模态数据结构

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  attachments?: FileAttachment[];
  timestamp: Date;
  memories?: Memory[];
}

interface FileAttachment {
  type: 'pdf' | 'image' | 'audio';
  url: string;
  name: string;
  size: number;
}
```

## 测试与质量

### 示例完整性

- **runnable**: 所有示例都是可直接运行的完整应用
- **环境隔离**: 每个示例都有独立的依赖管理
- **配置文档**: 详细的设置和运行说明
- **错误处理**: 完善的异常处理和用户提示

### 最佳实践展示

- **配置管理**: 统一的环境变量和配置模式
- **错误恢复**: 网络失败和 API 限制的处理
- **用户体验**: 加载状态、错误提示、响应式设计
- **性能优化**: 流式响应、懒加载、缓存策略

## 常见问题 (FAQ)

**Q: 如何运行图数据库示例？**
A: 
1. 启动对应的图数据库 (Docker 或云服务)
2. 配置连接参数和 API 密钥
3. 运行 Jupyter Notebook 文件

**Q: 前端演示需要哪些环境？**
A: Node.js 18+, npm/yarn, 对应的 API 密钥配置

**Q: 多模态演示支持哪些文件格式？**
A: 目前支持 PDF 和常见图片格式，语音和视频功能在开发中

**Q: 可以直接用于生产环境吗？**
A: 示例代码主要用于学习和原型开发，生产使用需要额外的安全性和错误处理优化

## 相关文件清单

### 图数据库演示
- `graph-db-demo/neo4j-example.ipynb` - Neo4j 集成演示
- `graph-db-demo/memgraph-example.ipynb` - Memgraph 使用示例  
- `graph-db-demo/neptune-example.ipynb` - AWS Neptune 演示
- `graph-db-demo/kuzu-example.ipynb` - Kuzu 嵌入式图数据库
- `graph-db-demo/*.png` - 可视化截图和图表

### 交互式演示应用
- `mem0-demo/app/` - Next.js 应用主体
- `mem0-demo/components/` - UI 组件库
- `mem0-demo/package.json` - 项目依赖配置

### 多模态演示
- `multimodal-demo/src/` - React 应用源码
- `multimodal-demo/src/components/` - 多模态组件
- `multimodal-demo/src/hooks/` - 自定义 React 钩子

### 多代理系统
- `multiagents/llamaindex_learning_system.py` - LlamaIndex 集成学习系统

### 应用场景示例 (11 个)
- `misc/study_buddy.py` - AI 学习伙伴 (87 行)
- `misc/personal_assistant_agno.py` - 个人助手集成
- `misc/diet_assistant_voice_cartesia.py` - 语音饮食助手
- `misc/healthcare_assistant_google_adk.py` - 医疗助手
- `misc/movie_recommendation_grok3.py` - 电影推荐系统
- `misc/fitness_checker.py` - 健身追踪助手
- `misc/voice_assistant_elevenlabs.py` - ElevenLabs 语音助手
- `misc/personalized_search.py` - 个性化搜索
- `misc/multillm_memory.py` - 多 LLM 记忆系统
- `misc/vllm_example.py` - vLLM 高性能推理
- `misc/test.py` - 基础测试示例

---

**模块特色**: 全栈应用示例，多技术栈集成，生产级最佳实践展示