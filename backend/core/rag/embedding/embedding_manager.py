from .doubao_embedding import DouBaoEmbedding
from .openai_embedding import OpenAIEmbedding
from .oneapi_embedding import OneAPIEmbedding
from .siliconflow_embedding import SiliconFlowEmbedding
from enum import Enum
from .embedding import Embedding
from config.embedding_config import(
    DOUBAO_Embedding_Config,
    OneAPI_Embedding_Config,
    OpenAI_Embedding_Config,
    SILICONFLOW_Embedding_Config
)
# 导入 ValueError 用于更具体的异常处理
from builtins import ValueError

class EmbeddingType(Enum):
    DOUBAO = "DOUBAO"
    OPENAI = "OPENAI"
    ONEAPI = "ONEAPI"
    SILICONFLOW = "SILICONFLOW"

    @classmethod
    def get_embedding_type(cls, name: str): # 方法名可以更清晰
        print(f"Trying to get embedding type for name: {name}")
        # 忽略大小写进行比较
        upper_name = name.upper()
        for member_name, member in cls.__members__.items():
            if member_name == upper_name:
                return member
        else:
            # 抛出 ValueError 而不是通用 Exception
            raise ValueError(f"不支持的 Embedding 提供商类型: {name}")

class EmbeddingManager:
    def create_embedding(self, embedding_provider: str,model:str)-> Embedding: # 参数名可以更清晰
        try:
            embedding_type = EmbeddingType.get_embedding_type(embedding_provider)
        except ValueError as e:
            raise e # 直接抛出 get_embedding_type 抛出的异常

        # 根据类型加载配置并创建实例
        if embedding_type == EmbeddingType.DOUBAO:
            config = DOUBAO_Embedding_Config(model=model)
            if not config.API_KEY or not config.BASE_URL or not config.MODEL:
                raise ValueError(f"豆包（DOUBAO）Embedding 的配置信息不完整或未设置。请检查数据库。")
            return DouBaoEmbedding(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)

        elif embedding_type == EmbeddingType.OPENAI:
            config = OpenAI_Embedding_Config(model=model)
            if not config.API_KEY: # 至少需要 API Key
                 raise ValueError(f"OpenAI Embedding 的配置信息不完整或未设置（缺少 API Key）。请检查数据库。")
            return OpenAIEmbedding(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)

        elif embedding_type == EmbeddingType.ONEAPI:
            config = OneAPI_Embedding_Config(model=model)
            if not config.API_KEY or not config.BASE_URL or not config.MODEL:
                 raise ValueError(f"OneAPI Embedding 的配置信息不完整或未设置。请检查数据库。")
            return OneAPIEmbedding(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)

        elif embedding_type == EmbeddingType.SILICONFLOW:
            config = SILICONFLOW_Embedding_Config(model=model)
            if not config.API_KEY or not config.BASE_URL or not config.MODEL:
                raise ValueError(f"SiliconFlow Embedding 的配置信息不完整或未设置。请检查数据库。")
            return SiliconFlowEmbedding(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)

        else:
            raise Exception("Not supported embedding type Now") 