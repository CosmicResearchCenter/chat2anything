from core.rag.embedding.embedding_manager import EmbeddingManager
from config.config_info import settings
from core.utils.utils import GetDefaultEmbedding

class EmbeddingConfig:
    def __init__(self):
        pass
    
    def get_dim(self)->int:
        """获取向量维度"""
        config = GetDefaultEmbedding()
        embedding_client = EmbeddingManager().create_embedding(embedding_provider=config.vendor_type,model=config.model)
        
        text = "获取向量维度"
        vector = embedding_client.embed_with_str(text, "query")
        dim = len(vector)
        return dim