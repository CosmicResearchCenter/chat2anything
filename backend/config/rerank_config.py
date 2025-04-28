from core.database.mysql_client import MysqlClient
from core.database.models import ReRankVendorType,ReRankModelConfig

class OLLAMA_ReRank_Config(MysqlClient):
    BASE_URL:str= ""
    MODEL:str= ""
    API_KEY:str = ""
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(ReRankModelConfig).filter(ReRankModelConfig.vendor_type == ReRankVendorType.OLLAMA,ReRankModelConfig.model == model).first()
        if info:
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            self.API_KEY = info.api_key
            return
        print("没有配置OLLAMA_Config API信息")
        return

class SILICONFLOW_ReRank_Config(MysqlClient):
    BASE_URL:str= ""
    MODEL:str= ""
    API_KEY:str = ""
    def __init__(self,model:str) -> None:
        super().__init__()
        self.getinfo(model=model)
    def __del__(self):
        super().__del__()
    def getinfo(self,model:str):
        info = self.db.query(ReRankModelConfig).filter(ReRankModelConfig.vendor_type == ReRankVendorType.SILICONFLOW,ReRankModelConfig.model == model).first()
        if info:
            self.BASE_URL = info.base_url
            self.MODEL = info.model
            self.API_KEY = info.api_key
            return
        print("没有配置SILICONFLOW_Config API信息")
        return