#!/usr/bin/env python3
"""
测试 MCP 工具功能
"""
import os
import sys
import json
import asyncio
from pathlib import Path

# 设置环境
os.environ['PYTHONPATH'] = '/Users/xiao/Documents/BaiduNetSyncDownload/ToolCode/mem0'
os.environ['GLM_API_KEY'] = '91654c7966f149dc94f4bdcba1d90fa3.BGlbzom7iMDHyjhS'
os.environ['GLM_BASE_URL'] = 'https://open.bigmodel.cn/api/paas/v4'
sys.path.insert(0, '/Users/xiao/Documents/BaiduNetSyncDownload/ToolCode/mem0')

# 导入 MCP 服务器模块
from mcp_server.server import mcp, create_memory_instance, create_glm_llm

async def test_mcp_tools():
    """测试 MCP 工具功能"""
    print("=" * 60)
    print("🧪 MCP 工具功能测试")
    print("=" * 60)
    
    # 1. 测试健康检查
    print("\n1️⃣ 测试 health_check 工具...")
    try:
        from mcp_server.server import health_check
        result = await health_check()
        print(f"✅ 健康检查结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 2. 测试添加记忆
    print("\n2️⃣ 测试 add_memory 工具...")
    try:
        from mcp_server.server import add_memory
        test_memory = "用户喜欢使用 Python 和 GLM 模型进行开发"
        result = await add_memory(
            content=test_memory,
            user_id="test_user",
            metadata={"category": "preference", "timestamp": "2025-09-02"}
        )
        print(f"✅ 添加记忆成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 添加记忆失败: {e}")
    
    # 3. 测试搜索记忆
    print("\n3️⃣ 测试 search_memories 工具...")
    try:
        from mcp_server.server import search_memories
        result = await search_memories(
            query="Python 开发",
            user_id="test_user",
            limit=5
        )
        print(f"✅ 搜索记忆结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 搜索记忆失败: {e}")
    
    # 4. 测试获取所有记忆
    print("\n4️⃣ 测试 get_all_memories 工具...")
    try:
        from mcp_server.server import get_all_memories
        result = await get_all_memories(user_id="test_user")
        print(f"✅ 所有记忆: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 获取记忆失败: {e}")
    
    # 5. 测试基于记忆的对话
    print("\n5️⃣ 测试 chat_with_memory 工具...")
    try:
        from mcp_server.server import chat_with_memory
        result = await chat_with_memory(
            message="我之前用什么语言开发？",
            user_id="test_user",
            include_memories=True
        )
        print(f"✅ 对话结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 对话失败: {e}")
    
    # 6. 测试统计信息
    print("\n6️⃣ 测试 memory_stats 工具...")
    try:
        from mcp_server.server import memory_stats
        result = await memory_stats(user_id="test_user")
        print(f"✅ 统计信息: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 统计失败: {e}")
    
    print("\n" + "=" * 60)
    print("✅ MCP 工具测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    # 运行异步测试
    asyncio.run(test_mcp_tools())