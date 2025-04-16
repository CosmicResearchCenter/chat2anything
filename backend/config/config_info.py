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
    
    MYSQL_IP:str
    MYSQL_PORT:str
    MYSQL_BASE:str
    MYSQL_USER:str
    MYSQL_PASSWORD:str

    EMBEEDING_BASE_URL:str
    EMBEEDING_API_KEY:str
    EMBEDDING_MODEL_PROVIDER :str 
    LLM_PROVIDER :str
    # 0 1
    SPPLITTER_MODEL :int

    # ES_BASE_URL
    ES_BASE_URL :str 
    ES_BASE_PORT :int 

    # Milvus Host
    MILVUS_HOST :str 
    MILVUS_PORT :int 

    OCR_PORT :int 
    OCR_URL :str 

    RERANK_BASE_URL:str
    
    ONEAPI_BASE_URL:str
    ONEAPI_API_KEY:str
    ONEAPI_MODEL:str
    ONEAPI_EMBEDDING_MODEL:str
    
    OPENAI_API_KEY:str
    OPENAI_BASE_URL:str
    OPENAI_MODEL:str
    OPENAI_EMBEDDING_MODEL:str

    ZHIPUAI_API_KEY:str
    ZHIPUAI_MODEL: str

    SPARKAI_APP_ID:str
    SPARKAI_API_SECRET:str
    SPARKAI_API_KEY:str
    SPARKAI_DOMAIN:str
    SPARKAI_BASE_URL:str

    DOUBAOAI_API_KEY:str
    DOUBAOAI_BASE_URL:str
    DOUBAOAI_MODEL:str
    DOUBAOAI_EMBEDDING_MODEL:str

    OLLAMA_MODEL :str
    OLLAMA_BASE_URL:str
    
    SILICONFLOW_API_KEY:str
    SILICONFLOW_BASE_URL:str
    SILICONFLOW_MODEL:str  # 或其他可用模型
    SILICONFLOW_EMBEDDING_MODEL:str
     
    class Config:
        env_file = ".env"
        extra = 'allow'

    # 文档存放路径
    DOCS_PATH:str = "documents_stored"



settings = Settings()

#print(settings.MYSQL_IP)