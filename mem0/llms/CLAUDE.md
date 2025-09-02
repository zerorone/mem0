[根目录](../../CLAUDE.md) > [mem0](../) > **llms**

# LLM 提供商集成模块

## 变更记录 (Changelog)

### 2025-09-02 12:28:50 - 深度补扫
- 完成 LLM 模块的深入分析
- 发现支持 18 种 LLM 提供商
- 识别出统一的 LLM 抽象基类和推理模型支持
- 分析了结构化输出和工具调用能力

---

## 模块职责

提供统一的大语言模型抽象层，支持多种 LLM 提供商，实现记忆系统中的文本生成、实体抽取、关系推理等核心功能。

## 入口与启动

- **基础抽象类**: `base.py` - 定义 `LLMBase` 统一接口
- **配置管理**: `configs.py` - LLM 提供商配置验证
- **主要入口**: 通过 `LlmConfig` 类自动加载对应提供商

## 对外接口

### 核心抽象接口 (`LLMBase`)

```python
class LLMBase(ABC):
    def __init__(self, config: Union[BaseLlmConfig, Dict])
    
    # 核心生成方法
    @abstractmethod
    def generate_response(self, 
                         messages: List[Dict[str, str]], 
                         tools: Optional[List[Dict]] = None,
                         tool_choice: str = "auto", 
                         **kwargs)
    
    # 推理模型检测
    def _is_reasoning_model(self, model: str) -> bool
    def _get_supported_params(self, **kwargs) -> Dict
```

### 支持的 LLM 提供商 (19 种)

**主流商业提供商:**
- **OpenAI**: GPT-4, GPT-3.5, GPT-4o, GPT-5, o1 系列
- **Anthropic**: Claude 系列模型
- **Google**: Gemini Pro, Gemini Flash 等
- **Microsoft**: Azure OpenAI 服务
- **Deepseek**: 中国领先的 AI 模型
- **GLM (智谱清言)**: GLM-4, GLM-4.5 系列，支持深度思考模式

**专业化服务:**
- **Groq**: 高性能推理引擎
- **Together**: 开源模型托管平台
- **LiteLLM**: 统一 LLM API 包装器
- **XAI**: Elon Musk 的 AI 公司 (Grok 系列)
- **Sarvam**: 专注印度语言的 AI 模型

**开源和自托管:**
- **Ollama**: 本地 LLM 运行引擎
- **LM Studio**: 本地 LLM 管理工具
- **vLLM**: 高性能 LLM 推理服务器
- **LangChain**: 通过 LangChain 接入其他 LLM

**云平台集成:**
- **AWS Bedrock**: 亚马逊云的 LLM 服务
- **结构化输出支持**: `openai_structured`, `azure_openai_structured`

## 关键依赖与配置

### 推理模型特殊处理

```python
def _is_reasoning_model(self, model: str) -> bool:
    reasoning_models = {
        "o1", "o1-preview", "o3-mini", "o3",
        "gpt-5", "gpt-5o", "gpt-5o-mini", "gpt-5o-micro",
    }
    # 推理模型不支持某些参数 (temperature, top_p 等)
```

### 参数支持策略

**推理模型支持的参数:**
- `messages` - 对话历史
- `response_format` - 响应格式
- `tools` - 工具调用定义
- `tool_choice` - 工具选择策略

**常规模型额外支持:**
- `temperature` - 创造性控制
- `max_tokens` - 最大生成长度
- `top_p` - 核采样参数
- 其他提供商特定参数

### 配置系统

```python
class LlmConfig(BaseModel):
    provider: str = "openai"        # 默认提供商
    config: Optional[dict] = {}     # 提供商特定配置
    
    # 支持的提供商列表
    SUPPORTED_PROVIDERS = [
        "openai", "ollama", "anthropic", "groq", "together",
        "aws_bedrock", "litellm", "azure_openai", 
        "openai_structured", "azure_openai_structured",
        "gemini", "deepseek", "xai", "sarvam", 
        "lmstudio", "vllm", "langchain", "glm"
    ]
```

## 数据模型

### 消息格式

```python
messages: List[Dict[str, str]] = [
    {"role": "system", "content": "系统提示词"},
    {"role": "user", "content": "用户输入"},
    {"role": "assistant", "content": "助手回复"},
]
```

### 工具调用格式

```python
tools: List[Dict] = [{
    "type": "function",
    "function": {
        "name": "function_name",
        "description": "函数描述",
        "parameters": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    }
}]
```

### 结构化输出

支持 JSON Schema 格式的结构化输出：
- **OpenAI Structured**: 使用 OpenAI 的结构化输出 API
- **Azure OpenAI Structured**: Azure 版本的结构化输出
- **工具调用模拟**: 其他提供商通过工具调用实现结构化输出

## 测试与质量

### 配置验证

```python
def _validate_config(self):
    # 验证必要属性
    if not hasattr(self.config, "model"):
        raise ValueError("Configuration must have a 'model' attribute")
    
    # API 密钥检查 (由各提供商具体实现)
    if not hasattr(self.config, "api_key"):
        # 检查环境变量等
        pass
```

### 错误处理

- **连接失败**: 网络连接和 API 端点错误处理
- **认证错误**: API 密钥验证和权限检查
- **参数错误**: 不支持的参数自动过滤
- **推理模型**: 特殊模型的参数兼容性处理

## 常见问题 (FAQ)

**Q: 如何选择合适的 LLM 提供商？**
A:
- **开发测试**: Ollama, LM Studio (本地免费)
- **生产高质量**: OpenAI GPT-4, Anthropic Claude
- **成本优化**: OpenAI GPT-3.5, Google Gemini Flash
- **推理任务**: OpenAI o1 系列
- **中文优化**: Deepseek, GLM (智谱清言)
- **企业部署**: Azure OpenAI, AWS Bedrock

**Q: 推理模型 (o1, GPT-5) 有什么特殊之处？**
A: 推理模型专注于复杂逻辑推理，但不支持 `temperature`、`top_p` 等参数，系统会自动过滤这些参数。

**Q: 如何实现自定义 LLM 提供商？**
A: 继承 `LLMBase` 类，实现 `generate_response` 方法，并在配置验证中添加你的提供商名称。

**Q: 结构化输出和普通输出有什么区别？**
A: 结构化输出确保返回符合 JSON Schema 的格式化数据，普通输出返回自然语言文本。

## 相关文件清单

### 核心文件
- `base.py` - LLM 抽象基类 (132 行)
- `configs.py` - 配置管理和提供商验证 (35 行)

### 主流商业提供商
- `openai.py` - OpenAI GPT 系列支持
- `openai_structured.py` - OpenAI 结构化输出支持
- `anthropic.py` - Anthropic Claude 系列支持
- `azure_openai.py` - Azure OpenAI 服务支持
- `azure_openai_structured.py` - Azure 结构化输出支持
- `gemini.py` - Google Gemini 系列支持
- `deepseek.py` - Deepseek 模型支持
- `glm.py` - GLM (智谱清言) 模型支持
- `xai.py` - XAI Grok 系列支持

### 专业化和开源提供商
- `groq.py` - Groq 高性能推理支持
- `together.py` - Together 开源模型托管支持
- `litellm.py` - LiteLLM 统一接口支持
- `ollama.py` - Ollama 本地运行支持
- `lmstudio.py` - LM Studio 本地管理支持
- `vllm.py` - vLLM 高性能推理服务器支持
- `sarvam.py` - Sarvam 印度语言模型支持

### 云平台集成
- `aws_bedrock.py` - AWS Bedrock 服务支持
- `langchain.py` - LangChain LLM 集成支持

### 配置文件
- `../configs/llms/*.py` - 各提供商的 Pydantic 配置类

---

**模块特色**: 业界最全面的 LLM 提供商支持，智能推理模型适配，统一抽象接口设计