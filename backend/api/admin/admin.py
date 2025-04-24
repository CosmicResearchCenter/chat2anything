from pydantic import BaseModel
from typing import List,Any

class ResponseGenral(BaseModel):
    code: int
    message: str
    data: List[Any]
    
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