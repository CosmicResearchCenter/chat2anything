from pydantic import BaseModel
from typing import List, Optional,Dict,Any
from core.rag.models.knolwedge_base import ResultByDoc
from services.chat.chat_type import ChatMessageHistory
# Chat message request
class ChatMessageRequest(BaseModel):
    streaming: bool
    conversation_id: str
    message: str

# Chat message history response
class ChatMessageHistoryResponse(BaseModel):
    code: int
    data: List[ChatMessageHistory]
    message: str

class ChatMessageResponse(BaseModel):
    code: int
    data: List[Any]
    message: str
class ChatConversationResponse(BaseModel):
    code: int
    data: List[Any]
    message: str

class ConversationCreateRequest(BaseModel):
    knowledge_base_id: str

class ConversationCreateResponse(BaseModel):
    code: int
    data: Optional[dict]
    message: str

# Knowledge base selection request
class KnowledgeBaseSelectRequest(BaseModel):
    conversation_id: str
    knowledge_base_id: str

# Knowledge base selection response
class KnowledgeBaseSelectResponse(BaseModel):
    code: int
    data: List[Any]
    message: str

# Clear chat request
class ChatClearRequest(BaseModel):
    conversation_id: str

# Clear chat response
class ChatClearResponse(BaseModel):
    code: int
    data: List[Any]
    message: str

# Create knowledge base request
class CreateKnowledgeBaseRequest(BaseModel):
    name: str

# Create knowledge base response
class CreateKnowledgeBaseResponse(BaseModel):
    code: int
    data: List[Optional[dict]]
    message: str

# Knowledge base list response
class KnowledgeBaseListResponse(BaseModel):
    code: int
    data: List[Optional[dict]]
    message: str

# Knowledge base details response
class KnowledgeBaseDetailResponse(BaseModel):
    code: int
    data: List[Optional[dict]]
    message: str

# Upload file request
class UploadFileRequest(BaseModel):
    file: str

# Upload file response
class UploadFileResponse(BaseModel):
    code: int
    data: List[Optional[dict]]
    message: str

# File index status response
class FileIndexStatusResponse(BaseModel):
    code: int
    data: List[Optional[dict]]
    message: str

class DeleteConversationResponse(BaseModel):
    code: int
    data: Optional[dict]
    message: str

class ReNameRequest(BaseModel):
    conversation_id: str
    new_name: str

class ReNameResponse(BaseModel):
    code: int
    data: Optional[dict]
    message: str

class ConversationTitleCreateRequest(BaseModel):
    conversation_id: str

class ConversationTitleCreateResponse(BaseModel):
    code: int
    data: Optional[Any]
    message: str