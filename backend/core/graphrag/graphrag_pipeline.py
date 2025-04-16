from .types.types import Entity_Label, Entity, Entity_Relation
from .doc_to_graph.doc_to_graph import DocToGraph
from .graph_to_base.neo4j_client import Neo4jClient
from typing import List, Dict, Optional

class GraphRAG_Pipeline:
    def __init__(self, neo4j_uri: str = None, neo4j_user: str = None, neo4j_password: str = None):
        """
        初始化 GraphRAG 流水线
        
        Args:
            neo4j_uri: Neo4j 数据库 URI
            neo4j_user: Neo4j 用户名
            neo4j_password: Neo4j 密码
        """
        self.doc_to_graph = DocToGraph()
        if neo4j_uri and neo4j_user and neo4j_password:
            self.neo4j_client = Neo4jClient(uri=neo4j_uri, username=neo4j_user, password=neo4j_password)
        else:
            self.neo4j_client = None
    
    def set_neo4j_client(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str) -> None:
        """设置 Neo4j 客户端"""
        if self.neo4j_client:
            self.neo4j_client.close()
        self.neo4j_client = Neo4jClient(uri=neo4j_uri, username=neo4j_user, password=neo4j_password)
    
    def process_document(self, doc_path: str) -> Dict:
        """
        处理文档，提取实体和关系，并存入 Neo4j 数据库
        
        Args:
            doc_path: 文档路径
            
        Returns:
            包含提取的实体和关系的字典
        """
        # 读取文档
        text = self.doc_to_graph.read_doc(doc_path)
        return self.process_text(text)
    
    def process_text(self, text: str) -> Dict:
        """
        处理文本，提取实体和关系，并存入 Neo4j 数据库
        
        Args:
            text: 文本内容
            
        Returns:
            包含提取的实体和关系的字典
        """
        # 提取实体标签
        entity_labels = self.doc_to_graph.entity_abstract(text)
        
        # 提取实体
        entities = self.doc_to_graph.entity_extraction(text)
        
        # 提取实体关系
        relations = self.doc_to_graph.entity_relation(text)
        
        # 如果 Neo4j 客户端已设置，则将实体和关系存入 Neo4j
        if self.neo4j_client:
            self.neo4j_client.batch_import(
                entities=self.doc_to_graph.entity_list,
                relations=relations
            )
        
        return {
            "entity_labels": entity_labels,
            "entities": entities,
            "relations": relations
        }
    
    def query_entities_by_label(self, label: str) -> List[Dict]:
        """
        根据标签查询实体
        
        Args:
            label: 实体标签
            
        Returns:
            符合条件的实体列表
        """
        if not self.neo4j_client:
            raise ValueError("Neo4j 客户端尚未设置")
        return self.neo4j_client.find_entities_by_label(label)
    
    def query_entities_by_attributes(self, label: str, attributes: Dict[str, str]) -> List[Dict]:
        """
        根据属性查询实体
        
        Args:
            label: 实体标签
            attributes: 属性字典
            
        Returns:
            符合条件的实体列表
        """
        if not self.neo4j_client:
            raise ValueError("Neo4j 客户端尚未设置")
        return self.neo4j_client.find_entity_by_attributes(label, attributes)
    
    def query_relations_between_entities(self, source_label: str, source_attrs: Dict[str, str],
                                        target_label: str, target_attrs: Dict[str, str],
                                        relation_type: Optional[str] = None) -> List[Dict]:
        """
        查询两个实体之间的关系
        
        Args:
            source_label: 源实体标签
            source_attrs: 源实体属性
            target_label: 目标实体标签
            target_attrs: 目标实体属性
            relation_type: 关系类型，可选
            
        Returns:
            符合条件的关系列表
        """
        if not self.neo4j_client:
            raise ValueError("Neo4j 客户端尚未设置")
        return self.neo4j_client.find_relations_between_entities(
            source_label, source_attrs, target_label, target_attrs, relation_type
        )
    
    def query_related_entities(self, label: str, attributes: Dict[str, str], direction: str = "both") -> List[Dict]:
        """
        查询与指定实体相关的所有实体
        
        Args:
            label: 实体标签
            attributes: 属性字典
            direction: 关系方向，可选值为 "outgoing"、"incoming" 或 "both"
            
        Returns:
            相关实体列表
        """
        if not self.neo4j_client:
            raise ValueError("Neo4j 客户端尚未设置")
        return self.neo4j_client.find_related_entities(label, attributes, direction)
    
    def execute_custom_query(self, query: str, params: Dict = None) -> List[Dict]:
        """
        执行自定义的 Cypher 查询
        
        Args:
            query: Cypher 查询语句
            params: 查询参数
            
        Returns:
            查询结果
        """
        if not self.neo4j_client:
            raise ValueError("Neo4j 客户端尚未设置")
        return self.neo4j_client.execute_query(query, params or {})
    
    def close(self) -> None:
        """关闭 Neo4j 连接"""
        if self.neo4j_client:
            self.neo4j_client.close()

if __name__ == "__main__":
    # 创建 GraphRAG_Pipeline 实例
    pipeline = GraphRAG_Pipeline(neo4j_uri="bolt://222.199.255.41:7687", neo4j_user="neo4j", neo4j_password="password")

    # 处理文档
    result = pipeline.process_document("E:\\Projects\\Chat2anything\\backend\\test\\example.txt")

    # 查询实体
    entities = pipeline.query_entities_by_label("Person")

    # 关闭连接
    pipeline.close()