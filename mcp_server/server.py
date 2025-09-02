#!/usr/bin/env python3
"""
Mem0 GLM MCP Server
基于 mem0 和 GLM 的智能记忆管理 MCP 服务器
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from fastmcp import FastMCP
    from fastmcp.exceptions import FastMCPError
except ImportError:
    print("❌ FastMCP 未安装，请运行: pip install fastmcp")
    sys.exit(1)

try:
    from mem0 import Memory
    from mem0.configs.base import MemoryConfig
    from mem0.configs.llms.glm import GLMConfig
    from mem0.llms.glm import GLMLLM
    from mem0.llms.configs import LlmConfig
    from mem0.embeddings.configs import EmbedderConfig
    from mem0.vector_stores.configs import VectorStoreConfig
    from mem0.graphs.configs import GraphStoreConfig
except ImportError as e:
    print(f"❌ Mem0 模块导入失败: {e}")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mem0_mcp_server.log')
    ]
)
logger = logging.getLogger(__name__)

class Mem0GLMConfig:
    """Mem0 GLM MCP 服务器配置管理"""
    
    def __init__(self):
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """按优先级加载配置文件"""
        config_paths = [
            os.path.expanduser("~/.claude/mem0-glm-config.json"),
            "config/development.json",
            "config/.env.json"
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    logger.info(f"✅ 加载配置文件: {config_path}")
                    return config
                except json.JSONDecodeError as e:
                    logger.error(f"❌ 配置文件格式错误 {config_path}: {e}")
        
        # 如果没有找到配置文件，使用环境变量
        logger.warning("⚠️  未找到配置文件，使用环境变量")
        return self._load_from_env()
    
    def _load_from_env(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        return {
            # GLM 配置
            "glm_api_key": os.getenv("GLM_API_KEY", "91654c7966f149dc94f4bdcba1d90fa3.BGlbzom7iMDHyjhS"),
            "glm_base_url": os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            "glm_model": os.getenv("GLM_MODEL", "glm-4.5"),
            
            # Vector Store 配置
            "vector_store_provider": os.getenv("VECTOR_STORE_PROVIDER", "chroma"),
            "vector_store_config": {
                "collection_name": os.getenv("COLLECTION_NAME", "mem0_memories"),
                "path": os.getenv("CHROMA_PATH", "/tmp/chroma_mem0")
            },
            
            # 嵌入模型配置
            "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "ollama"),
            "embedding_config": {
                "model": os.getenv("EMBEDDING_MODEL", "bge-m3")
            },
            
            # 日志配置
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "enable_thinking": os.getenv("ENABLE_THINKING", "true").lower() == "true"
        }
    
    def _validate_config(self):
        """验证配置"""
        required_keys = ["glm_api_key", "vector_store_provider"]
        for key in required_keys:
            if not self.config.get(key):
                logger.error(f"❌ 缺少必需配置项: {key}")
                raise ValueError(f"Missing required config: {key}")
        
        logger.info("✅ 配置验证通过")

class Mem0GLMServer:
    """Mem0 GLM MCP 服务器主类"""
    
    def __init__(self):
        self.config_manager = Mem0GLMConfig()
        self.memory = None
        self._init_memory()
    
    def _init_memory(self):
        """初始化 Mem0 实例"""
        try:
            # 创建 LLM 配置
            llm_config = LlmConfig(
                provider="glm",
                config={
                    "model": self.config_manager.config["glm_model"],
                    "api_key": self.config_manager.config["glm_api_key"],
                    "glm_base_url": self.config_manager.config.get("glm_base_url"),
                    "temperature": 0.7,
                    "enable_thinking": self.config_manager.config.get("enable_thinking", True)
                }
            )
            
            # 创建向量存储配置
            vector_store_config = VectorStoreConfig(
                provider=self.config_manager.config["vector_store_provider"],
                config=self.config_manager.config.get("vector_store_config", {})
            )
            
            # 创建嵌入模型配置
            embedder_config = EmbedderConfig(
                provider=self.config_manager.config.get("embedding_provider", "ollama"),
                config=self.config_manager.config.get("embedding_config", {})
            )
            
            # 创建图数据库配置（可选）
            graph_store_config = None
            if self.config_manager.config.get("graph_store_provider"):
                graph_store_config = GraphStoreConfig(
                    provider=self.config_manager.config["graph_store_provider"],
                    config=self.config_manager.config.get("graph_store_config", {})
                )
            
            # 创建完整的 MemoryConfig 对象
            memory_config = MemoryConfig(
                llm=llm_config,
                vector_store=vector_store_config,
                embedder=embedder_config,
                graph_store=graph_store_config if graph_store_config else GraphStoreConfig(),
                version="v1.1"
            )
            
            # 初始化 Memory 实例
            self.memory = Memory(memory_config)
            logger.info("✅ Mem0 实例初始化成功")
            
        except Exception as e:
            logger.error(f"❌ Mem0 实例初始化失败: {e}")
            self.memory = None
            # 创建一个基础的 GLM 实例以提供基本功能
            try:
                glm_config = GLMConfig(
                    model=self.config_manager.config["glm_model"],
                    api_key=self.config_manager.config["glm_api_key"],
                    glm_base_url=self.config_manager.config.get("glm_base_url"),
                    enable_thinking=self.config_manager.config.get("enable_thinking", True)
                )
                self.glm_llm = GLMLLM(glm_config)
                logger.info("✅ 备用 GLM LLM 初始化成功")
            except Exception as glm_error:
                logger.error(f"❌ GLM LLM 初始化也失败: {glm_error}")
                self.glm_llm = None

# 创建服务器实例
server_instance = Mem0GLMServer()

# 创建 MCP 应用
mcp = FastMCP("Mem0-GLM Memory Server")

@mcp.tool()
async def add_memory(
    content: str,
    user_id: str = "default_user",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    添加记忆到 Mem0
    
    Args:
        content: 要记忆的内容
        user_id: 用户ID，默认为 default_user
        metadata: 可选的元数据
    
    Returns:
        添加结果的JSON字符串
    """
    try:
        if not server_instance.memory:
            raise FastMCPError("INTERNAL_ERROR", "Mem0 实例不可用")
        
        result = server_instance.memory.add(
            content, 
            user_id=user_id, 
            metadata=metadata or {}
        )
        
        logger.info(f"✅ 成功添加记忆 - 用户: {user_id}")
        return json.dumps({
            "success": True,
            "message": "记忆添加成功",
            "result": result
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"❌ 添加记忆失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def search_memories(
    query: str,
    user_id: str = "default_user",
    limit: int = 10
) -> str:
    """
    搜索记忆
    
    Args:
        query: 搜索查询
        user_id: 用户ID
        limit: 返回结果数量限制
    
    Returns:
        搜索结果的JSON字符串
    """
    try:
        if not server_instance.memory:
            raise FastMCPError("INTERNAL_ERROR", "Mem0 实例不可用")
        
        results = server_instance.memory.search(
            query, 
            user_id=user_id, 
            limit=limit
        )
        
        logger.info(f"✅ 搜索记忆成功 - 用户: {user_id}, 查询: {query}")
        return json.dumps({
            "success": True,
            "query": query,
            "user_id": user_id,
            "results": results
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"❌ 搜索记忆失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def get_all_memories(
    user_id: str = "default_user"
) -> str:
    """
    获取用户的所有记忆
    
    Args:
        user_id: 用户ID
    
    Returns:
        所有记忆的JSON字符串
    """
    try:
        if not server_instance.memory:
            raise FastMCPError("INTERNAL_ERROR", "Mem0 实例不可用")
        
        memories = server_instance.memory.get_all(user_id=user_id)
        
        logger.info(f"✅ 获取所有记忆成功 - 用户: {user_id}")
        return json.dumps({
            "success": True,
            "user_id": user_id,
            "count": len(memories) if memories else 0,
            "memories": memories
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"❌ 获取记忆失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def update_memory(
    memory_id: str,
    content: str,
    user_id: str = "default_user"
) -> str:
    """
    更新指定记忆
    
    Args:
        memory_id: 记忆ID
        content: 新的内容
        user_id: 用户ID
    
    Returns:
        更新结果的JSON字符串
    """
    try:
        if not server_instance.memory:
            raise FastMCPError("INTERNAL_ERROR", "Mem0 实例不可用")
        
        result = server_instance.memory.update(
            memory_id, 
            content, 
            user_id=user_id
        )
        
        logger.info(f"✅ 更新记忆成功 - ID: {memory_id}")
        return json.dumps({
            "success": True,
            "message": "记忆更新成功",
            "memory_id": memory_id,
            "result": result
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"❌ 更新记忆失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def delete_memory(
    memory_id: str,
    user_id: str = "default_user"
) -> str:
    """
    删除指定记忆
    
    Args:
        memory_id: 记忆ID
        user_id: 用户ID
    
    Returns:
        删除结果的JSON字符串
    """
    try:
        if not server_instance.memory:
            raise FastMCPError("INTERNAL_ERROR", "Mem0 实例不可用")
        
        server_instance.memory.delete(memory_id, user_id=user_id)
        
        logger.info(f"✅ 删除记忆成功 - ID: {memory_id}")
        return json.dumps({
            "success": True,
            "message": "记忆删除成功",
            "memory_id": memory_id
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"❌ 删除记忆失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def chat_with_memory(
    message: str,
    user_id: str = "default_user",
    include_memories: bool = True
) -> str:
    """
    基于记忆的智能对话
    
    Args:
        message: 用户消息
        user_id: 用户ID
        include_memories: 是否包含相关记忆作为上下文
    
    Returns:
        对话响应的JSON字符串
    """
    try:
        # 如果有 Mem0 实例，先搜索相关记忆
        context_memories = []
        if server_instance.memory and include_memories:
            try:
                memories = server_instance.memory.search(message, user_id=user_id, limit=5)
                context_memories = [m.get('memory', '') for m in memories if m.get('memory')]
            except Exception as mem_error:
                logger.warning(f"⚠️  搜索记忆时出错: {mem_error}")
        
        # 构建对话上下文
        if context_memories:
            context = f"相关记忆:\n" + "\n".join([f"- {mem}" for mem in context_memories])
            full_message = f"{context}\n\n用户问题: {message}"
        else:
            full_message = message
        
        # 使用 GLM 生成响应
        if server_instance.glm_llm:
            messages = [
                {"role": "system", "content": "你是一个智能助手，可以基于用户的历史记忆提供帮助。"},
                {"role": "user", "content": full_message}
            ]
            
            response = server_instance.glm_llm.generate_response(messages)
        else:
            response = "抱歉，GLM 服务不可用，无法生成响应。"
        
        logger.info(f"✅ 对话成功 - 用户: {user_id}")
        return json.dumps({
            "success": True,
            "message": message,
            "response": response,
            "context_memories_count": len(context_memories)
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"❌ 对话失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def memory_stats(
    user_id: str = "default_user"
) -> str:
    """
    获取记忆统计信息
    
    Args:
        user_id: 用户ID
    
    Returns:
        统计信息的JSON字符串
    """
    try:
        stats = {
            "user_id": user_id,
            "mem0_available": server_instance.memory is not None,
            "glm_available": server_instance.glm_llm is not None
        }
        
        if server_instance.memory:
            try:
                all_memories = server_instance.memory.get_all(user_id=user_id)
                stats["total_memories"] = len(all_memories) if all_memories else 0
            except Exception:
                stats["total_memories"] = "无法获取"
        
        logger.info(f"✅ 获取统计信息成功 - 用户: {user_id}")
        return json.dumps(stats, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"❌ 获取统计信息失败: {e}")
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

@mcp.tool()
async def health_check() -> str:
    """
    健康检查
    
    Returns:
        健康状态的JSON字符串
    """
    health_status = {
        "timestamp": "2025-09-02 12:36:01",
        "server_status": "running",
        "mem0_status": "available" if server_instance.memory else "unavailable",
        "glm_status": "available" if server_instance.glm_llm else "unavailable",
        "config_loaded": bool(server_instance.config_manager.config),
        "version": "1.0.0"
    }
    
    logger.info("✅ 健康检查完成")
    return json.dumps(health_status, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    logger.info("🚀 启动 Mem0-GLM MCP 服务器...")
    logger.info(f"✅ 服务器初始化完成")
    logger.info(f"✅ Mem0 状态: {'可用' if server_instance.memory else '不可用'}")
    logger.info(f"✅ GLM 状态: {'可用' if server_instance.glm_llm else '不可用'}")
    mcp.run()