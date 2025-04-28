from enum import Enum
from .doubao import DouBaoLLM
from .openaillm import OpenAILLM
from .siliconflow_rerank import SiliconFlowRerankModel
from .ollama_rerank import OllamaRerankModel
from .rerank import ReRankModel
from .llm import LLM
# 导入所有需要的配置类
from config.rerank_config import (
    SILICONFLOW_ReRank_Config,
    OLLAMA_ReRank_Config,
)

class ReRank_Provider(Enum):
    """
    Types of LLM Providers.
    """
    OLLAMA = "OLLAMA"
    SILICONFLOW = "SILICONFLOW"
    @classmethod
    def get_rerank(cls, mode_provider: str):
        for member_name, member in cls.__members__.items():
            # 忽略大小写进行比较
            if member_name.upper() == mode_provider.upper():
                return member
        else:
            raise ValueError(f"不支持的 LLM 提供商类型: {mode_provider}")


class ReRank_Manager:
    def creatRerank(self, mode_provider: str,model:str) -> ReRankModel:
        try:
            reRank_Provider = ReRank_Provider.get_rerank(mode_provider)
        except ValueError as e:
            raise e # 直接抛出 get_llm 抛出的异常

        # 根据提供商类型加载并检查配置
        if reRank_Provider == ReRank_Provider.OLLAMA:
            config = OLLAMA_ReRank_Config(model=model)
            if not config.API_KEY or not config.BASE_URL or not config.MODEL:
                raise ValueError(f"OLLAMA的配置信息不完整或未设置。请检查数据库。")
            return OllamaRerankModel(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)

        elif reRank_Provider == ReRank_Provider.SILICONFLOW:
            config = SILICONFLOW_ReRank_Config(model=model)
            if not config.API_KEY: # 至少需要 API Key
                raise ValueError(f"SILICONFLOW 的配置信息不完整或未设置（缺少 API Key）。请检查数据库。")

            return SiliconFlowRerankModel(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)
        else:
            # 这个分支理论上不会执行，因为 get_llm 已经处理了无效类型
            raise Exception(f"未处理的 LLM 提供商类型: {reRank_Provider}")

if __name__ == "__main__":
    pass
