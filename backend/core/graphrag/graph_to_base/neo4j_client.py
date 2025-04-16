from neo4j import GraphDatabase, Driver, Session
from typing import List, Dict, Optional
from ..types.types import Entity_Label, Entity, Entity_Relation

class Neo4jClient:
    def __init__(self, uri: str, username: str, password: str):
        self.driver: Driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self) -> None:
        self.driver.close()
        
    def create_entity(self, entity: Entity) -> None:
        """将实体导入到Neo4j数据库中"""
        with self.driver.session() as session:
            # 构造属性字典
            props = entity.attribute.copy()
            if entity.ext_info:
                props["ext_info"] = entity.ext_info
                
            # 创建节点的Cypher查询
            query = f"CREATE (n:{entity.label} $props)"
            session.run(query, props=props)

    def create_relation(self, relation: Entity_Relation) -> None:
        """将实体关系导入到Neo4j数据库中"""
        with self.driver.session() as session:
            # 为源实体和目标实体创建或匹配节点
            source_props = relation.source.attribute.copy()
            if relation.source.ext_info:
                source_props["ext_info"] = relation.source.ext_info
                
            target_props = relation.target.attribute.copy()
            if relation.target.ext_info:
                target_props["ext_info"] = relation.target.ext_info
            
            # 创建关系的Cypher查询
            query = f"""
            MERGE (a:{relation.source.label} $source_props)
            MERGE (b:{relation.target.label} $target_props)
            CREATE (a)-[r:{relation.relation} {{evidence: $evidence}}]->(b)
            """
            
            session.run(query, 
                        source_props=source_props,
                        target_props=target_props,
                        evidence=relation.evidence)

    def batch_import(self, entities: List[Entity], relations: List[Entity_Relation]) -> None:
        """批量导入实体和关系到Neo4j数据库"""
        # 先导入所有实体
        for entity in entities:
            self.create_entity(entity)
        
        # 再导入所有关系
        for relation in relations:
            self.create_relation(relation)

    def find_entities_by_label(self, label: str) -> List[Dict]:
        """通过标签查找实体"""
        with self.driver.session() as session:
            query = f"MATCH (n:{label}) RETURN n"
            result = session.run(query)
            return [dict(record["n"]) for record in result]

    def find_entity_by_attributes(self, label: str, attributes: Dict[str, str]) -> List[Dict]:
        """通过属性查找实体"""
        with self.driver.session() as session:
            # 构建属性匹配条件
            conditions = []
            for key, value in attributes.items():
                conditions.append(f"n.{key} = ${key}")
            
            condition_str = " AND ".join(conditions) if conditions else "1=1"
            query = f"MATCH (n:{label}) WHERE {condition_str} RETURN n"
            
            result = session.run(query, **attributes)
            return [dict(record["n"]) for record in result]

    def find_relations_between_entities(self, source_label: str, source_attrs: Dict[str, str],
                                      target_label: str, target_attrs: Dict[str, str],
                                      relation_type: Optional[str] = None) -> List[Dict]:
        """查找两个实体之间的关系"""
        with self.driver.session() as session:
            # 构建源实体和目标实体的属性匹配条件
            source_conditions = []
            target_conditions = []
            params = {}
            
            for key, value in source_attrs.items():
                source_conditions.append(f"a.{key} = $a_{key}")
                params[f"a_{key}"] = value
            
            for key, value in target_attrs.items():
                target_conditions.append(f"b.{key} = $b_{key}")
                params[f"b_{key}"] = value
            
            source_condition_str = " AND ".join(source_conditions) if source_conditions else "1=1"
            target_condition_str = " AND ".join(target_conditions) if target_conditions else "1=1"
            
            # 构建关系类型条件
            rel_condition = f"type(r) = '{relation_type}'" if relation_type else "1=1"
            
            query = f"""
            MATCH (a:{source_label})-[r]->(b:{target_label})
            WHERE {source_condition_str} AND {target_condition_str} AND {rel_condition}
            RETURN a, r, b
            """
            
            result = session.run(query, **params)
            return [{"source": dict(record["a"]), "relation": dict(record["r"]), "target": dict(record["b"])} for record in result]

    def find_related_entities(self, label: str, attributes: Dict[str, str], direction: str = "both") -> List[Dict]:
        """
        查找与指定实体相关的所有关系
        direction: "outgoing", "incoming", "both"
        """
        with self.driver.session() as session:
            # 构建属性匹配条件
            conditions = []
            for key, value in attributes.items():
                conditions.append(f"n.{key} = ${key}")
            
            condition_str = " AND ".join(conditions) if conditions else "1=1"
            
            if direction == "outgoing":
                query = f"MATCH (n:{label})-[r]->(m) WHERE {condition_str} RETURN n, r, m"
            elif direction == "incoming":
                query = f"MATCH (n:{label})<-[r]-(m) WHERE {condition_str} RETURN n, r, m"
            else:  # both
                query = f"MATCH (n:{label})-[r]-(m) WHERE {condition_str} RETURN n, r, m"
            
            result = session.run(query, **attributes)
            return [{"entity": dict(record["n"]), "relation": dict(record["r"]), "related": dict(record["m"])} for record in result]

    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """执行自定义的Cypher查询"""
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]
