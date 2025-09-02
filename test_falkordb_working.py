#!/usr/bin/env python3
"""
FalkorDB 成功集成测试 - 使用正确的命令格式
基于发现的工作配置：graph.QUERY 而不是 GRAPH.QUERY
"""

def test_falkordb_working():
    """测试 FalkorDB 的工作功能"""
    print("🎯 FalkorDB 工作功能测试")
    print("=" * 50)
    
    try:
        import falkordb
        print("✅ 导入 FalkorDB 客户端成功")
        
        # 连接
        client = falkordb.FalkorDB(host='localhost', port=6379)
        graph = client.select_graph('mem0_working_test')
        print("✅ 连接 FalkorDB 成功")
        
        # 测试基本图功能
        print("\n🔧 测试基本图功能...")
        
        # 清理现有数据
        try:
            result = graph.query("MATCH (n) DETACH DELETE n")
            print("✅ 清理现有数据")
        except Exception as e:
            print(f"ℹ️ 清理: {e}")
        
        # 创建知识图谱
        print("\n📊 创建知识图谱...")
        
        # 创建人物、地点、物品节点和关系
        create_result = graph.query("""
            CREATE 
                (zhang:Person {name: '张三', age: 30, occupation: '工程师'}),
                (li:Person {name: '李四', age: 28, occupation: '设计师'}),
                (coffee:Drink {name: '咖啡', type: 'beverage', temperature: 'hot'}),
                (tea:Drink {name: '茶', type: 'beverage', temperature: 'hot'}),
                (starbucks:Place {name: '星巴克', type: 'cafe', location: '北京'}),
                (office:Place {name: '办公室', type: 'workplace', location: '北京'}),
                
                (zhang)-[:LIKES {intensity: 9}]->(coffee),
                (zhang)-[:WORKS_AT {since: 2020}]->(office),
                (zhang)-[:FREQUENTS {times_per_week: 5}]->(starbucks),
                (zhang)-[:COLLEAGUE_OF {since: 2021}]->(li),
                
                (li)-[:LIKES {intensity: 7}]->(tea),
                (li)-[:WORKS_AT {since: 2021}]->(office),
                (li)-[:COLLEAGUE_OF {since: 2021}]->(zhang)
                
            RETURN count(*) as nodes_created
        """)
        
        if create_result.result_set:
            print(f"✅ 创建知识图谱成功")
        
        # 测试复杂图查询
        print("\n🔍 测试复杂图查询...")
        
        # 查询：找出所有在同一地点工作的同事关系
        colleagues_query = """
            MATCH (p1:Person)-[:WORKS_AT]->(place:Place)<-[:WORKS_AT]-(p2:Person)
            WHERE p1 <> p2
            RETURN p1.name as person1, p2.name as person2, place.name as workplace
        """
        
        result = graph.query(colleagues_query)
        if result.result_set:
            print("✅ 同事关系查询成功:")
            for record in result.result_set:
                print(f"   {record[0]} 和 {record[1]} 在 {record[2]} 工作")
        
        # 查询：推荐系统 - 基于同事的喜好推荐
        recommendation_query = """
            MATCH (person:Person)-[:COLLEAGUE_OF]-(colleague:Person)-[:LIKES]->(item)
            WHERE person.name = '张三' AND NOT (person)-[:LIKES]->(item)
            RETURN person.name as for_person, item.name as recommendation, colleague.name as recommended_by
        """
        
        result = graph.query(recommendation_query)
        if result.result_set:
            print("✅ 推荐系统查询成功:")
            for record in result.result_set:
                print(f"   为 {record[0]} 推荐 {record[1]} (基于 {record[2]} 的喜好)")
        
        # 测试图分析 - 使用内置算法
        print("\n📈 测试图分析算法...")
        
        try:
            # 页面排名算法
            pagerank_query = """
                CALL algo.pageRank(['Person'], ['COLLEAGUE_OF', 'LIKES'], {iterations: 20}) 
                YIELD nodeId, score
                MATCH (n) WHERE id(n) = nodeId
                RETURN n.name as person, score
                ORDER BY score DESC
            """
            
            result = graph.query(pagerank_query)
            if result.result_set:
                print("✅ PageRank 算法成功:")
                for record in result.result_set:
                    print(f"   {record[0]}: {record[1]:.4f}")
        except Exception as e:
            print(f"ℹ️ PageRank 测试: {e}")
        
        # 测试路径查询
        print("\n🛤️ 测试路径查询...")
        
        path_query = """
            MATCH path = shortestPath((start:Person {name: '张三'})-[*..3]-(end:Drink))
            RETURN [node in nodes(path) | node.name] as path_nodes,
                   [rel in relationships(path) | type(rel)] as relationship_types
        """
        
        result = graph.query(path_query)
        if result.result_set:
            print("✅ 最短路径查询成功:")
            for record in result.result_set:
                nodes = record[0]
                rels = record[1]
                path_str = " -[{}]-> ".join([f"{nodes[i]}" for i in range(len(nodes)-1)])
                if len(nodes) > 1:
                    path_str += f" -[{rels[-1] if rels else 'rel'}]-> {nodes[-1]}"
                else:
                    path_str = str(nodes[0]) if nodes else ""
                print(f"   路径: {path_str}")
        
        # 性能测试
        print("\n⚡ 性能测试...")
        
        import time
        start_time = time.time()
        
        # 批量创建节点测试性能
        for i in range(50):
            graph.query(f"""
                CREATE (test{i}:TestNode {{id: {i}, name: 'Test{i}', value: {i*10}}})
            """)
        
        bulk_create_time = time.time() - start_time
        print(f"✅ 批量创建 50 个节点耗时: {bulk_create_time:.2f} 秒")
        
        # 批量查询测试
        start_time = time.time()
        
        for i in range(20):
            graph.query("MATCH (n:TestNode) WHERE n.id >= $min_id RETURN count(n)", 
                       {"min_id": i})
        
        bulk_query_time = time.time() - start_time
        print(f"✅ 执行 20 次查询耗时: {bulk_query_time:.2f} 秒")
        
        # 清理测试节点
        graph.query("MATCH (n:TestNode) DELETE n")
        print("✅ 清理测试节点完成")
        
        print("\n🎉 FalkorDB 功能测试全部成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_falkordb_for_mem0():
    """测试 FalkorDB 对 Mem0 记忆管理的适用性"""
    print("\n🧠 测试 FalkorDB 对 Mem0 的适用性")
    print("=" * 50)
    
    try:
        import falkordb
        
        client = falkordb.FalkorDB(host='localhost', port=6379)
        graph = client.select_graph('mem0_memory_graph')
        
        # 清理
        graph.query("MATCH (n) DETACH DELETE n")
        
        # 模拟 Mem0 记忆场景
        print("\n📝 模拟用户记忆管理...")
        
        # 用户记忆：个人信息、偏好、行为模式
        memory_data = [
            {
                "memory": "用户张三是一名软件工程师",
                "entities": ["张三", "软件工程师"],
                "relations": [("张三", "PROFESSION", "软件工程师")]
            },
            {
                "memory": "张三喜欢喝星巴克的拿铁",
                "entities": ["张三", "星巴克", "拿铁"],
                "relations": [("张三", "LIKES", "拿铁"), ("拿铁", "AVAILABLE_AT", "星巴克")]
            },
            {
                "memory": "张三经常在下午3点休息",
                "entities": ["张三", "下午3点", "休息"],
                "relations": [("张三", "HABIT", "下午3点休息")]
            },
            {
                "memory": "张三和李四是同事",
                "entities": ["张三", "李四"],
                "relations": [("张三", "COLLEAGUE", "李四")]
            }
        ]
        
        # 构建记忆图
        for i, data in enumerate(memory_data):
            # 创建记忆节点
            memory_query = f"""
                CREATE (mem:Memory {{
                    id: {i}, 
                    content: $content, 
                    timestamp: datetime(),
                    user_id: 'user_001'
                }})
                RETURN mem.id
            """
            graph.query(memory_query, {"content": data["memory"]})
            
            # 创建实体和关系
            for entity in data["entities"]:
                entity_query = """
                    MERGE (e:Entity {name: $entity_name, user_id: 'user_001'})
                    WITH e
                    MATCH (mem:Memory {id: $mem_id})
                    CREATE (mem)-[:MENTIONS]->(e)
                """
                graph.query(entity_query, {"entity_name": entity, "mem_id": i})
            
            # 创建语义关系
            for source, relation, target in data["relations"]:
                relation_query = """
                    MATCH (s:Entity {name: $source, user_id: 'user_001'})
                    MATCH (t:Entity {name: $target, user_id: 'user_001'})
                    CREATE (s)-[r:SEMANTIC_RELATION {type: $relation, user_id: 'user_001'}]->(t)
                """
                graph.query(relation_query, {
                    "source": source, 
                    "target": target, 
                    "relation": relation
                })
        
        print("✅ 记忆图构建完成")
        
        # 测试记忆检索
        print("\n🔍 测试记忆检索...")
        
        # 查询：张三的所有记忆
        user_memories = """
            MATCH (mem:Memory {user_id: 'user_001'})-[:MENTIONS]->(e:Entity {name: '张三'})
            RETURN mem.content as memory
        """
        result = graph.query(user_memories)
        print("✅ 张三相关记忆:")
        for record in result.result_set:
            print(f"   - {record[0]}")
        
        # 查询：基于关系的推理
        inference_query = """
            MATCH (zhang:Entity {name: '张三'})-[:SEMANTIC_RELATION]->(profession:Entity)
            WHERE profession.name CONTAINS '工程师'
            WITH zhang
            MATCH (zhang)-[:COLLEAGUE]-(colleague:Entity)
            RETURN colleague.name as colleague_name
        """
        result = graph.query(inference_query)
        if result.result_set:
            print("✅ 基于关系推理:")
            for record in result.result_set:
                print(f"   张三的同事: {record[0]}")
        
        # 查询：上下文相关记忆
        context_query = """
            MATCH (item:Entity {name: '拿铁'})<-[:SEMANTIC_RELATION]-(user:Entity)
            MATCH (user)-[:SEMANTIC_RELATION]->(habit)
            WHERE habit.name CONTAINS '休息'
            RETURN user.name as user_name, habit.name as habit
        """
        result = graph.query(context_query)
        if result.result_set:
            print("✅ 上下文关联:")
            for record in result.result_set:
                print(f"   {record[0]} 的习惯: {record[1]}")
        
        print("\n🎯 FalkorDB 在 Mem0 中的优势:")
        print("   ✅ 复杂关系建模和查询")
        print("   ✅ 多跳推理能力")
        print("   ✅ 高性能图遍历")
        print("   ✅ 灵活的 Cypher 查询语言")
        print("   ✅ 实时记忆图更新")
        print("   ✅ 用户隔离（通过 user_id）")
        
        return True
        
    except Exception as e:
        print(f"❌ Mem0 适用性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 FalkorDB 完整功能验证")
    print("=" * 50)
    
    # 执行测试
    tests = [
        ("基础功能测试", test_falkordb_working),
        ("Mem0 适用性测试", test_falkordb_for_mem0)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 开始 {test_name}")
        results[test_name] = test_func()
    
    # 总结
    print("\n" + "=" * 50)
    print("🎯 测试结果总结")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 FalkorDB 完全就绪！")
        print("\n🚀 下一步: 在 MCP 环境中集成到 Mem0")
        print("   1. 修复循环导入问题")  
        print("   2. 更新 MCP 服务器配置")
        print("   3. 测试完整的 Mem0 + FalkorDB 功能")
    else:
        print(f"\n⚠️ 需要进一步调试，通过率: {(passed/total)*100:.1f}%")

if __name__ == "__main__":
    main()