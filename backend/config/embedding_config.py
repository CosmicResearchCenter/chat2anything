from core.database.mysql_client import MysqlClient
from core.database.models import LLMProviderConfig,EmbeddingVendorType

class DOUBAO_Embedding_Config(MysqlClient):
    BASE_URL:str= ""
    MODEL:str= ""
    API_KEY:str = ""
    def __init__(self) -> None:
        super().__init__()
        self.getinfo()
    def __del__(self):
        super().__del__()
    def getinfo(self):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == EmbeddingVendorType.DOUBAOAI).first()
        if info:
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            self.API_KEY = info.api_key
            return
        print("没有配置SILICONFLOW_Config API信息")
        return

class OpenAI_Embedding_Config(MysqlClient):
    BASE_URL:str= ""
    MODEL:str= ""
    API_KEY:str = ""
    def __init__(self) -> None:
        super().__init__()
        self.getinfo()
    def __del__(self):
        super().__del__()
    def getinfo(self):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == EmbeddingVendorType.OPENAI).first()
        if info:
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            self.API_KEY = info.api_key
            return
        print("没有配置SILICONFLOW_Config API信息")
        return
class OneAPI_Embedding_Config(MysqlClient):
    BASE_URL:str= ""
    MODEL:str= ""
    API_KEY:str = ""
    def __init__(self) -> None:
        super().__init__()
        self.getinfo()
    def __del__(self):
        super().__del__()
    def getinfo(self):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == EmbeddingVendorType.ONEAPI).first()
        if info:
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            self.API_KEY = info.api_key
            return
        print("没有配置SILICONFLOW_Config API信息")
        return
class SILICONFLOW_Embedding_Config(MysqlClient):
    BASE_URL:str= ""
    MODEL:str= ""
    API_KEY:str = ""
    def __init__(self) -> None:
        super().__init__()
        self.getinfo()
    def __del__(self):
        super().__del__()
    def getinfo(self):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == EmbeddingVendorType.SILICONFLOW).first()
        if info:
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            self.API_KEY = info.api_key
            return
        print("没有配置SILICONFLOW_Config API信息")
        return