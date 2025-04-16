from ..prompt_template.prompt_template import PromptTemplate
from ..prompt_template.prompts import entity_relation_prompt,entity_abstract_prompt,entity_extraction_prompt
from core.llm.llm_manager import LLM_Manager
from config.config_info import settings
import json
from ..graph_to_base.neo4j_client import Neo4jClient
from ..types.types import Entity_Label,Entity,Entity_Relation
from typing import List,Dict

class DocToGraph:
    def __init__(self) -> None:
        self.entity_label_list:List[Entity_Label] = []
        # self.entity_abstract_list = []
        self.entity_list:List[Entity] = []
        self.entity_relation_list:List[Entity_Relation] = []
        
    # 读取文档
    def read_doc(self,doc_path:str) -> str:
        with open(doc_path, 'r',encoding="utf-8") as f:
            text = f.read()
        return text
    
    def text_to_json(self,text:str):
        # 去除可能存在的Markdown代码块标记
        text = text.strip().strip('```json').strip('```')
        
        try:
            # 尝试将文本解析为JSON对象
            json_obj = json.loads(text)
            
            return json_obj
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return None
        
    
    # 提取文档中的抽象实体
    def entity_abstract(self, text: str) -> List[Entity_Label]:
        prompt = PromptTemplate(
                        template=entity_abstract_prompt,
                        input_variables=['entity_label_list','text']            
                    )
        llm = LLM_Manager().creatLLM(settings.LLM_PROVIDER)
        entity_label_list_str = ",".join([label.name for label in self.entity_label_list]) if self.entity_label_list else ""
        prompt = prompt.render(
            entity_label_list = entity_label_list_str,
            text = text
        )
        answer:str = llm.ChatToBot(prompt)
        
        answer = answer.replace(" ","") 
        entity_label_names = answer.split(",")
        
        result:List[Entity_Label]= []
        for label_name in entity_label_names:
            if label_name:
                label = Entity_Label(name=label_name)
                self.entity_label_list.append(label)
                result.append(label)
                
        return result
    
    # 提取文档中的实体
    def entity_extraction(self, text: str) -> List[Entity]:
        prompt = PromptTemplate(
                        template=entity_extraction_prompt,
                        input_variables=['entity_list', 'text']
                    )
        llm = LLM_Manager().creatLLM(settings.LLM_PROVIDER)
          
        entity_label_list_str = ",".join([label.name for label in self.entity_label_list]) 
        answer: str = prompt.render(
            entity_list=str([entity.model_dump() for entity in self.entity_list]),
            entity_label_list=entity_label_list_str,
            text=text
        )
        
        answer = llm.ChatToBot(answer)
        
        # 解析文本 文本转json
        json_data = self.text_to_json(answer) 
        
        result = []
        if json_data and 'entities' in json_data:
            for entity_data in json_data['entities']:
                # 确保数据符合Entity类定义
                if 'name' not in entity_data:
                    # 名称可能来自其他字段或生成一个默认名称
                    entity_data['name'] = entity_data.get('label', 'unnamed')
                
                entity = Entity(**entity_data)
                self.entity_list.append(entity)
                result.append(entity)
                
        return result
    
    # 建立文档中实体对象之间的关系
    def entity_relation(self, text: str) -> List[Entity_Relation]:
        prompt = PromptTemplate(
                        template=entity_relation_prompt,
                        input_variables=['entity_relation_list', 'text', 'entity_list']
                    )
        llm = LLM_Manager().creatLLM(settings.LLM_PROVIDER)
        
        prompt = prompt.render(
            entity_relation_list=str([relation.model_dump() for relation in self.entity_relation_list]),
            text=text,
            entity_list=str([entity.model_dump() for entity in self.entity_list])
        )
        
        answer: str = llm.ChatToBot(prompt)

        # 解析文本 文本转json
        json_data = self.text_to_json(answer)
        print(json_data)
        result = []
        if json_data and 'relations' in json_data:
            for relation_data in json_data['relations']:
                source = Entity(
                    label=relation_data['source'].get('label', 'unknown'),
                    attribute={"name": relation_data['source'].get('name', 'unknown')},
                    ext_info=relation_data['source'].get('ext_info', '')
                )
                target = Entity(
                    label=relation_data['target'].get('label', 'unknown'),
                    attribute={"name": relation_data['target'].get('name', 'unknown')},
                    ext_info=relation_data['target'].get('ext_info', '')
                )
                relation = relation_data.get('relation', 'unknown')
                evidence = relation_data.get('evidence', '')
                result.append(Entity_Relation(source=source, target=target, relation=relation, evidence=evidence))
            
        return result
        
if __name__ == "__main__":
    doc_to_graph = DocToGraph()
    text = doc_to_graph.read_doc('E:\\Projects\\Chat2anything\\backend\\test\\example.txt')
    doc_to_graph.entity_abstract(text)
    print("提取的实体类型：")
    print(doc_to_graph.entity_label_list)
    doc_to_graph.entity_extraction(text)
    print("提取的实体：")
    print(doc_to_graph.entity_list)
    entity_relation_list = doc_to_graph.entity_relation(text)
    print("提取的实体关系：")
    print(entity_relation_list)