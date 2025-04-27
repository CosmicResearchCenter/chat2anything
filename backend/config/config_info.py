from pydantic_settings import BaseSettings
from config.splitter_model import SplitterModel
from pathlib import Path
SPPLITTER_MODEL = SplitterModel.LLMSplitter
from pydantic import model_validator
import os


class Settings(BaseSettings):
    @model_validator(mode='after')
    def setup_docs_path(self):
        BASE_DIR = Path(__file__).resolve().parent.parent
        self.DOCS_PATH = str(BASE_DIR / self.DOCS_PATH)
        if not os.path.exists(self.DOCS_PATH):
            os.makedirs(self.DOCS_PATH)
        return self
    SECRET_KEY:str
    
    ADMIN_KEY:str
    
    MYSQL_IP:str
    MYSQL_PORT:str
    MYSQL_BASE:str
    MYSQL_USER:str
    MYSQL_PASSWORD:str

    SPPLITTER_MODEL :int

    # ES_BASE_URL
    ES_BASE_URL :str 
    ES_BASE_PORT :int 

    # Milvus Host
    MILVUS_HOST :str 
    MILVUS_PORT :int 

    RERANK_BASE_URL:str
     
    class Config:
        env_file = ".env"
        extra = 'allow'

    # 文档存放路径
    DOCS_PATH:str = "documents_stored"



settings = Settings()

#print(settings.MYSQL_IP)