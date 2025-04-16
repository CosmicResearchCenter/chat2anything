from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, Integer, String, Text,TIMESTAMP, Boolean
import uuid

Base = declarative_base()

def generate_id(length=18):
    # 生成一个 UUID
    id_str = str(uuid.uuid4())
    # 将 UUID 前加上 'kb'
    full_id = f'kb{id_str}'
    # 截取指定长度
    return full_id[:length].replace('-', '')
class KnowledgeBase(Base):
    __tablename__ = 'knowledgeBasesList'
    id = Column(Integer, primary_key=True, autoincrement=True)
    knowledgeBaseId = Column(String(18), default=lambda: str(generate_id(length=18)))
    knowledgeBaseName 	= Column(String(255))
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
    
class ConversationsList(Base):
    __tablename__ = 'conversationsList'
    id = Column(String, primary_key=True, default=lambda: str(generate_id()))
    lastChatTime 	= Column(TIMESTAMP)
    conversationName 	= Column(String)
    num_conversation = Column(Integer)
    dataSourceName = Column(String)
    dataSourceID = Column(String)

# 知识库文档表
class KnowledgeBaseDocuments(Base):
    __tablename__ = 'knowledgeBaseDocuments'
    id = Column(String, primary_key=True, default=lambda: str(generate_id()))
    # 知识库ID
    knowledgeBaseID = Column(String)
    # 文档名
    documentName = Column(String)

# 知识库文档内容表
class KnowledgeBaseDocumentContent(Base):
    __tablename__ = 'knowledgeBaseDocumentContent'
    id = Column(String, primary_key=True, default=lambda: str(generate_id()))
    # 知识库ID
    knowledgeBaseID = Column(String)
    # 文档ID
    documentID = Column(String)
    # 文档内容
    content = Column(Text)
