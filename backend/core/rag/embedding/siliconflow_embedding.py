import requests
import numpy as np
from .embedding import Embedding
from config.config_info import settings

class SiliconFlowEmbedding(Embedding):
    def __init__(self, 
                 api_key: str,
                 target_dim: int ,
                 base_url: str = 'https://api.siliconflow.cn',
                 model: str ='BAAI/bge-large-zh-v1.5'):  # 默认目标维度为1536，与OpenAI维度一致
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.target_dim = target_dim
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def embed_with_str(self, text: str, embType: str) -> list[float]:
        payload = {
            "model": self.model,
            "input": text,
            "encoding_format": "float"
        }
        
        response = requests.post(
            f"{self.base_url}/v1/embeddings", 
            json=payload, 
            headers=self.headers
        )
        
        response_data = response.json()
        embedding = response_data["data"][0]["embedding"]
        
        # 检查维度并适配到目标维度
        return self._adjust_vector_dimension(embedding)
    
    def _adjust_vector_dimension(self, vector: list[float]) -> list[float]:
        """调整向量维度以匹配目标维度"""
        current_dim = len(vector)
        
        # 如果已经是目标维度，直接返回
        if current_dim == self.target_dim:
            return vector
            
        # 打印维度调整日志
        print(f"调整向量维度: 从 {current_dim} 到 {self.target_dim}")
        
        # 如果当前维度小于目标维度，填充零
        if current_dim < self.target_dim:
            return vector + [0.0] * (self.target_dim - current_dim)
        
        # 如果当前维度大于目标维度，截断
        return vector[:self.target_dim]
