#!/usr/bin/env python3
"""
Mem0 本地 API 服务器
提供 REST API 接口供前端调用
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import json
import uuid
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig  
from mem0.vector_stores.configs import VectorStoreConfig

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化 Memory 实例
def init_memory():
    """初始化 Mem0 实例"""
    try:
        # 创建配置
        llm_config = LlmConfig(
            provider="glm",
            config={
                "model": "glm-4.5",
                "api_key": "91654c7966f149dc94f4bdcba1d90fa3.BGlbzom7iMDHyjhS",
                "glm_base_url": "https://open.bigmodel.cn/api/paas/v4",
                "temperature": 0.7,
                "enable_thinking": True
            }
        )
        
        vector_store_config = VectorStoreConfig(
            provider="chroma",
            config={
                "collection_name": "mem0_api_memories",
                "host": "localhost",
                "port": 8000
            }
        )
        
        embedder_config = EmbedderConfig(
            provider="ollama",
            config={"model": "bge-m3"}
        )
        
        memory_config = MemoryConfig(
            llm=llm_config,
            vector_store=vector_store_config,
            embedder=embedder_config,
            version="v1.1"
        )
        
        return Memory(memory_config)
    except Exception as e:
        print(f"❌ Memory 初始化失败: {e}")
        return None

memory = init_memory()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "memory_available": memory is not None,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/memories', methods=['POST'])
def add_memory():
    """添加记忆"""
    try:
        data = request.json
        content = data.get('content', '')
        user_id = data.get('user_id', 'default')
        metadata = data.get('metadata', {})
        
        if not memory:
            return jsonify({"error": "Memory service unavailable"}), 503
        
        result = memory.add(content, user_id=user_id, metadata=metadata)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memories/search', methods=['POST'])
def search_memories():
    """搜索记忆"""
    try:
        data = request.json
        query = data.get('query', '')
        user_id = data.get('user_id', 'default')
        limit = data.get('limit', 10)
        
        if not memory:
            return jsonify({"error": "Memory service unavailable"}), 503
        
        results = memory.search(query, user_id=user_id, limit=limit)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memories', methods=['GET'])
def get_all_memories():
    """获取所有记忆"""
    try:
        user_id = request.args.get('user_id', 'default')
        
        if not memory:
            return jsonify({"error": "Memory service unavailable"}), 503
        
        results = memory.get_all(user_id=user_id)
        return jsonify({"success": True, "memories": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memories/<memory_id>', methods=['PUT'])
def update_memory(memory_id):
    """更新记忆"""
    try:
        data = request.json
        content = data.get('content', '')
        
        if not memory:
            return jsonify({"error": "Memory service unavailable"}), 503
        
        result = memory.update(memory_id, content)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memories/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """删除记忆"""
    try:
        if not memory:
            return jsonify({"error": "Memory service unavailable"}), 503
        
        memory.delete(memory_id)
        return jsonify({"success": True, "message": "Memory deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """基于记忆的对话"""
    try:
        data = request.json
        message = data.get('message', '')
        user_id = data.get('user_id', 'default')
        
        if not memory:
            return jsonify({"error": "Memory service unavailable"}), 503
        
        # 搜索相关记忆
        memories = memory.search(message, user_id=user_id, limit=5)
        
        # 这里可以集成 GLM 进行对话生成
        response = {
            "message": f"基于您的记忆，我了解到：{json.dumps(memories, ensure_ascii=False)}",
            "memories_used": len(memories.get('results', [])) if memories else 0
        }
        
        return jsonify({"success": True, "response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 启动 Mem0 API 服务器...")
    print("📍 访问地址: http://localhost:8080")
    print("✅ Memory 状态:", "可用" if memory else "不可用")
    app.run(host='0.0.0.0', port=8080, debug=True)