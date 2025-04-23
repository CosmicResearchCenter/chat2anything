from core.rag.embedding.embedding_manager import EmbeddingManager
from config.config_info import settings

class EmbeddingConfig:
    def __init__(self):
        pass
    
    def get_dim(self)->int:
        """获取向量维度"""
        embedding_client = EmbeddingManager().create_embedding(settings.EMBEDDING_MODEL_PROVIDER)
        
        text = "获取向量维度"
        vector = embedding_client.embed_with_str(text, "query")
        dim = len(vector)
        return dim