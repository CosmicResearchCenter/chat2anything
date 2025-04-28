from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer, String, Text,TIMESTAMP,Boolean, DateTime, JSON
from sqlalchemy.dialects.mysql import ENUM as SQLEnum
import uuid
from .mysql_client import Base
from enum import Enum
from datetime import datetime
import json
def generate_id(length=18):
    # 生成一个 UUID
    id_str = str(uuid.uuid4())
    # 将 UUID 前加上 'kb'
    full_id = f'kb{id_str}'
    # 截取指定长度
    return full_id[:length].replace('-', '')

def generate_general_id(length=18):
    # 生成一个 UUID
    id_str = str(uuid.uuid4())
    # 将 UUID 前加上 'kb'
    full_id = f'uu{id_str}'
    # 截取指定长度
    return full_id[:length].replace('-', '')

class KnowledgeBase(Base):
    __tablename__ = 'knowledgeBasesList'
    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledgeBaseId = Column(String(18), default=lambda: str(generate_id(length=18)))
    knowledgeBaseName 	= Column(String(255))
    is_public = Column(Boolean, default=False)
    # docs_num = Column(Integer, default=0)
    # words_num = Column(Integer, default=0)
    # related_conversations = Column(Integer, default=0)
    delete_sign = Column(Boolean, default=False)
    create_time = Column(TIMESTAMP)
    update_time = Column(TIMESTAMP)
    # 创建者
    created_by = Column(String(255))
    def to_dict(self):
        return {
            "id": self.knowledgeBaseId,
            # "docs_num": self.docs_num,
            # "words_num": self.words_num,
            # "related_conversations": self.related_conversations,
            "knowledgeBaseName": self.knowledgeBaseName
        }

# 对话列表
class Conversation(Base):
    __tablename__ = 'conversationsList'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lastChatTime 	= Column(TIMESTAMP, nullable=False)
    conversationName 	= Column(String(255))
    num_conversation = Column(Integer)
    knowledgeBaseId = Column(String(255))
    username = Column(String(255))
    delete_sign = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "conversation_id": self.id,
            "lastChatTime": self.lastChatTime,
            "conversationName": self.conversationName,
            "num_conversation": self.num_conversation,
            "knowledgeBaseId": self.knowledgeBaseId,
            "username": self.username
        }
class Chat_Messages (Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversationID = Column(String(255))
    timeStamp = Column(TIMESTAMP)
    query = Column(String(255))
    answer = Column(Text)
    username = Column(String(255)) # 存储用户 ID
    knowledgeBaseId = Column(String(255)) # 存储知识库 ID

class RetrieverDoc(Base):
    __tablename__ = 'retrieverDocs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text)
    knowledge_doc_name = Column(String(255))
    knowledgeBaseId = Column(String(255))
    messageId = Column(String(255))

# 文档信息
class DocInfo(Base):
    __tablename__ = 'docsInfo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_name = Column(String(255))
    knowledgeBaseId = Column(String(255))
    
    # 召回次数
    # retriever_num = Column(Integer, default=0)
    
    create_time = Column(TIMESTAMP)
    doc_type = Column(String(255))
    doc_size = Column(Integer)
    save_id = Column(String(255))
    delete_sign = Column(Boolean, default=False)

class DocIndexStatus(Base):
    __tablename__ = 'docIndexStatus'
    id = Column(String(255), primary_key=True, default=lambda: str(generate_general_id(length=18)))
    index_status = Column(Integer)
    knowledgeBaseId = Column(String(255))
    doc_id = Column(String(255))

    def to_dict(self):
        return {
            "index_status": self.index_status,
            "knowledgeBaseId": self.knowledgeBaseId,
            "doc_id": self.doc_id
        }

# 知识库配置信息
class KnowledgeConfig(Base):
    __tablename__ = 'knowledgeConfig'
    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledgeBaseId = Column(String(255))
    rag_model = Column(Integer) # 0: 混合检索 1:向量检索 2:文档检索
    is_rerank = Column(Boolean, default=False)
    create_time = Column(TIMESTAMP)
    update_time = Column(TIMESTAMP)

    def to_dict(self):
        return {
            "knowledgeBaseId": self.knowledgeBaseId,
            "config": self.rag_model,
            "create_time": self.create_time,
            "update_time": self.update_time
        }

# 用户信息
class UserInfo(Base):
    __tablename__ = 'userInfo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # userId = Column(String(18), default=lambda: str(generate_general_id(length=18)), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    email = Column(String(100), unique=True, index=True)
    create_time = Column(TIMESTAMP)
    update_time = Column(TIMESTAMP)
    delete_sign = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    status = Column(String(20), default='active') # 新增 status 字段，默认为 active

class LLMVendorType(str, Enum):
    OPENAI = "OPENAI"
    ONEAPI = "ONEAPI"
    ZHIPUAI = "ZHIPUAI"
    SPARKAI = "SPARKAI"
    DOUBAOAI = "DOUBAOAI"
    OLLAMA = "OLLAMA"
    SILICONFLOW = "SILICONFLOW"

class LLMProviderConfig(Base):
    __tablename__ = 'llm_provider_configs'

    id = Column(Integer, primary_key=True)
    vendor_type = Column(SQLEnum(LLMVendorType), nullable=False)
    config = Column(JSON, nullable=True)  # 存储厂商专属配置
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_default_chat = Column(Boolean, default=False, nullable=False) # 新增：标记是否为默认配置
    is_default_splitter = Column(Boolean, default=False, nullable=False) # 新增：标记是否为默认配置
    # 通用字段（可选）
    base_url = Column(String, nullable=True)  # 多个厂商共用
    api_key = Column(String, nullable=True)  # 多个厂商共用
    model = Column(String, nullable=True)    # 多个厂商共用

class EmbeddingVendorType(str, Enum):
    OPENAI = "OPENAI"
    ONEAPI = "ONEAPI"
    ZHIPUAI = "ZHIPUAI"
    DOUBAOAI = "DOUBAOAI"
    SILICONFLOW = "SILICONFLOW"

class EmbeddingModelConfig(Base):
    __tablename__ = 'embedding_model_configs'

    id = Column(Integer, primary_key=True)
    vendor_type = Column(SQLEnum(EmbeddingVendorType), nullable=False)
    config = Column(JSON, nullable=False)  # 存储厂商专属配置
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_default = Column(Boolean, default=False, nullable=False) # 新增：标记是否为默认配置

    # 通用字段（可选）
    base_url = Column(String, nullable=True)  # 多个厂商共用
    api_key = Column(String, nullable=True)  # 多个厂商共用
    model = Column(String, nullable=True)    # 多个厂商共用