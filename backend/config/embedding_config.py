from core.database.mysql_client import MysqlClient
from core.database.models import EmbeddingModelConfig,EmbeddingVendorType

class DOUBAO_Embedding_Config(MysqlClient):
    BASE_URL:str= ""
    MODEL:str= ""
    API_KEY:str = ""
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(EmbeddingModelConfig).filter(EmbeddingModelConfig.vendor_type == EmbeddingVendorType.DOUBAOAI,EmbeddingModelConfig.model == model).first()
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
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(EmbeddingModelConfig).filter(EmbeddingModelConfig.vendor_type == EmbeddingVendorType.OPENAI,EmbeddingModelConfig.model == model).first()
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
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(EmbeddingModelConfig).filter(EmbeddingModelConfig.vendor_type == EmbeddingVendorType.ONEAPI,EmbeddingModelConfig.model == model).first()
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
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(EmbeddingModelConfig).filter(EmbeddingModelConfig.vendor_type == EmbeddingVendorType.SILICONFLOW,EmbeddingModelConfig.model == model).first()
        if info:
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            self.API_KEY = info.api_key
            return
        print("没有配置SILICONFLOW_Config API信息")
        return