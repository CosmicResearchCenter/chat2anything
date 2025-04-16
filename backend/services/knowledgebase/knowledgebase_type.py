from pydantic import BaseModel
from typing import Dict
class CreateBaseRequest(BaseModel):
    base_name: str

class UploadFileRequest(BaseModel):
    base_id: int
    
class IndexStatusRequest(BaseModel):
    base_id: str

class DocumentSplitArgs(BaseModel):
    splitter_model: int 
    splitter_args: Dict[str, str]

class KnowledgeBaseConfig(BaseModel):
    knowledgeBaseId: str
    knowledgeBaseName: str
    rag_model: int
    is_rerank: bool