from pydantic import BaseModel
from typing import List,Optional
from datetime import datetime

class SystemInfo(BaseModel):
    knowledge_base_count: int
    user_count: int
    conversation_count: int
    
    
class User(BaseModel):
    username:str
    admin_sign: bool

    
class Message(BaseModel):
    assistant: str
    message_time: Optional[str] = None
    user: str 
    
class Conversation_Collection(BaseModel):
    conversation_title: Optional[str] = None
    conversation_time: str
    conversation_id: int
    delete_sign: bool
    



class KnowledgeBaseInfo(BaseModel):
    knowledge_base_id: str
    knowledge_base_name: str
    # docs_num: int
    # words_num: int
    # related_conversations: int
    delete_sign: bool
    # create_time: str
    # update_time: str
    created_by: str
    
    create_time: datetime  # 直接使用 datetime 类型
    update_time: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()  # JSON序列化时自动转换为ISO格式
        }
    
class KnowledgeBaseItem(BaseModel):
    knowledge_base_id: str
    knowledge_base_name: str
    knowledge_base_info : KnowledgeBaseInfo
    
class DocInfo_Re(BaseModel):
    doc_id: str
    doc_name: str
    doc_type: str
    doc_size: int
    delete_sign: bool

class SystemResources(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    status: str

class TrendData(BaseModel):
    labels: List[str]
    values: List[int]

class Activity(BaseModel):
    id: int
    type: str
    action: str
    username: str
    time: str

class UserListItem(BaseModel):
    username: str
    email: Optional[str] = None
    create_time: Optional[datetime] = None
    admin_sign: bool
    status: Optional[str] = None # 修改这里，允许 None

    class Config:
        orm_mode = True # 允许从 ORM 对象创建模型实例
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }

class UserStats(BaseModel):
    conversationCount: int
    knowledgeBaseCount: int
    lastActive: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat() if dt else None
        }

class UserDetails(UserListItem):
    stats: UserStats

class ActiveUsersStats(BaseModel):
    active_users: int
    growth_rate: float