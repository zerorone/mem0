import json
import os
import httpx
from typing import Dict, List, Optional, Union

from mem0.configs.llms.base import BaseLlmConfig
from mem0.configs.llms.glm import GLMConfig
from mem0.llms.base import LLMBase
from mem0.memory.utils import extract_json


class GLMLLM(LLMBase):
    """
    智谱 GLM 大语言模型实现
    支持 GLM-4.5 系列模型，具备深度思考功能和工具调用能力
    """

    def __init__(self, config: Optional[Union[BaseLlmConfig, GLMConfig, Dict]] = None):
        """初始化 GLM LLM 实例"""
        
        # 配置转换和初始化
        if config is None:
            config = GLMConfig()
        elif isinstance(config, dict):
            config = GLMConfig(**config)
        elif isinstance(config, BaseLlmConfig) and not isinstance(config, GLMConfig):
            # 转换基础配置为 GLM 配置
            config = GLMConfig(
                model=config.model,
                temperature=config.temperature,
                api_key=config.api_key,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                top_k=config.top_k,
                enable_vision=config.enable_vision,
                vision_details=config.vision_details,
                http_client_proxies=config.http_client,
            )

        super().__init__(config)

        # 设置默认模型为 GLM-4.5
        if not self.config.model:
            self.config.model = "glm-4.5"

        # 获取 API 配置
        api_key = self.config.api_key or os.getenv("GLM_API_KEY") or os.getenv("ZHIPU_API_KEY")
        if not api_key:
            api_key = "91654c7966f149dc94f4bdcba1d90fa3.BGlbzom7iMDHyjhS"  # 默认提供的 key
            
        base_url = (
            self.config.glm_base_url 
            or os.getenv("GLM_API_BASE") 
            or "https://open.bigmodel.cn/api/paas/v4"
        )

        # 初始化 HTTP 客户端
        self.client = httpx.Client(
            timeout=httpx.Timeout(self.config.timeout),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        self.base_url = base_url.rstrip('/')

    def _parse_response(self, response, tools):
        """
        解析 GLM API 响应

        Args:
            response: GLM API 响应
            tools: 工具列表

        Returns:
            str or dict: 解析后的响应内容
        """
        if tools:
            processed_response = {
                "content": response['choices'][0]['message']['content'],
                "tool_calls": [],
            }

            # 处理工具调用
            if response['choices'][0]['message'].get('tool_calls'):
                for tool_call in response['choices'][0]['message']['tool_calls']:
                    processed_response["tool_calls"].append({
                        "name": tool_call['function']['name'],
                        "arguments": json.loads(extract_json(tool_call['function']['arguments'])),
                    })

            return processed_response
        else:
            return response['choices'][0]['message']['content']

    def _is_reasoning_model(self, model: str) -> bool:
        """
        检查是否为支持深度思考的推理模型

        Args:
            model: 模型名称

        Returns:
            bool: 是否支持深度思考
        """
        reasoning_models = {"glm-4.5", "glm-4-plus", "glm-4.5-pro"}
        return model.lower() in reasoning_models

    def _validate_config(self):
        """验证 GLM 配置"""
        super()._validate_config()
        
        # 检查模型是否支持
        supported_models = [
            "glm-4.5", "glm-4", "glm-4-plus", "glm-4.5-flash", 
            "glm-4.5-pro", "glm-4-air", "glm-3-turbo"
        ]
        
        if self.config.model and self.config.model.lower() not in [m.lower() for m in supported_models]:
            print(f"Warning: Model '{self.config.model}' may not be supported. Supported models: {supported_models}")

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs,
    ):
        """
        生成 GLM 响应

        Args:
            messages: 消息列表
            response_format: 响应格式
            tools: 可用工具列表
            tool_choice: 工具选择策略
            **kwargs: 其他参数

        Returns:
            str or dict: 生成的响应
        """
        
        # 构建请求参数
        params = self._get_supported_params(messages=messages, **kwargs)
        params.update({
            "model": self.config.model.lower(),
            "messages": messages,
        })

        # 添加工具调用
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice

        # 添加响应格式
        if response_format:
            params["response_format"] = response_format

        # 添加深度思考参数（如果模型支持）
        if (hasattr(self.config, 'enable_thinking') 
            and self.config.enable_thinking 
            and self._is_reasoning_model(self.config.model)):
            params["thinking"] = {"type": "enabled"}

        # 发送请求到 GLM API
        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                json=params
            )
            response.raise_for_status()
            result = response.json()

            return self._parse_response(result, tools)

        except httpx.HTTPStatusError as e:
            error_text = e.response.text if e.response else "Unknown error"
            raise RuntimeError(f"GLM API 错误 {e.response.status_code if e.response else 'Unknown'}: {error_text}")
        except httpx.TimeoutException:
            raise RuntimeError(f"GLM API 请求超时（{self.config.timeout}秒）")
        except Exception as e:
            raise RuntimeError(f"GLM 调用失败: {str(e)}")

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
            except:
                pass