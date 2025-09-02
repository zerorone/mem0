import logging
from typing import Dict, List

from mem0.graphs.utils import get_delete_messages
from mem0.utils.factory import EmbedderFactory, LlmFactory

logger = logging.getLogger(__name__)

try:
    import redis
    import falkordb
    from falkordb import FalkorDB as FalkorDBClient
except ImportError:
    logger.error("Failed to import FalkorDB. Please install it using: pip install falkordb redis")
    raise ImportError("FalkorDB dependencies are required. Install: pip install falkordb redis")


class FalkorDB:
    """
    FalkorDB 图数据库适配器
    专为 GraphRAG 设计，原生支持向量相似度搜索和图遍历
    """
    
    def __init__(self, config):
        self.config = config
        self.graph_name = config.graph_store.config.graph_name
        
        # 创建 FalkorDB 连接
        self.client = FalkorDBClient(
            host=config.graph_store.config.host,
            port=config.graph_store.config.port,
            decode_responses=config.graph_store.config.decode_responses
        )
        
        # 选择图
        self.graph = self.client.select_graph(self.graph_name)
        
        # 创建嵌入模型
        self.embedding_model = self._create_embedding_model(config)
        
        # 创建 LLM
        if config.llm:
            self.llm = self._create_llm(config, config.llm.provider)
            self.llm_provider = config.llm.provider
        else:
            self.llm = None
            self.llm_provider = None
            
        # 初始化图结构
        self._initialize_graph()
        
    @staticmethod
    def _create_embedding_model(config):
        """创建嵌入模型"""
        return EmbedderFactory.create(
            config.embedder.provider,
            config.embedder.config,
            {"enable_embeddings": True},
        )
    
    @staticmethod
    def _create_llm(config, llm_provider):
        """创建 LLM 模型"""
        return LlmFactory.create(llm_provider, config.llm.config)
    
    def _initialize_graph(self):
        """初始化图数据库结构，创建向量索引"""
        try:
            # 创建节点向量索引
            create_index_query = f"""
            CALL db.idx.vector.createNodeIndex(
                'Entity', 
                'embedding', 
                1024, 
                'COSINE'
            )
            """
            self.graph.query(create_index_query)
            logger.info("FalkorDB 向量索引创建成功")
            
        except Exception as e:
            # 索引可能已存在，忽略错误
            logger.debug(f"向量索引创建跳过: {e}")
    
    def add(self, data, filters):
        """
        添加图记忆数据
        
        Args:
            data (str): 要添加的数据
            filters (dict): 过滤条件，包含 user_id
            
        Returns:
            dict: 添加结果
        """
        if not self.llm:
            logger.warning("未配置 LLM，无法进行图记忆管理")
            return {"added_entities": [], "message": "需要配置 LLM 进行图记忆管理"}
        
        try:
            # 从数据中提取实体和关系
            entities_relations = self._extract_entities_relations(data, filters)
            
            added_entities = []
            for relation in entities_relations:
                # 添加源节点
                self._add_node_with_embedding(
                    relation["source"], 
                    relation.get("source_type", "Entity"),
                    filters["user_id"]
                )
                
                # 添加目标节点  
                self._add_node_with_embedding(
                    relation["destination"],
                    relation.get("destination_type", "Entity"), 
                    filters["user_id"]
                )
                
                # 创建关系
                self._add_relationship(
                    relation["source"],
                    relation["destination"], 
                    relation["relationship"],
                    filters["user_id"]
                )
                
                added_entities.append(relation)
                
            logger.info(f"成功添加 {len(added_entities)} 个图记忆关系")
            return {"added_entities": added_entities}
            
        except Exception as e:
            logger.error(f"添加图记忆失败: {e}")
            return {"added_entities": [], "error": str(e)}
    
    def _extract_entities_relations(self, data, filters):
        """从文本中提取实体和关系"""
        # 这里简化实现，实际应使用 LLM 进行实体和关系抽取
        # 参考 neptune/base.py 中的实现
        
        # 模拟简单的实体关系抽取
        relations = []
        user_id = filters["user_id"]
        
        # 简单示例：如果文本包含"喜欢"，创建相应的关系
        if "喜欢" in data:
            parts = data.split("喜欢")
            if len(parts) >= 2:
                source = parts[0].strip() or user_id
                destination = parts[1].strip()
                relations.append({
                    "source": source.lower().replace(" ", "_"),
                    "destination": destination.lower().replace(" ", "_"),
                    "relationship": "likes",
                    "source_type": "Person",
                    "destination_type": "Object"
                })
        
        return relations
    
    def _add_node_with_embedding(self, node_name, node_type, user_id):
        """添加带向量嵌入的节点"""
        try:
            # 生成节点嵌入
            embedding = self.embedding_model.embed(node_name)
            embedding_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
            
            # 使用 MERGE 避免重复节点
            query = """
            MERGE (n:Entity {name: $node_name, user_id: $user_id})
            SET n.type = $node_type, n.embedding = $embedding
            RETURN n
            """
            
            params = {
                "node_name": node_name,
                "user_id": user_id, 
                "node_type": node_type,
                "embedding": embedding_list
            }
            
            self.graph.query(query, params)
            logger.debug(f"添加节点: {node_name} (类型: {node_type})")
            
        except Exception as e:
            logger.error(f"添加节点失败 {node_name}: {e}")
    
    def _add_relationship(self, source, destination, relationship, user_id):
        """创建节点间关系"""
        try:
            query = """
            MATCH (s:Entity {name: $source, user_id: $user_id})
            MATCH (d:Entity {name: $destination, user_id: $user_id})
            MERGE (s)-[r:RELATES {type: $relationship}]->(d)
            SET r.user_id = $user_id
            RETURN r
            """
            
            params = {
                "source": source,
                "destination": destination,
                "relationship": relationship,
                "user_id": user_id
            }
            
            self.graph.query(query, params)
            logger.debug(f"创建关系: {source} -[{relationship}]-> {destination}")
            
        except Exception as e:
            logger.error(f"创建关系失败: {e}")
    
    def search(self, query, filters, limit=10):
        """
        基于向量相似度和图遍历的混合搜索
        
        Args:
            query (str): 搜索查询
            filters (dict): 过滤条件
            limit (int): 返回结果数量限制
            
        Returns:
            list: 搜索结果
        """
        try:
            # 生成查询向量
            query_embedding = self.embedding_model.embed(query)
            query_embedding_list = query_embedding.tolist() if hasattr(query_embedding, 'tolist') else list(query_embedding)
            
            # 使用 FalkorDB 的向量相似度搜索 + 图遍历
            search_query = """
            CALL db.idx.vector.queryNodes(
                'Entity', 
                'embedding', 
                $limit, 
                $query_embedding
            ) YIELD node, score
            WHERE node.user_id = $user_id
            WITH node, score
            MATCH (node)-[r]->(connected)
            WHERE connected.user_id = $user_id
            RETURN node.name as source, 
                   type(r) as relationship, 
                   connected.name as destination,
                   score
            ORDER BY score DESC
            LIMIT $limit
            """
            
            params = {
                "query_embedding": query_embedding_list,
                "user_id": filters["user_id"],
                "limit": limit
            }
            
            results = self.graph.query(search_query, params)
            
            search_results = []
            for result in results:
                search_results.append({
                    "source": result.get("source", ""),
                    "relationship": result.get("relationship", ""),
                    "destination": result.get("destination", ""),
                    "score": result.get("score", 0.0)
                })
            
            logger.info(f"图向量混合搜索返回 {len(search_results)} 条结果")
            return search_results
            
        except Exception as e:
            logger.error(f"图搜索失败: {e}")
            return []
    
    def get_all(self, filters, limit=100):
        """获取用户的所有图记忆"""
        try:
            query = """
            MATCH (source:Entity)-[r]->(dest:Entity)
            WHERE source.user_id = $user_id AND dest.user_id = $user_id
            RETURN source.name as source, 
                   type(r) as relationship, 
                   dest.name as destination
            LIMIT $limit
            """
            
            params = {
                "user_id": filters["user_id"],
                "limit": limit
            }
            
            results = self.graph.query(query, params)
            
            all_memories = []
            for result in results:
                all_memories.append({
                    "source": result.get("source", ""),
                    "relationship": result.get("relationship", ""),
                    "destination": result.get("destination", "")
                })
            
            return all_memories
            
        except Exception as e:
            logger.error(f"获取所有图记忆失败: {e}")
            return []
    
    def delete_all(self, filters):
        """删除用户的所有图记忆"""
        try:
            query = """
            MATCH (n:Entity)
            WHERE n.user_id = $user_id
            DETACH DELETE n
            """
            
            params = {"user_id": filters["user_id"]}
            self.graph.query(query, params)
            
            logger.info(f"已删除用户 {filters['user_id']} 的所有图记忆")
            
        except Exception as e:
            logger.error(f"删除所有图记忆失败: {e}")
    
    def update(self, data, filters):
        """更新图记忆"""
        # 简化实现：删除后重新添加
        # 实际应该实现更智能的更新逻辑
        return self.add(data, filters)
    
    def delete(self, data, filters):
        """删除特定的图记忆"""
        # 这里可以实现基于 LLM 的智能删除逻辑
        # 参考 neptune/base.py 中的 _get_delete_entities_from_search_output
        logger.info("图记忆删除功能待完善")
        return {"deleted_entities": []}