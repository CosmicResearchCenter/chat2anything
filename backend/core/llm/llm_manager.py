from enum import Enum
from .doubao import DouBaoLLM
from .openaillm import OpenAILLM
from .zhipuai_llm import ZhiPuAI_LLM
from .sparkai_llm import SparkAILLM
from .openapi_llm import OneApiLLM
from .siliconflow import SiliconFlowLLM
from .llm import LLM
# 导入所有需要的配置类
from config.llm_config import (
    LLM_Settings,
    DouBaoAI_Config,
    OpenAI_Config,
    ZhiPuAI_Config,
    SparkAI_Config,
    OneAPI_Config,
    SILICONFLOW_Config
)

class LLM_Provider(Enum):
    """
    Types of LLM Providers.
    """
    OPENAI = "OPENAI"
    DOUBAO = "DOUBAO"
    ZHIPUAI = "ZHIPUAI"
    SPARKAI = "SPARKAI"
    ONEAPI = "ONEAPI"
    SILICONFLOW = "SILICONFLOW"
    @classmethod
    def get_llm(cls, mode_provider: str):
        for member_name, member in cls.__members__.items():
            # 忽略大小写进行比较
            if member_name.upper() == mode_provider.upper():
                return member
        else:
            raise ValueError(f"不支持的 LLM 提供商类型: {mode_provider}")


class LLM_Manager:
    def creatLLM(self, mode_provider: str) -> LLM:
        try:
            lLM_Provider = LLM_Provider.get_llm(mode_provider)
        except ValueError as e:
            raise e # 直接抛出 get_llm 抛出的异常

        # 根据提供商类型加载并检查配置
        if lLM_Provider == LLM_Provider.DOUBAO:
            config = DouBaoAI_Config()
            if not config.API_KEY or not config.BASE_URL or not config.MODEL:
                raise ValueError(f"豆包（DOUBAO）的配置信息不完整或未设置。请检查数据库。")
            return DouBaoLLM(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)

        elif lLM_Provider == LLM_Provider.OPENAI:
            config = OpenAI_Config()
            if not config.API_KEY: # 至少需要 API Key
                raise ValueError(f"OpenAI 的配置信息不完整或未设置（缺少 API Key）。请检查数据库。")

            return OpenAILLM(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)

        elif lLM_Provider == LLM_Provider.ZHIPUAI:
            config = ZhiPuAI_Config()
            if not config.API_KEY or not config.MODEL:
                raise ValueError(f"智谱AI（ZHIPUAI）的配置信息不完整或未设置。请检查数据库。")
            return ZhiPuAI_LLM(api_key=config.API_KEY, model=config.MODEL)

        elif lLM_Provider == LLM_Provider.SPARKAI:
            config = SparkAI_Config()
            if not config.APP_ID or not config.API_SECRET or not config.API_KEY or not config.BASE_URL or not config.DOMAIN:
                raise ValueError(f"讯飞星火（SPARKAI）的配置信息不完整或未设置。请检查数据库。")
            return SparkAILLM(app_id=config.APP_ID, api_secret=config.API_SECRET, api_key=config.API_KEY, base_url=config.BASE_URL, domain=config.DOMAIN)

        elif lLM_Provider == LLM_Provider.ONEAPI:
            config = OneAPI_Config()
            if not config.API_KEY or not config.BASE_URL or not config.MODEL:
                 raise ValueError(f"OneAPI 的配置信息不完整或未设置。请检查数据库。")
            return OneApiLLM(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)

        elif lLM_Provider == LLM_Provider.SILICONFLOW:
            config = SILICONFLOW_Config()
            if not config.API_KEY or not config.BASE_URL or not config.MODEL:
                raise ValueError(f"SiliconFlow 的配置信息不完整或未设置。请检查数据库。")
            return SiliconFlowLLM(api_key=config.API_KEY, base_url=config.BASE_URL, model=config.MODEL)
        else:
            # 这个分支理论上不会执行，因为 get_llm 已经处理了无效类型
            raise Exception(f"未处理的 LLM 提供商类型: {lLM_Provider}")

if __name__ == "__main__":
    try:
        # 测试一个可能没有配置的提供商
        # llm = LLM_Manager().creatLLM("OPENAI")
        # llm = LLM_Manager().creatLLM("DOUBAO")
        llm = LLM_Manager().creatLLM("INVALID_PROVIDER") # 测试无效提供商
        llm.setPrompt("你是一个聊天助手")
        print(llm.ChatToBot("你好"))
    except ValueError as e:
        print(f"创建 LLM 时出错: {e}")
    except Exception as e:
        print(f"发生意外错误: {e}")
