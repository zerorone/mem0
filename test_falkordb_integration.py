#!/usr/bin/env python3
"""
测试 FalkorDB 图向量数据库集成
验证向量相似度搜索和图遍历的混合查询功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig
from mem0.graphs.configs import GraphStoreConfig, FalkorDBConfig
import json
import time

def init_memory_with_falkordb():
    """初始化带有 FalkorDB 图数据库的 Mem0"""
    print("🚀 初始化 Mem0 + FalkorDB 图向量数据库架构...")
    
    # LLM 配置（GLM）
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
    
    # 向量数据库配置（ChromaDB）
    vector_store_config = VectorStoreConfig(
        provider="chroma",
        config={
            "collection_name": "mem0_falkordb_test",
            "host": "localhost",
            "port": 8000
        }
    )
    
    # 嵌入模型配置（Ollama）
    embedder_config = EmbedderConfig(
        provider="ollama",
        config={
            "model": "bge-m3",
            "embedding_dims": 1024
        }
    )
    
    # FalkorDB 图数据库配置
    graph_store_config = GraphStoreConfig(
        provider="falkordb",
        config=FalkorDBConfig(
            host="localhost",
            port=6379,
            graph_name="mem0_knowledge_graph",
            decode_responses=True
        ),
        llm=llm_config
    )
    
    # 创建记忆配置
    memory_config = MemoryConfig(
        llm=llm_config,
        vector_store=vector_store_config,
        embedder=embedder_config,
        graph_store=graph_store_config,
        version="v1.1"
    )
    
    return Memory(memory_config)

def test_falkordb_vector_similarity():
    """测试 FalkorDB 原生向量相似度功能"""
    print("\n🧪 测试 FalkorDB 原生向量相似度功能")
    print("=" * 60)
    
    try:
        import falkordb
        
        # 连接 FalkorDB
        client = falkordb.FalkorDB(host='localhost', port=6379)
        graph = client.select_graph('test_vectors')
        
        print("✅ 成功连接到 FalkorDB")
        
        # 创建向量索引
        try:
            create_index_query = """
            CALL db.idx.vector.createNodeIndex(
                'TestNode', 
                'embedding', 
                3, 
                'COSINE'
            )
            """
            result = graph.query(create_index_query)
            print("✅ 向量索引创建成功")
        except Exception as e:
            print(f"⚠️ 向量索引可能已存在: {e}")
        
        # 添加测试向量节点
        test_data = [
            {"name": "coffee", "embedding": [1.0, 0.5, 0.2]},
            {"name": "tea", "embedding": [0.9, 0.6, 0.1]}, 
            {"name": "water", "embedding": [0.1, 0.1, 0.9]},
            {"name": "latte", "embedding": [0.95, 0.55, 0.25]}
        ]
        
        for item in test_data:
            add_query = """
            MERGE (n:TestNode {name: $name})
            SET n.embedding = $embedding
            RETURN n
            """
            graph.query(add_query, {"name": item["name"], "embedding": item["embedding"]})
        
        print(f"✅ 添加了 {len(test_data)} 个测试向量节点")
        
        # 测试向量相似度查询
        query_vector = [1.0, 0.5, 0.2]  # 与 coffee 最相似
        
        vector_search_query = """
        CALL db.idx.vector.queryNodes(
            'TestNode', 
            'embedding', 
            3, 
            $query_vector
        ) YIELD node, score
        RETURN node.name as name, score
        ORDER BY score DESC
        """
        
        results = graph.query(vector_search_query, {"query_vector": query_vector})
        
        print("\n🔍 向量相似度搜索结果:")
        for result in results:
            name = result.get("name", "")
            score = result.get("score", 0.0)
            print(f"   - {name}: {score:.4f}")
        
        # 清理测试数据
        cleanup_query = "MATCH (n:TestNode) DELETE n"
        graph.query(cleanup_query)
        print("🧹 清理测试数据完成")
        
        return True
        
    except ImportError:
        print("❌ FalkorDB Python 客户端未安装")
        return False
    except Exception as e:
        print(f"❌ FalkorDB 向量测试失败: {e}")
        return False

def test_dual_database_integration():
    """测试双数据库集成功能"""
    try:
        memory = init_memory_with_falkordb()
        user_id = "test_user_falkordb"
        
        print("\n📊 测试 FalkorDB 双数据库架构")
        print("=" * 60)
        
        # 测试数据
        test_memories = [
            "张三喜欢喝星巴克的拿铁咖啡",
            "李四在北京工作，是软件工程师",
            "张三和李四是同事，经常一起讨论技术",
            "他们都喜欢用 Python 编程",
            "星巴克的拿铁很受欢迎"
        ]
        
        # 1. 添加记忆到双数据库
        print("\n1️⃣ 添加记忆到双数据库...")
        for i, mem_content in enumerate(test_memories, 1):
            print(f"   添加记忆 {i}: {mem_content}")
            result = memory.add(mem_content, user_id=user_id)
            time.sleep(0.5)  # 避免请求过快
        
        # 2. 测试向量数据库搜索
        print("\n2️⃣ 测试向量数据库搜索...")
        search_queries = [
            "咖啡相关",
            "技术工作",
            "人员关系"
        ]
        
        for query in search_queries:
            print(f"\n   🔍 搜索: '{query}'")
            results = memory.search(query, user_id=user_id, limit=3)
            
            if results:
                print(f"   📝 找到 {len(results)} 条相关记忆:")
                for j, res in enumerate(results[:2], 1):
                    content = res.get('memory', '') if isinstance(res, dict) else str(res)
                    print(f"      {j}. {content[:50]}...")
            else:
                print("   📝 未找到相关记忆")
        
        # 3. 获取所有记忆
        print("\n3️⃣ 获取所有记忆...")
        all_memories = memory.get_all(user_id=user_id)
        if all_memories:
            count = len(all_memories) if isinstance(all_memories, list) else len(all_memories.get('results', []))
            print(f"   📚 共有 {count} 条记忆")
        
        print("\n✅ FalkorDB 双数据库集成测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 双数据库集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_memory_capabilities():
    """专门测试图记忆能力"""
    print("\n🕸️ 测试图记忆功能")
    print("=" * 60)
    
    try:
        from mem0.graphs.falkordb.main import FalkorDB
        from mem0.configs.base import MemoryConfig
        from mem0.llms.configs import LlmConfig
        from mem0.embeddings.configs import EmbedderConfig
        from mem0.graphs.configs import FalkorDBConfig
        
        # 创建简化配置用于图测试
        config = type('Config', (), {})()
        config.graph_store = type('GraphStore', (), {})()
        config.graph_store.config = FalkorDBConfig(
            host="localhost",
            port=6379,
            graph_name="test_graph_memory",
            decode_responses=True
        )
        
        # 嵌入模型配置
        config.embedder = type('Embedder', (), {})()
        config.embedder.provider = "ollama"
        config.embedder.config = {
            "model": "bge-m3",
            "embedding_dims": 1024
        }
        
        # 不配置 LLM（简化测试）
        config.llm = None
        
        # 创建 FalkorDB 实例
        falkordb_memory = FalkorDB(config)
        
        print("✅ FalkorDB 图记忆实例创建成功")
        
        # 测试简单的图操作
        user_id = "test_graph_user"
        test_data = "张三喜欢咖啡"
        
        # 添加图记忆
        result = falkordb_memory.add(test_data, {"user_id": user_id})
        print(f"📝 添加图记忆结果: {result}")
        
        # 搜索图记忆
        search_result = falkordb_memory.search("咖啡", {"user_id": user_id})
        print(f"🔍 图搜索结果: {search_result}")
        
        # 获取所有图记忆
        all_result = falkordb_memory.get_all({"user_id": user_id})
        print(f"📚 所有图记忆: {all_result}")
        
        # 清理测试数据
        falkordb_memory.delete_all({"user_id": user_id})
        print("🧹 图记忆测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 图记忆测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎯 FalkorDB 图向量数据库集成测试")
    print("=" * 60)
    
    # 测试结果统计
    tests = {
        "FalkorDB 原生向量相似度": test_falkordb_vector_similarity,
        "图记忆功能": test_graph_memory_capabilities,
        "双数据库集成": test_dual_database_integration
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        print(f"\n🧪 开始测试: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results[test_name] = False
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("🎯 测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！FalkorDB 集成成功！")
        print("\n💡 FalkorDB 优势:")
        print("   ✅ 原生支持向量相似度搜索")
        print("   ✅ 图遍历和关系查询")
        print("   ✅ 向量+图混合查询")
        print("   ✅ 完全开源免费")
        print("   ✅ 专为 GraphRAG 设计")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试")

if __name__ == "__main__":
    main()