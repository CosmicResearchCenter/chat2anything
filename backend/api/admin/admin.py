from pydantic import BaseModel
from typing import List,Any, Optional
from services.admin.admin_type import UserListItem, UserDetails # 导入新的类型

class ResponseGenral(BaseModel):
    code: int
    message: str
    data: Any # 修改为 Any 以适应不同结构

class UserListResponseData(BaseModel):
    users: List[UserListItem]
    total: int

class UserListResponse(BaseModel):
    code: int
    message: str
    data: UserListResponseData

class UserDetailsResponse(BaseModel):
    code: int
    message: str
    data: UserDetails

class UpdateUserStatusRequest(BaseModel):
    status: str # 'active' or 'disabled'

class DeleteUserRequest(BaseModel):
    username: str
    
class DeleteUserConversationRequest(BaseModel):
    username: str
    conversation_id: str

class DeleteUserKnowledgeBaseRequest(BaseModel):
    username: str
    knowledge_base_id: str

class GrantAdminRequest(BaseModel):
    username: str

class RevokeAdminRequest(BaseModel):
    username: str

class UserGrowthRequest(BaseModel):
    period: str
    count: int

class ConversationTrendRequest(BaseModel):
    period: str
    count: int

class RecentActivitiesRequest(BaseModel):
    limit: int = 5

class ActiveUsersRequest(BaseModel):
    period: str

# 新增模型API配置相关模型
class LLMConfigBase(BaseModel):
    vendor_type: str
    model: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[dict] = None
    is_default_chat: Optional[bool] = False
    is_default_splitter: Optional[bool] = False

class LLMConfigCreate(LLMConfigBase):
    pass

class LLMConfigUpdate(LLMConfigBase):
    pass

class LLMConfigResponse(BaseModel):
    id: int
    vendor_type: str
    model: str
    base_url: Optional[str] = None
    api_key_masked: Optional[str] = None  # API密钥会被掩码处理
    config: Optional[dict] = None
    is_default_chat: bool
    is_default_splitter: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class LLMConfigListResponse(BaseModel):
    code: int
    message: str
    data: List[LLMConfigResponse]

# 嵌入模型配置
class EmbeddingConfigBase(BaseModel):
    vendor_type: str
    model: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[dict] = None
    is_default: Optional[bool] = False

class EmbeddingConfigCreate(EmbeddingConfigBase):
    pass

class EmbeddingConfigUpdate(EmbeddingConfigBase):
    id: int

class EmbeddingConfigResponse(BaseModel):
    id: int
    vendor_type: str
    model: str
    base_url: Optional[str] = None
    api_key_masked: Optional[str] = None  # API密钥会被掩码处理
    config: Optional[dict] = None
    is_default: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class EmbeddingConfigListResponse(BaseModel):
    code: int
    message: str
    data: List[EmbeddingConfigResponse]