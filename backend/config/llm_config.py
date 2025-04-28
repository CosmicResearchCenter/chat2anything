from core.database.mysql_client import MysqlClient
from core.database.models import LLMProviderConfig,LLMVendorType

class OLLAMA_Config(MysqlClient):
    BASE_URL:str= ""
    MODEL:str= ""

    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == LLMVendorType.OLLAMA,LLMProviderConfig.model == model).first()
        if info:
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            return
        print("没有配置 OLLAMA API 信息") # Updated print message
        return

class SILICONFLOW_Config(MysqlClient):
    API_KEY:str = ""
    BASE_URL:str= ""
    MODEL:str= ""

    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == LLMVendorType.SILICONFLOW,LLMProviderConfig.model == model).first()
        if info:
            self.API_KEY = info.api_key
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            return
        print("没有配置 SILICONFLOW API 信息") # Updated print message
        return

class OneAPI_Config(MysqlClient):
    API_KEY:str = ""
    BASE_URL:str= ""
    MODEL:str= ""

    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == LLMVendorType.ONEAPI,LLMProviderConfig.model == model).first()
        if info:
            self.API_KEY = info.api_key
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            return
        print("没有配置 OneAPI API 信息")
        return

class OpenAI_Config(MysqlClient):
    API_KEY:str = ""
    BASE_URL:str= ""
    MODEL:str= ""

    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == LLMVendorType.OPENAI,LLMProviderConfig.model == model).first()
        if info:
            self.API_KEY = info.api_key
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            return
        print("没有配置 OPENAI API 信息")
        return


class ZhiPuAI_Config(MysqlClient):
    API_KEY:str= ""
    MODEL:str= ""
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    # Removed __del__ as it only called super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == LLMVendorType.ZHIPUAI,LLMProviderConfig.model == model).first()
        if info:
            self.API_KEY = info.api_key
            self.MODEL = info.model
            return
        print("没有配置 ZHIPUAI API 信息")
        return

class SparkAI_Config(MysqlClient):
    APP_ID:str= ""
    API_SECRET:str= ""
    API_KEY:str= ""
    BASE_URL:str= ""
    DOMAIN:str= ""
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == LLMVendorType.SPARKAI,LLMProviderConfig.model == model).first()
        if info and info.config: # Check if info and info.config exist
            self.API_KEY = info.api_key
            self.APP_ID = info.config.get('APP_ID', '') # Use .get for safety
            self.API_SECRET = info.config.get('API_SECRET', '') # Use .get for safety
            self.BASE_URL = info.base_url
            self.DOMAIN = info.config.get('DOMAIN', '') # Use .get for safety
            return
        print("没有配置 SPARKAI API 信息或配置不完整") # Updated print message
        return

class DouBaoAI_Config(MysqlClient):
    API_KEY:str= ""
    BASE_URL:str= ""
    MODEL:str= ""
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(LLMProviderConfig).filter(LLMProviderConfig.vendor_type == LLMVendorType.DOUBAOAI,LLMProviderConfig.model == model).first()
        if info:
            self.API_KEY = info.api_key
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            return
        print("没有配置 DOUBAOAI API 信息")
        return