import requests
import numpy as np
from .embedding import Embedding
from config.config_info import settings

class OneAPIEmbedding(Embedding):
    def __init__(self, base_url:str=settings.ONEAPI_BASE_URL, api_key:str=settings.ONEAPI_API_KEY, model:str=settings.ONEAPI_EMBEDDING_MODEL) -> None:
        self.base_url = base_url.rstrip('/')  # 移除末尾的斜杠
        self.api_key = api_key
        self.model = model
        
    def embed_with_str(self, text:str, embType:str) -> list[float]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "input": text
        }
        
        response = requests.post(
            f"{self.base_url}/embeddings",
            headers=headers,
            json=payload,
            verify=False
        )
        
        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        else:
            raise Exception(f"API调用失败: {response.status_code} - {response.text}")

def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    similarity = dot_product / (norm_vector1 * norm_vector2)
    return similarity

if __name__ == '__main__':
    model = "m3e-base"
    base_url = "https://oneapi.k.cn:8443/v1"
    em = OneAPIEmbedding(base_url=base_url, model=model)
    
    v1 = em.embed_with_str("=-=-=-=-=-", 'query')
    v2 = em.embed_with_str("学校各个网站链接北京化工大学官网www.buct.edu.cn教务管理系统jwglxt.buct.edu.cn教务处网站jiaowuchu.buct.edu.cn", "document")
    print(len(v1))
    cos = cosine_similarity(v1, v2)
    print("相似度1:" + str(cos))

    v1 = em.embed_with_str("访客如何到北化游览", 'query')
    v2 = em.embed_with_str("校外人员进校参观预约流程：1、学生提供预约链接 2、访客填写访客信息 3、等待审批", "document")
    cos = cosine_similarity(v1, v2)
    print("相似度2:" + str(cos))