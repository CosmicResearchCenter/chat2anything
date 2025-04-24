from core.rag.rag_pipeline import RAG_Pipeline
from core.database.mysql_client import MysqlClient
from core.database.models import KnowledgeBase,UserInfo,Chat_Messages,Conversation,DocInfo
from core.rag.database.milvus.milvus_client import MilvusCollectionManager
from core.rag.database.elasticsearch.elastic_client import ElasticClient
from .admin_type import (SystemInfo,
                        Conversation_Collection,
                        Message,
                        KnowledgeBaseItem,
                        KnowledgeBaseInfo,
                        User,
                        DocInfo_Re
                         )
from typing import List,Tuple
from datetime import datetime
class AdminService:
    def __init__(self):
        pass
    
    # 获取系统基本信息
    def get_system_info(self)->SystemInfo:
        mysql_client = MysqlClient()
        # 获取知识库、用户、对话数量
        knowledge_base_count = mysql_client.db.query(KnowledgeBase).count()
        user_count = mysql_client.db.query(UserInfo).count()
        conversation_count = mysql_client.db.query(Conversation).count()
        
        return SystemInfo(
            knowledge_base_count=knowledge_base_count,
            user_count=user_count,
            conversation_count=conversation_count
        )
    # 获取所有用户
    def get_all_users(self)->List[User]:
        mysql_client = MysqlClient()
        users = mysql_client.db.query(UserInfo).all()
        user_list: List[User] = []
        for user in users:
            user_list.append(User(
                username=user.username,
                admin_sign=user.is_admin
            ))
        return user_list
    
    # 根据用户对话列表
    def get_user_conversation(self,username:str,s_username:str)->List[Conversation_Collection]:
        mysql_client = MysqlClient()
        
        if s_username == 'admin' or s_username == username:
            # 获取用户对话
            conversations = mysql_client.db.query(Conversation).filter(
                Conversation.username == username
            ).all()
            user_conversation_list: List[Conversation_Collection] = []
            for conversation in conversations:
                user_conversation_list.append(Conversation_Collection(
                    conversation_title=conversation.conversationName,
                    conversation_time=str(conversation.lastChatTime),
                    conversation_id=conversation.id,
                    delete_sign=conversation.delete_sign
                ))
        else:
            # 不能返回管理员的对话
            user_conversation_list = []
            # 获取当前请求用户信息
            current_user = mysql_client.db.query(UserInfo).filter(
                UserInfo.username == username
            ).first()
            if current_user and current_user.is_admin:
                return []
            else:
                # 获取用户对话
                conversations = mysql_client.db.query(Conversation).filter(
                    Conversation.username == username
                ).all()
                for conversation in conversations:
                    user_conversation_list.append(Conversation_Collection(
                        conversation_title=conversation.conversationName,
                        conversation_time=str(conversation.lastChatTime),
                        conversation_id=conversation.id,
                        delete_sign=conversation.delete_sign
                    ))

        return user_conversation_list
    
    # 根据对话id获取对话内容
    def get_conversation_content(self,conversation_id:int,s_username:str)->List[Message]:
        mysql_client = MysqlClient()
        # 获取对话内容
        messages = mysql_client.db.query(Chat_Messages).filter(
            Chat_Messages.conversationID == conversation_id
        ).all()
        message_list: List[Message] = []
        for message in messages:
            message_list.append(Message(
                assistant=message.answer,
                message_time=str(message.timeStamp),  # 将 datetime 转换为字符串
                user=message.query
            ))
        return message_list
    
    # 根据用户获取知识库列表
    def get_user_knowledge_base(self,username:str,s_username:str)->List[KnowledgeBaseItem]:
        mysql_client = MysqlClient()
        if s_username == 'admin' or s_username == username:
            # 获取用户知识库
            knowledge_bases = mysql_client.db.query(KnowledgeBase).filter(
                KnowledgeBase.created_by == username
            ).all()
            knowledge_base_list: List[KnowledgeBaseItem] = []
            for knowledge_base in knowledge_bases:
                knowledge_base_list.append(KnowledgeBaseItem(
                    knowledge_base_id=knowledge_base.knowledgeBaseId,
                    knowledge_base_name=knowledge_base.knowledgeBaseName,
                    knowledge_base_info=KnowledgeBaseInfo(
                        knowledge_base_id=knowledge_base.knowledgeBaseId,
                        knowledge_base_name=knowledge_base.knowledgeBaseName,
                        # docs_num=0,
                        # words_num=0,
                        # related_conversations=0,
                        delete_sign=knowledge_base.delete_sign,
                        create_time=knowledge_base.create_time,
                        update_time=knowledge_base.update_time,
                        created_by=knowledge_base.created_by
                    )
                ))
        else:
            # 不能返回管理员的知识库
            knowledge_base_list = []
            # 获取当前请求用户信息
            current_user = mysql_client.db.query(UserInfo).filter(
                UserInfo.username == username
            ).first()
            if current_user.is_admin:
                return []
            else:
                # 获取用户知识库
                knowledge_bases = mysql_client.db.query(KnowledgeBase).filter(
                    KnowledgeBase.created_by == username
                ).all()
                for knowledge_base in knowledge_bases:
                    knowledge_base_list.append(KnowledgeBaseItem(
                        knowledge_base_id=knowledge_base.knowledgeBaseId,
                        knowledge_base_name=knowledge_base.knowledgeBaseName,
                        knowledge_base_info=KnowledgeBaseInfo(
                            knowledge_base_id=knowledge_base.knowledgeBaseId,
                            knowledge_base_name=knowledge_base.knowledgeBaseName,
                            # docs_num=knowledge_base.docs_num,
                            # words_num=knowledge_base.words_num,
                            # related_conversations=knowledge_base.related_conversations,
                            delete_sign=knowledge_base.delete_sign,
                            create_time=knowledge_base.create_time,
                            update_time=knowledge_base.update_time,
                            created_by=knowledge_base.created_by
                        )
                    ))
        return knowledge_base_list
    def get_knowledge_base(self,username:str,knowledge_base_id:str,username_s:str)->List[DocInfo_Re]:
        
        mysql_client = MysqlClient()
        if username_s == 'admin' or username_s == username:
            # 获取知识库文档
            knowledge_base = mysql_client.db.query(KnowledgeBase).filter(
                KnowledgeBase.created_by == username,
                KnowledgeBase.knowledgeBaseId == knowledge_base_id
            ).first()
            
            docs = mysql_client.db.query(DocInfo).filter(
                DocInfo.knowledgeBaseId == knowledge_base_id
            ).all()
            
            doc_list: List[DocInfo_Re] = []
            for doc in docs:
                doc_list.append(DocInfo_Re(
                    doc_id=doc.save_id,
                    doc_name=doc.doc_name,
                    doc_type=doc.doc_type,
                    doc_size=doc.doc_size,
                    delete_sign=doc.delete_sign
                ))
                
        else:
            # 不能返回管理员的知识库
            doc_list = []
            # 获取当前请求用户信息
            current_user = mysql_client.db.query(UserInfo).filter(
                UserInfo.username == username
            ).first()
            if current_user.is_admin:
                return []
            else:
                # 获取知识库文档
                knowledge_base = mysql_client.db.query(KnowledgeBase).filter(
                    KnowledgeBase.created_by == username,
                    KnowledgeBase.knowledgeBaseId == knowledge_base_id
                ).first()
                
                docs = mysql_client.db.query(DocInfo).filter(
                    DocInfo.knowledgeBaseId == knowledge_base_id
                ).all()
                
                for doc in docs:
                    doc_list.append(DocInfo_Re(
                        doc_id=doc.save_id,
                        doc_name=doc.doc_name,
                        doc_type=doc.doc_type,
                        doc_size=doc.doc_size,
                        delete_sign=doc.delete_sign,
                        retriever_num=doc.retriever_num
                    ))
        return doc_list
        
    # 删除用户对话
    def delete_user_conversation(self,username:str,conversation_id:int,username_s:str)->bool:
        mysql_client = MysqlClient()
        
        # 不能删除管理员的对话  
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()
            
        if user.is_admin == True and username_s != 'admin': 
            return False
        
        # 删除对话
        conversation = mysql_client.db.query(Conversation).filter(
            Conversation.username == username,
            Conversation.id == conversation_id
        ).first()
        
        conversation.delete_sign = True
        
        mysql_client.db.commit()
        
        mysql_client.db.refresh(conversation)
        
        return True


    # 删除用户知识库
    def delete_user_knowledge_base(self,username:str,knowledge_base_id:str,username_s)->bool:
        mysql_client = MysqlClient()
        # 不能删除管理员的知识库
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()
        if user.is_admin == True and username_s != 'admin':
            return False
        # 删除知识库
        knowledge_base = mysql_client.db.query(KnowledgeBase).filter(
            KnowledgeBase.created_by == username,
            KnowledgeBase.knowledgeBaseId == knowledge_base_id
        ).first()
        
        knowledge_base.delete_sign = True
        
        mysql_client.db.commit()
        mysql_client.db.refresh(knowledge_base)
        
        try:
            milvus_client = MilvusCollectionManager()
            milvus_client.drop_collection(knowledge_base_id)
        except Exception as e:
            print(e)
        
        try:
            elastic_client = ElasticClient()
            elastic_client.delete_index(knowledge_base_id)
        except Exception as e:
            print(e)
        
        return True
    
    # 删除用户
    def delete_user(self,username:str,username_s:str)->bool:
        mysql_client = MysqlClient()
        # 不能删除管理员
        
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()
        if user.is_admin == True and username_s != 'admin':
            return False
        # 删除用户
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()
        
        user.delete_sign = True
        
        mysql_client.db.commit()
        mysql_client.db.refresh(user)
        
        return True
    
    # 授予用户管理员权限
    def grant_user_admin(self,username:str,username_s)->bool:
        mysql_client = MysqlClient()
        # 授予用户管理员权限
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()
        user.is_admin = True
        mysql_client.db.commit()
        return True
    
    # 撤销用户管理员权限
    def revoke_user_admin(self,username:str,username_s)->bool:
        mysql_client = MysqlClient()
        # 管理员不能撤销管理员权限
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()
        if user.username == 'admin' and username_s != 'admin':
            return False
        # 撤销用户管理员权限
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()
        if user.username == 'admin':
            return False
        
        if user.is_admin:
            user.is_admin = False
        
        mysql_client.db.commit()
        
        mysql_client.db.refresh(user)
        
        return True
    
    
if __name__ == "__main__":
    admin_service = AdminService()
