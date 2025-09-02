from typing import Optional

from mem0.configs.llms.base import BaseLlmConfig


class GLMConfig(BaseLlmConfig):
    """
    智谱 GLM 模型配置类
    支持 GLM-4.5 系列模型的配置和深度思考功能
    """

    def __init__(
        self,
        # 基础参数
        model: Optional[str] = None,
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        max_tokens: int = 2000,
        top_p: float = 0.7,
        top_k: int = 1,
        enable_vision: bool = False,
        vision_details: Optional[str] = "auto",
        http_client_proxies: Optional[dict] = None,
        # GLM 特有参数
        glm_base_url: Optional[str] = None,
        enable_thinking: bool = False,  # 深度思考模式
        enable_memory_management: bool = False,  # 记忆管理
        max_context_tokens: int = 8192,  # 最大上下文 token
        timeout: float = 60.0,  # 超时时间
    ):
        """
        初始化 GLM 配置

        Args:
            model: GLM 模型名称，默认使用 GLM-4.5
            temperature: 温度参数，控制创造性，默认 0.7
            api_key: GLM API 密钥，默认从环境变量获取
            max_tokens: 最大生成 token 数，默认 2000
            top_p: 核采样参数，默认 0.7
            top_k: Top-k 采样参数，默认 1
            enable_vision: 是否启用视觉能力，默认 False
            vision_details: 视觉处理细节级别，默认 "auto"
            http_client_proxies: HTTP 代理设置，默认 None
            glm_base_url: GLM API 基础 URL，默认使用官方地址
            enable_thinking: 是否启用深度思考模式，默认 False
            enable_memory_management: 是否启用记忆管理，默认 False
            max_context_tokens: 最大上下文 token 数，默认 8192
            timeout: 请求超时时间（秒），默认 60.0
        """
        # 初始化基础参数
        super().__init__(
            model=model,
            temperature=temperature,
            api_key=api_key,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            enable_vision=enable_vision,
            vision_details=vision_details,
            http_client_proxies=http_client_proxies,
        )

        # GLM 特有参数
        self.glm_base_url = glm_base_url
        self.enable_thinking = enable_thinking
        self.enable_memory_management = enable_memory_management
        self.max_context_tokens = max_context_tokens
        self.timeout = timeout