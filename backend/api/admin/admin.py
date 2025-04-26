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