import requests
from langchain_core.documents import Document
from typing import List
from config.config_info import settings
from elasticsearch import Elasticsearch,helpers

class ElasticClient:
    def __init__(self, base_url: str = settings.ES_BASE_URL, port: int = settings.ES_BASE_PORT, scheme: str = "http") -> None:
        self.base_url = base_url
        self.port = port
        self.scheme = scheme
        self.es_client = Elasticsearch(hosts=[{
            "host": self.base_url,
            "port": self.port,
            "scheme": self.scheme
        }])
    
    # 查询
    def search(self,question:str,knowledgeBaseID:str):
        # 构造查询语句
        query = {
            "query": {
                "match": {
                    # 根据content字段进行模糊查询
                    "content": {
                        "query": question,
                        # 设置模糊查询的相似度
                        "fuzziness": "AUTO"
                    }
                }
            },
            # 设置返回结果的最大数量为2
            "size": 5 
        }
    
        # 使用Elasticsearch客户端进行搜索
        response = self.es_client.search(index=knowledgeBaseID, body=query)
    
        # 如果搜索结果不为空
        if response['hits']['hits']:
            # 返回搜索结果
            print("es结果：",response['hits']['hits'])
            return response['hits']['hits']
        else:
            # 返回未找到结果的消息
            return "Not Hit"
        
    # 批量写入数据
    def insert_data(self, docs:List[Document],knowledgeBaseID:str,knowledgeDocName:str):
        data = []
        for doc in docs:
            item = {
                "content":doc.page_content,
                "knowledgeDocName":knowledgeDocName
            }
            data.append(item)
        # 构建批量写入的 actions 列表
        actions = [
            {
                "_index": knowledgeBaseID,  # 替换为你的索引名称
                "_source": item
            }
            for item in data
        ]
        # 批量写入数据并获取响应
        success, failed = helpers.bulk(self.es_client, actions, raise_on_error=False, stats_only=False)

        return success, failed
    
    # 创建知识库
    def create_index(self,knowledgeBaseID:str)->str:
        # # 创建索引
        response = self.es_client.indices.create(index=knowledgeBaseID)
        print(response)
        return response

    # 删除索引
    def delete_index(self,knowledgeBaseID:str)->str:
        # 删除索引
        response = self.es_client.indices.delete(index=knowledgeBaseID)
        # print(response)
        return response
if __name__ == "__main__":
    client = ElasticClient(base_url="10.116.123.148",port=9200)
    # client.create_index("test","test")
    client.create_index(knowledgeBaseID="kb292f83a3955549")