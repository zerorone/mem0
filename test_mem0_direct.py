#!/usr/bin/env python3
"""
直接测试 Mem0 核心功能
"""
import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mem0 import Memory

def test_mem0_basic():
    """测试 Mem0 基本功能"""
    print("=" * 50)
    print("Mem0 核心功能测试")
    print("=" * 50)
    
    try:
        # 使用 GLM 配置初始化
        config = {
            "llm": {
                "provider": "glm",
                "config": {
                    "model": "glm-4.5",
                    "api_key": "91654c7966f149dc94f4bdcba1d90fa3.BGlbzom7iMDHyjhS",
                    "glm_base_url": "https://open.bigmodel.cn/api/paas/v4",
                    "temperature": 0.7,
                    "enable_thinking": True
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "bge-m3"
                }
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "test_memories_glm",
                    "host": "localhost",
                    "port": 8000
                }
            }
        }
        
        print("\n1. 初始化 Memory 实例 (使用 GLM)...")
        memory = Memory.from_config(config_dict=config)
        print("✅ Memory 实例创建成功 (GLM + ChromaDB + Ollama)")
        
    except Exception as e:
        print(f"❌ 使用 GLM 配置失败: {e}")
        print("\n尝试备用配置...")
        
        try:
            # 尝试只使用向量数据库
            local_config = {
                "llm": {
                    "provider": "glm",
                    "config": {
                        "model": "glm-4.5",
                        "api_key": "91654c7966f149dc94f4bdcba1d90fa3.BGlbzom7iMDHyjhS"
                    }
                },
                "vector_store": {
                    "provider": "chroma",
                    "config": {
                        "collection_name": "test_memories_simple",
                        "host": "localhost",
                        "port": 8000
                    }
                }
            }
            
            memory = Memory.from_config(config_dict=local_config)
            print("✅ 使用简化配置创建 Memory 实例成功")
            
        except Exception as e2:
            print(f"❌ 简化配置也失败: {e2}")
            return

    # 测试基本操作
    print("\n2. 测试添加记忆...")
    try:
        result = memory.add(
            "用户喜欢喝咖啡，特别是拿铁",
            user_id="test_user",
            metadata={"category": "preference"}
        )
        print(f"✅ 添加记忆成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 添加记忆失败: {e}")
    
    print("\n3. 测试搜索记忆...")
    try:
        results = memory.search("咖啡", user_id="test_user")
        print(f"✅ 搜索记忆成功: {json.dumps(results, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ 搜索记忆失败: {e}")
    
    print("\n4. 测试获取所有记忆...")
    try:
        all_memories = memory.get_all(user_id="test_user")
        print(f"✅ 获取所有记忆成功: 共 {len(all_memories) if all_memories else 0} 条")
        if all_memories:
            print(json.dumps(all_memories, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ 获取所有记忆失败: {e}")
    
    # 测试更新记忆
    print("\n5. 测试更新记忆...")
    try:
        if all_memories and len(all_memories.get('results', [])) > 0:
            memory_id = all_memories['results'][0]['id']
            update_result = memory.update(
                memory_id,
                "用户喜欢喝咖啡，特别是拿铁和卡布奇诺",
                user_id="test_user"
            )
            print(f"✅ 更新记忆成功: {json.dumps(update_result, ensure_ascii=False, indent=2)}")
            
            # 再次获取记忆验证更新
            updated_memories = memory.get_all(user_id="test_user")
            print(f"更新后的记忆: {json.dumps(updated_memories, ensure_ascii=False, indent=2)}")
        else:
            print("⚠️ 没有记忆可供更新")
    except Exception as e:
        print(f"❌ 更新记忆失败: {e}")
    
    # 测试添加更多记忆
    print("\n6. 测试添加多条记忆...")
    try:
        memories_to_add = [
            "用户是一名软件工程师",
            "用户擅长 Python 和 JavaScript 编程",
            "用户对 AI 技术很感兴趣"
        ]
        
        for mem_content in memories_to_add:
            result = memory.add(mem_content, user_id="test_user")
            print(f"✅ 添加记忆: {mem_content[:20]}...")
        
        # 搜索相关记忆
        search_result = memory.search("编程", user_id="test_user", limit=5)
        print(f"搜索 '编程' 相关记忆: 找到 {len(search_result.get('results', []))} 条")
        
    except Exception as e:
        print(f"❌ 添加多条记忆失败: {e}")
    
    # 测试删除记忆
    print("\n7. 测试删除记忆...")
    try:
        all_memories = memory.get_all(user_id="test_user")
        if all_memories and len(all_memories.get('results', [])) > 0:
            # 删除第一条记忆
            memory_id = all_memories['results'][0]['id']
            memory.delete(memory_id, user_id="test_user")
            print(f"✅ 删除记忆成功: ID={memory_id[:8]}...")
            
            # 验证删除
            remaining = memory.get_all(user_id="test_user")
            print(f"剩余记忆数量: {len(remaining.get('results', []))} 条")
        else:
            print("⚠️ 没有记忆可供删除")
    except Exception as e:
        print(f"❌ 删除记忆失败: {e}")
    
    # 测试批量删除
    print("\n8. 测试批量删除所有记忆...")
    try:
        memory.delete_all(user_id="test_user")
        print("✅ 删除所有记忆成功")
        
        # 验证删除
        final_memories = memory.get_all(user_id="test_user")
        print(f"最终记忆数量: {len(final_memories.get('results', []))} 条")
    except Exception as e:
        print(f"❌ 批量删除失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    test_mem0_basic()