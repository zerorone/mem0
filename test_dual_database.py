#!/usr/bin/env python3
"""
测试 Mem0 双数据库架构功能
验证向量数据库（ChromaDB）和图数据库（Neo4j）的协同工作
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.llms.configs import LlmConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig
from mem0.graphs.configs import GraphStoreConfig
import json

def init_memory_with_dual_db():
    """初始化带有双数据库的 Mem0"""
    print("🔧 初始化 Mem0 双数据库架构...")
    
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
            "collection_name": "mem0_dual_db_test",
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
    
    # 图数据库配置（Memgraph）
    graph_store_config = GraphStoreConfig(
        provider="memgraph",
        config={
            "url": "bolt://localhost:7687",
            "username": "memgraph",
            "password": "memgraph"
        }
    )
    
    # 创建记忆配置（启用双数据库）
    memory_config = MemoryConfig(
        llm=llm_config,
        vector_store=vector_store_config,
        embedder=embedder_config,
        graph_store=graph_store_config,  # 启用 Memgraph 图数据库
        version="v1.1"
    )
    
    return Memory(memory_config)

def test_dual_database():
    """测试双数据库功能"""
    memory = init_memory_with_dual_db()
    user_id = "test_user_dual_db"
    
    print("\n📊 测试双数据库架构")
    print("=" * 60)
    
    # 测试数据
    test_memories = [
        "我是张三，在北京工作，是一名软件工程师",
        "我喜欢在星巴克喝拿铁咖啡",
        "昨天和李四讨论了新项目的架构设计",
        "新项目使用微服务架构，计划用 Kubernetes 部署",
        "李四负责前端开发，王五负责数据库设计"
    ]
    
    # 1. 添加记忆
    print("\n1️⃣ 添加记忆到双数据库...")
    for mem_content in test_memories:
        result = memory.add(mem_content, user_id=user_id)
        print(f"   ✅ 添加: {mem_content[:30]}...")
        
        # 检查是否包含图数据库关系
        if result and isinstance(result, dict):
            if 'relations' in result and result['relations']:
                print(f"      🕸️ 发现关系: {len(result.get('relations', []))} 个")
    
    # 2. 向量数据库搜索
    print("\n2️⃣ 测试向量数据库（语义搜索）...")
    queries = [
        "咖啡偏好",
        "项目架构",
        "团队成员"
    ]
    
    for query in queries:
        results = memory.search(query, user_id=user_id, limit=3)
        print(f"\n   🔍 搜索: '{query}'")
        
        if isinstance(results, dict):
            # 向量数据库结果
            vector_results = results.get('results', [])
            if vector_results:
                print(f"   📝 向量搜索结果 ({len(vector_results)} 条):")
                for i, res in enumerate(vector_results[:2], 1):
                    print(f"      {i}. {res.get('memory', '')[:50]}...")
            
            # 图数据库结果
            graph_results = results.get('relations', [])
            if graph_results:
                print(f"   🕸️ 图关系结果 ({len(graph_results)} 个):")
                for rel in graph_results[:2]:
                    print(f"      - {rel}")
        else:
            # 纯向量数据库模式
            if results:
                print(f"   📝 找到 {len(results)} 条相关记忆")
                for i, res in enumerate(results[:2], 1):
                    print(f"      {i}. {res.get('memory', '')[:50]}...")
    
    # 3. 测试图数据库连接
    print("\n3️⃣ 验证图数据库连接...")
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "mem0password")
        )
        
        with driver.session() as session:
            # 查询所有节点
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            print(f"   ✅ Neo4j 连接成功，节点总数: {node_count}")
            
            # 查询关系
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()["count"]
            print(f"   ✅ 关系总数: {rel_count}")
            
            # 查询特定实体
            result = session.run("""
                MATCH (n) 
                WHERE n.name IN ['张三', '李四', '王五', '北京', '星巴克']
                RETURN n.name as name, labels(n) as labels
                LIMIT 5
            """)
            
            entities = list(result)
            if entities:
                print(f"   🏷️ 识别的实体:")
                for entity in entities:
                    print(f"      - {entity['name']} ({', '.join(entity['labels'])})")
        
        driver.close()
        
    except Exception as e:
        print(f"   ⚠️ 图数据库查询失败: {e}")
    
    # 4. 获取所有记忆
    print("\n4️⃣ 获取所有记忆...")
    all_memories = memory.get_all(user_id=user_id)
    if all_memories:
        if isinstance(all_memories, dict) and 'results' in all_memories:
            memories_list = all_memories['results']
            print(f"   📚 共有 {len(memories_list)} 条记忆")
            for i, mem in enumerate(memories_list[:3], 1):
                print(f"      {i}. {mem.get('memory', '')[:50]}...")
        else:
            print(f"   📚 共有记忆数据")
            print(f"      {all_memories}")
    
    print("\n" + "=" * 60)
    print("✅ 双数据库测试完成！")
    print("\n💡 总结:")
    print("   • 向量数据库 (ChromaDB): 用于语义搜索和相似度匹配")
    print("   • 图数据库 (Neo4j): 用于实体关系建模和知识图谱")
    print("   • 两者协同工作，提供更智能的记忆管理")

if __name__ == "__main__":
    test_dual_database()