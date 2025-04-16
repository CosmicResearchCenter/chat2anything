from .doubao_embedding import DouBaoEmbedding
from .openai_embedding import OpenAIEmbedding
from .oneapi_embedding import OneAPIEmbedding
from .siliconflow_embedding import SiliconFlowEmbedding
from enum import Enum
from .embedding import Embedding

class EmbeddingType(Enum):
    DOUBAO = "DOUBAO"
    OPENAI = "OPENAI"
    ONEAPI = "ONEAPI"
    SILICONFLOW = "SILICONFLOW"

    @classmethod
    def get_embedding(cls, name: str):
        print(f"Trying to get embedding for name: {name}")
        for member_name, member in cls.__members__.items():
            if member_name == name:
                return member
        else:
            raise Exception("Not supported embedding type")

class EmbeddingManager:
    def create_embedding(self, name: str)->Embedding:
        embedding_type = EmbeddingType.get_embedding(name)
        if embedding_type == EmbeddingType.DOUBAO:
            return DouBaoEmbedding()
        elif embedding_type == EmbeddingType.OPENAI:
            return OpenAIEmbedding()
        elif embedding_type == EmbeddingType.ONEAPI:
            return OneAPIEmbedding()
        elif embedding_type == EmbeddingType.SILICONFLOW:
            return SiliconFlowEmbedding()
        else:
            raise Exception("Not supported embedding type Now")