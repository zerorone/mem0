#!/usr/bin/env python3
"""
测试 Mem0 MCP 服务器功能
直接调用服务器中定义的函数
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入服务器模块
from mcp_server.server import (
    add_memory,
    search_memories,
    get_all_memories,
    update_memory,
    delete_memory,
    memory_stats,
    health_check,
    chat_with_memory
)

async def test_mcp_functions():
    """测试所有 MCP 函数"""
    print("=" * 60)
    print("Mem0 MCP 服务器功能测试")
    print("=" * 60)
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    health = await health_check()
    print(f"健康状态: {health}")
    
    # 2. 记忆统计
    print("\n2. 获取记忆统计...")
    stats = await memory_stats(user_id="test_user")
    print(f"统计信息: {stats}")
    
    # 3. 添加记忆
    print("\n3. 添加记忆...")
    result = await add_memory(
        content="用户喜欢使用 GLM 模型进行开发",
        user_id="test_user",
        metadata={"category": "preference"}
    )
    print(f"添加结果: {result}")
    
    # 4. 搜索记忆
    print("\n4. 搜索记忆...")
    search_result = await search_memories(
        query="GLM",
        user_id="test_user",
        limit=5
    )
    print(f"搜索结果: {search_result}")
    
    # 5. 获取所有记忆
    print("\n5. 获取所有记忆...")
    all_memories = await get_all_memories(user_id="test_user")
    print(f"所有记忆: {all_memories}")
    
    # 6. 基于记忆的对话
    print("\n6. 测试智能对话...")
    chat_result = await chat_with_memory(
        message="我之前喜欢什么模型？",
        user_id="test_user",
        include_memories=True
    )
    print(f"对话结果: {chat_result}")
    
    # 7. 删除记忆（如果有）
    print("\n7. 清理测试记忆...")
    memories = json.loads(all_memories)
    if memories.get("success") and memories.get("memories"):
        for memory in memories["memories"]:
            delete_result = await delete_memory(
                memory_id=memory["id"],
                user_id="test_user"
            )
            print(f"删除记忆 {memory['id'][:8]}...")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    # 设置环境变量
    os.environ["PYTHONPATH"] = str(Path(__file__).parent)
    
    # 运行测试
    asyncio.run(test_mcp_functions())