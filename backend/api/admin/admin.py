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

# Rerank模型配置
class ReRankConfigBase(BaseModel):
    vendor_type: str
    model: str
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    config: Optional[dict] = None
    is_default: Optional[bool] = False

class ReRankConfigCreate(ReRankConfigBase):
    pass

class ReRankConfigUpdate(ReRankConfigBase):
    pass

class ReRankConfigResponse(BaseModel):
    id: int
    vendor_type: str
    model: str
    base_url: Optional[str] = None
    api_key_masked: Optional[str] = None  # API密钥会被掩码处理
    config: Optional[dict] = None
    is_default: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ReRankConfigListResponse(BaseModel):
    code: int
    message: str
    data: List[ReRankConfigResponse]

# 邀请码相关模型
class InviteCodeCreate(BaseModel):
    max_uses: Optional[int] = 1
    expire_hours: Optional[int] = None  # 过期小时数，None表示永不过期
    description: Optional[str] = None

class InviteCodeResponse(BaseModel):
    id: int
    code: str
    created_by: str
    created_at: str
    used_by: Optional[str] = None
    used_at: Optional[str] = None
    is_used: bool
    is_active: bool
    expire_at: Optional[str] = None
    max_uses: int
    current_uses: int
    description: Optional[str] = None

class InviteCodeListResponse(BaseModel):
    code: int
    message: str
    data: List[InviteCodeResponse]

class InviteCodeUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    description: Optional[str] = None
    max_uses: Optional[int] = None