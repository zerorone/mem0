import os
from unittest.mock import Mock, patch

import pytest
import httpx

from mem0.configs.llms.base import BaseLlmConfig
from mem0.configs.llms.glm import GLMConfig
from mem0.llms.glm import GLMLLM


@pytest.fixture
def mock_glm_client():
    with patch("mem0.llms.glm.httpx.Client") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        yield mock_client


def test_glm_llm_base_url():
    """测试 GLM LLM base URL 配置"""
    # case1: default config with glm official base url
    config = BaseLlmConfig(model="glm-4.5", temperature=0.7, max_tokens=100, top_p=1.0, api_key="test_api_key")
    llm = GLMLLM(config)
    assert llm.base_url == "https://open.bigmodel.cn/api/paas/v4"

    # case2: with env variable GLM_API_BASE
    provider_base_url = "https://api.provider.com/v1"
    os.environ["GLM_API_BASE"] = provider_base_url
    config = GLMConfig(model="glm-4.5", temperature=0.7, max_tokens=100, top_p=1.0, api_key="test_api_key")
    llm = GLMLLM(config)
    assert llm.base_url == provider_base_url

    # case3: with config.glm_base_url
    config_base_url = "https://api.config.com/v1"
    config = GLMConfig(
        model="glm-4.5",
        temperature=0.7,
        max_tokens=100,
        top_p=1.0,
        api_key="test_api_key",
        glm_base_url=config_base_url,
    )
    llm = GLMLLM(config)
    assert llm.base_url == config_base_url

    # Clean up environment variable
    if "GLM_API_BASE" in os.environ:
        del os.environ["GLM_API_BASE"]


def test_glm_llm_default_model():
    """测试默认模型设置"""
    config = GLMConfig(api_key="test_key")
    llm = GLMLLM(config)
    assert llm.config.model == "glm-4.5"


def test_glm_llm_config_conversion():
    """测试配置类转换"""
    # Test dict config
    config_dict = {
        "model": "glm-4.5",
        "api_key": "test_key",
        "temperature": 0.8
    }
    llm = GLMLLM(config_dict)
    assert llm.config.model == "glm-4.5"
    assert llm.config.temperature == 0.8

    # Test BaseLlmConfig to GLMConfig conversion
    base_config = BaseLlmConfig(
        model="glm-4.5",
        api_key="test_key",
        temperature=0.8
    )
    llm = GLMLLM(base_config)
    assert isinstance(llm.config, GLMConfig)


def test_reasoning_model_detection():
    """测试推理模型检测"""
    config = GLMConfig(api_key="test_key")
    llm = GLMLLM(config)
    
    # Only specific GLM models need parameter filtering
    assert llm._is_reasoning_model("glm-4.5-pro") == True
    assert llm._is_reasoning_model("glm-4-plus") == True
    
    # Regular GLM models support thinking but keep normal parameters
    assert llm._is_reasoning_model("glm-4.5") == False
    assert llm._is_reasoning_model("glm-4.5-flash") == False
    assert llm._is_reasoning_model("glm-4") == False


def test_generate_response_without_tools(mock_glm_client):
    """测试不使用工具的响应生成"""
    config = BaseLlmConfig(model="glm-4.5", temperature=0.7, max_tokens=100, top_p=1.0, api_key="test_key")
    llm = GLMLLM(config)
    messages = [
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "你好，你怎么样？"},
    ]

    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "我很好，谢谢你的关心！"
            }
        }]
    }
    mock_response.raise_for_status = Mock()
    mock_glm_client.post.return_value = mock_response

    response = llm.generate_response(messages)

    # Verify the API call
    mock_glm_client.post.assert_called_once()
    call_args = mock_glm_client.post.call_args
    assert call_args[0][0] == "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    
    # Verify request data
    request_data = call_args[1]["json"]
    assert request_data["model"] == "glm-4.5"
    assert request_data["messages"] == messages
    assert request_data["temperature"] == 0.7

    assert response == "我很好，谢谢你的关心！"


def test_generate_response_with_tools(mock_glm_client):
    """测试使用工具的响应生成"""
    config = BaseLlmConfig(model="glm-4.5", temperature=0.7, max_tokens=100, top_p=1.0, api_key="test_key")
    llm = GLMLLM(config)
    messages = [
        {"role": "system", "content": "你是一个有用的助手。"},
        {"role": "user", "content": "添加一个新记忆：今天是晴天。"},
    ]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_memory",
                "description": "添加记忆",
                "parameters": {
                    "type": "object",
                    "properties": {"data": {"type": "string", "description": "要添加到记忆的数据"}},
                    "required": ["data"],
                },
            },
        }
    ]

    # Mock response with tool calls
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "我已经为你添加了记忆。",
                "tool_calls": [{
                    "function": {
                        "name": "add_memory",
                        "arguments": '{"data": "今天是晴天。"}'
                    }
                }]
            }
        }]
    }
    mock_response.raise_for_status = Mock()
    mock_glm_client.post.return_value = mock_response

    response = llm.generate_response(messages, tools=tools)

    # Verify the API call
    mock_glm_client.post.assert_called_once()
    call_args = mock_glm_client.post.call_args
    request_data = call_args[1]["json"]
    
    assert request_data["model"] == "glm-4.5"
    assert request_data["messages"] == messages
    assert request_data["tools"] == tools
    assert request_data["tool_choice"] == "auto"

    # Verify response structure
    assert response["content"] == "我已经为你添加了记忆。"
    assert len(response["tool_calls"]) == 1
    assert response["tool_calls"][0]["name"] == "add_memory"
    assert response["tool_calls"][0]["arguments"] == {"data": "今天是晴天。"}


def test_generate_response_with_thinking(mock_glm_client):
    """测试深度思考模式"""
    config = GLMConfig(
        model="glm-4.5", 
        temperature=0.7, 
        max_tokens=100, 
        top_p=1.0, 
        api_key="test_key",
        enable_thinking=True
    )
    llm = GLMLLM(config)
    messages = [
        {"role": "user", "content": "解决这个数学问题：2+2等于多少？"},
    ]

    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": "2+2等于4。",
                "reasoning_content": "让我计算一下：2 + 2 = 4"
            }
        }]
    }
    mock_response.raise_for_status = Mock()
    mock_glm_client.post.return_value = mock_response

    response = llm.generate_response(messages)

    # Verify thinking parameter is included
    call_args = mock_glm_client.post.call_args
    request_data = call_args[1]["json"]
    assert "thinking" in request_data
    assert request_data["thinking"] == {"type": "enabled"}

    assert response == "2+2等于4。"


def test_http_error_handling(mock_glm_client):
    """测试HTTP错误处理"""
    config = GLMConfig(api_key="test_key")
    llm = GLMLLM(config)
    messages = [{"role": "user", "content": "test"}]

    # Mock HTTP error
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    error = httpx.HTTPStatusError("HTTP error", request=Mock(), response=mock_response)
    mock_glm_client.post.side_effect = error

    with pytest.raises(RuntimeError) as exc_info:
        llm.generate_response(messages)
    
    assert "GLM API 错误 400" in str(exc_info.value)
    assert "Bad Request" in str(exc_info.value)


def test_timeout_error_handling(mock_glm_client):
    """测试超时错误处理"""
    config = GLMConfig(api_key="test_key", timeout=30.0)
    llm = GLMLLM(config)
    messages = [{"role": "user", "content": "test"}]

    # Mock timeout error
    mock_glm_client.post.side_effect = httpx.TimeoutException("Request timed out")

    with pytest.raises(RuntimeError) as exc_info:
        llm.generate_response(messages)
    
    assert "GLM API 请求超时" in str(exc_info.value)
    assert "30" in str(exc_info.value)  # Check timeout value