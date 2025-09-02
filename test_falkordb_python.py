#!/usr/bin/env python3
"""
使用 FalkorDB Python 客户端直接测试
避免 redis-cli 命令格式问题
"""

def test_falkordb_direct():
    """直接使用 FalkorDB Python 客户端测试"""
    print("🎯 FalkorDB Python 客户端直接测试")
    print("=" * 50)
    
    try:
        import falkordb
        print("✅ 成功导入 FalkorDB")
        
        # 连接到 FalkorDB
        client = falkordb.FalkorDB(host='localhost', port=6379)
        print("✅ 连接 FalkorDB 成功")
        
        # 选择图数据库
        graph = client.select_graph('mem0_test')
        print("✅ 选择图 'mem0_test' 成功")
        
        # 测试基本的图创建
        print("\n🔧 测试基本图操作...")
        
        # 清理现有数据
        try:
            graph.query("MATCH (n) DETACH DELETE n")
            print("✅ 清理现有数据")
        except Exception as e:
            print(f"ℹ️ 清理数据: {e}")
        
        # 创建节点和关系
        result = graph.query("""
            CREATE (zhang:Person {name: '张三', age: 30}),
                   (coffee:Drink {name: '咖啡', type: 'hot'}),
                   (starbucks:Place {name: '星巴克', type: 'cafe'})
            CREATE (zhang)-[:LIKES {intensity: 'high'}]->(coffee),
                   (zhang)-[:VISITS {frequency: 'daily'}]->(starbucks)
            RETURN zhang.name, coffee.name, starbucks.name
        """)
        
        print("✅ 创建图数据成功")
        if result.result_set:
            for record in result.result_set:
                print(f"   创建了: {record[0]}, {record[1]}, {record[2]}")
        
        # 查询图数据
        print("\n🔍 测试图查询...")
        result = graph.query("""
            MATCH (p:Person)-[r]->(target)
            RETURN p.name as person, type(r) as relation, target.name as target
        """)
        
        if result.result_set:
            print("✅ 图查询成功:")
            for record in result.result_set:
                print(f"   {record[0]} -[{record[1]}]-> {record[2]}")
        else:
            print("⚠️ 未找到数据")
        
        # 测试向量索引（如果支持）
        print("\n🎯 测试向量索引...")
        try:
            # 尝试创建向量索引
            index_result = graph.query("""
                CALL db.idx.vector.createNodeIndex(
                    'Person', 
                    'embedding', 
                    128, 
                    'COSINE'
                )
            """)
            print("✅ 向量索引创建成功")
            
            # 添加带向量的节点
            import random
            random.seed(42)
            embedding = [random.random() for _ in range(128)]
            
            vector_result = graph.query("""
                CREATE (p:Person {name: '李四', embedding: $embedding})
                RETURN p.name
            """, {"embedding": embedding})
            
            print("✅ 向量节点创建成功")
            
            # 测试向量搜索
            query_embedding = embedding  # 使用相同向量进行搜索
            search_result = graph.query("""
                CALL db.idx.vector.queryNodes(
                    'Person', 
                    'embedding', 
                    3, 
                    $query_vector
                ) YIELD node, score
                RETURN node.name as name, score
                ORDER BY score DESC
            """, {"query_vector": query_embedding})
            
            if search_result.result_set:
                print("✅ 向量搜索成功:")
                for record in search_result.result_set:
                    print(f"   {record[0]}: 相似度 {record[1]:.4f}")
            
        except Exception as e:
            print(f"ℹ️ 向量功能测试: {e}")
            print("   (可能是该 FalkorDB 版本不支持向量索引)")
        
        print("\n🎉 FalkorDB 基本功能测试完成！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_redis_connection():
    """测试基本的 Redis 连接"""
    print("\n🔧 测试基本 Redis 连接...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # 测试基本操作
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')
        
        if value == 'test_value':
            print("✅ Redis 基本连接正常")
            return True
        else:
            print("❌ Redis 连接有问题")
            return False
    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始 FalkorDB 综合测试")
    print("=" * 50)
    
    # 先测试基本的 Redis 连接
    redis_ok = test_basic_redis_connection()
    
    if not redis_ok:
        print("\n❌ Redis 连接失败，停止测试")
        return
    
    # 测试 FalkorDB 功能
    falkor_ok = test_falkordb_direct()
    
    print("\n" + "=" * 50)
    print("🎯 测试结果总结")
    print("=" * 50)
    
    if redis_ok and falkor_ok:
        print("✅ Redis 连接: 正常")
        print("✅ FalkorDB 功能: 正常")
        print("\n🎉 FalkorDB 已就绪，可用于 Mem0 集成！")
    else:
        print(f"{'✅' if redis_ok else '❌'} Redis 连接: {'正常' if redis_ok else '失败'}")
        print(f"{'✅' if falkor_ok else '❌'} FalkorDB 功能: {'正常' if falkor_ok else '失败'}")
        print("\n⚠️ 需要进一步调试")

if __name__ == "__main__":
    main()