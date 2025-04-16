from openai import OpenAI
import numpy as np
from .embedding import Embedding
from config.config_info import settings

class OpenAIEmbedding(Embedding):
    def __init__(self,base_url:str=settings.OPENAI_BASE_URL,api_key:str=settings.OPENAI_API_KEY,model:str=settings.OPENAI_EMBEDDING_MODEL):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = model

    def embed_with_str(self,text:str,embType:str)-> list[float]:    
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)
    similarity = dot_product / (norm_vector1 * norm_vector2)
    return similarity
# print(len(em.embed_with_str("你好","query")))
if __name__ == '__main__':
    em = OpenAIEmbedding()
    
    v1 = em.embed_with_str("=-=-=-=-=-",'query')
    v2 = em.embed_with_str("学校各个网站链接北京化工大学官网www.buct.edu.cn教务管理系统jwglxt.buct.edu.cn教务处网站jiaowuchu.buct.edu.cn","document")
    print(len(v1))
    cos = cosine_similarity(v1,v2)

    print("相似度1:"+str(cos))


    v1 = em.embed_with_str("访客如何到北化游览",'query')
    v2 = em.embed_with_str("校外人员进校参观预约流程：1、学生提供预约链接 2、访客填写访客信息 3、等待审批","document")

    cos = cosine_similarity(v1,v2)

    print("相似度2:"+str(cos))