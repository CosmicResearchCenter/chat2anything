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
                        DocInfo_Re,
                        SystemResources,
                        TrendData,
                        Activity,
                        ActiveUsersStats,
                        UserListItem, # 导入
                        UserDetails,  # 导入
                        UserStats     # 导入
                         )
import psutil
from typing import List,Tuple, Optional
from datetime import datetime, timedelta
import calendar
from sqlalchemy import or_, desc, asc, func # 导入 or_, desc, asc, func

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

    # 获取用户列表（增强版）
    def get_users_paginated(
        self,
        page: int = 1,
        pageSize: int = 10,
        search: Optional[str] = None,
        user_type: str = 'all', # 'all', 'admin', 'user'
        sortBy: Optional[str] = None,
        sortOrder: str = 'asc'
    ) -> Tuple[List[UserListItem], int]:
        mysql_client = MysqlClient()
        query = mysql_client.db.query(UserInfo)

        # 过滤已删除用户
        query = query.filter(UserInfo.delete_sign == False)

        # 搜索
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(UserInfo.username.like(search_term), UserInfo.email.like(search_term))
            )

        # 用户类型过滤
        if user_type == 'admin':
            query = query.filter(UserInfo.is_admin == True)
        elif user_type == 'user':
            query = query.filter(UserInfo.is_admin == False)

        # 排序
        if sortBy:
            column = getattr(UserInfo, sortBy, None)
            if column:
                if sortOrder == 'desc':
                    query = query.order_by(desc(column))
                else:
                    query = query.order_by(asc(column))
            else: # 默认按创建时间排序
                 query = query.order_by(desc(UserInfo.create_time))
        else: # 默认按创建时间排序
            query = query.order_by(desc(UserInfo.create_time))


        # 获取总数
        total = query.count()

        # 分页
        offset = (page - 1) * pageSize
        users = query.offset(offset).limit(pageSize).all()

        # 转换 Pydantic 模型
        user_list = [
            UserListItem(
                username=user.username,
                email=user.email,
                create_time=user.create_time,
                admin_sign=user.is_admin,
                status=user.status
            ) for user in users
        ]

        return user_list, total

    # 获取用户详细信息及统计
    def get_user_details(self, username: str) -> Optional[UserDetails]:
        mysql_client = MysqlClient()
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username,
            UserInfo.delete_sign == False
        ).first()

        if not user:
            return None

        # 统计对话数
        conversation_count = mysql_client.db.query(Conversation).filter(
            Conversation.username == username,
            Conversation.delete_sign == False # 仅统计未删除的对话
        ).count()

        # 统计知识库数
        knowledge_base_count = mysql_client.db.query(KnowledgeBase).filter(
            KnowledgeBase.created_by == username,
            KnowledgeBase.delete_sign == False # 仅统计未删除的知识库
        ).count()

        # 获取最后活跃时间 (基于 Chat_Messages)
        last_active_time = mysql_client.db.query(func.max(Chat_Messages.timeStamp)).filter(
            Chat_Messages.username == username
        ).scalar()

        user_stats = UserStats(
            conversationCount=conversation_count,
            knowledgeBaseCount=knowledge_base_count,
            lastActive=last_active_time
        )

        user_details = UserDetails(
            username=user.username,
            email=user.email,
            create_time=user.create_time,
            admin_sign=user.is_admin,
            status=user.status,
            stats=user_stats
        )

        return user_details

    # 更新用户状态
    def update_user_status(self, username: str, status: str, username_s: str) -> bool:
        mysql_client = MysqlClient()
        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()

        if not user:
            return False # 用户不存在

        # 防止非 admin 用户修改 admin 用户的状态
        if user.is_admin and username_s != 'admin':
             return False # 权限不足

        # 防止修改 admin 用户的状态为 disabled
        if user.username == 'admin' and status == 'disabled':
            return False # 不能禁用 admin 用户

        if status not in ['active', 'disabled']:
            return False # 无效状态

        user.status = status
        user.update_time = datetime.now()
        mysql_client.db.commit()
        mysql_client.db.refresh(user)
        return True

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
    
    # 删除用户 (修改为软删除，更新 delete_sign 和 status)
    def delete_user(self,username:str,username_s:str)->bool:
        mysql_client = MysqlClient()
        # 不能删除 admin 用户
        if username == 'admin':
            return False

        user = mysql_client.db.query(UserInfo).filter(
            UserInfo.username == username
        ).first()

        if not user:
            return False # 用户不存在

        # 不能删除其他管理员，除非操作者是 admin
        if user.is_admin == True and username_s != 'admin':
            return False # 权限不足

        # 软删除用户
        user.delete_sign = True
        user.status = 'disabled' # 同时禁用
        user.update_time = datetime.now()

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
    
    # 获取系统资源使用情况
    def get_system_resources(self) -> SystemResources:
        # 获取系统CPU使用率
        cpu_usage = psutil.cpu_percent()
        
        # 获取内存使用情况
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # 获取磁盘使用情况
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # 确定系统状态
        if cpu_usage > 90 or memory_usage > 90 or disk_usage > 90:
            status = "critical"
        elif cpu_usage > 70 or memory_usage > 70 or disk_usage > 70:
            status = "warning"
        else:
            status = "healthy"
            
        return SystemResources(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            status=status
        )
    
    # 获取用户增长趋势
    def get_user_growth(self, period: str, count: int) -> TrendData:
        mysql_client = MysqlClient()
        labels = []
        values = []
        
        today = datetime.now()
        
        if period == "day":
            # 按天统计
            for i in range(count):
                target_date = today - timedelta(days=count-i-1)
                date_str = target_date.strftime('%Y-%m-%d')
                labels.append(date_str)
                
                # 统计该日期注册的用户数量
                start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
                end_of_day = start_of_day + timedelta(days=1)
                
                user_count = mysql_client.db.query(UserInfo).filter(
                    UserInfo.create_time >= start_of_day,
                    UserInfo.create_time < end_of_day
                ).count()
                
                values.append(user_count)
                
        elif period == "month":
            # 按月统计
            for i in range(count):
                target_month = today.month - i
                target_year = today.year
                
                # 处理年份变化
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                month_name = calendar.month_name[target_month]
                labels.insert(0, f"{month_name}")
                
                # 统计该月份注册的用户数量
                start_of_month = datetime(target_year, target_month, 1, 0, 0, 0)
                if target_month == 12:
                    end_of_month = datetime(target_year + 1, 1, 1, 0, 0, 0)
                else:
                    end_of_month = datetime(target_year, target_month + 1, 1, 0, 0, 0)
                
                user_count = mysql_client.db.query(UserInfo).filter(
                    UserInfo.create_time >= start_of_month,
                    UserInfo.create_time < end_of_month
                ).count()
                
                values.insert(0, user_count)
        
        return TrendData(labels=labels, values=values)
    
    # 获取对话趋势
    def get_conversation_trend(self, period: str, count: int) -> TrendData:
        mysql_client = MysqlClient()
        labels = []
        values = []
        
        today = datetime.now()
        
        if period == "day":
            # 按天统计
            for i in range(count):
                target_date = today - timedelta(days=count-i-1)
                date_str = target_date.strftime('%Y-%m-%d')
                labels.append(date_str)
                
                # 统计该日期的对话数量
                start_of_day = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
                end_of_day = start_of_day + timedelta(days=1)
                
                conversation_count = mysql_client.db.query(Chat_Messages).filter(
                    Chat_Messages.timeStamp >= start_of_day,
                    Chat_Messages.timeStamp < end_of_day
                ).count()
                
                values.append(conversation_count)
                
        elif period == "month":
            # 按月统计
            for i in range(count):
                target_month = today.month - i
                target_year = today.year
                
                # 处理年份变化
                while target_month <= 0:
                    target_month += 12
                    target_year -= 1
                
                month_name = calendar.month_name[target_month]
                labels.insert(0, f"{month_name}")
                
                # 统计该月份的对话数量
                start_of_month = datetime(target_year, target_month, 1, 0, 0, 0)
                if target_month == 12:
                    end_of_month = datetime(target_year + 1, 1, 1, 0, 0, 0)
                else:
                    end_of_month = datetime(target_year, target_month + 1, 1, 0, 0, 0)
                
                conversation_count = mysql_client.db.query(Chat_Messages).filter(
                    Chat_Messages.timeStamp >= start_of_month,
                    Chat_Messages.timeStamp < end_of_month
                ).count()
                
                values.insert(0, conversation_count)
        
        return TrendData(labels=labels, values=values)
    
    # 获取系统最近活动
    def get_recent_activities(self, limit: int = 5) -> List[Activity]:
        mysql_client = MysqlClient()
        activities = []
        
        # 获取最近的用户注册
        recent_users = mysql_client.db.query(UserInfo).order_by(UserInfo.create_time.desc()).limit(limit).all()
        for i, user in enumerate(recent_users):
            if user.create_time is not None:
                time_diff = datetime.now() - user.create_time
                if time_diff.days > 0:
                    time_str = f"{time_diff.days}天前"
                elif time_diff.seconds // 3600 > 0:
                    time_str = f"{time_diff.seconds // 3600}小时前"
                else:
                    time_str = f"{time_diff.seconds // 60}分钟前"
            else:
                time_str = "未知时间"
                
            activities.append(Activity(
                id=i + 1,
                type="user",
                action="新用户注册",
                username=user.username,
                time=time_str
            ))
        
        # 获取最近的对话
        recent_conversations = mysql_client.db.query(Conversation).order_by(Conversation.lastChatTime.desc()).limit(limit).all()
        for i, convo in enumerate(recent_conversations):
            time_diff = datetime.now() - convo.lastChatTime
            if time_diff.days > 0:
                time_str = f"{time_diff.days}天前"
            elif time_diff.seconds // 3600 > 0:
                time_str = f"{time_diff.seconds // 3600}小时前"
            else:
                time_str = f"{time_diff.seconds // 60}分钟前"
                
            activities.append(Activity(
                id=i + len(recent_users) + 1,
                type="conversation",
                action="新增对话",
                username=convo.username,
                time=time_str
            ))
        
        # 排序并限制数量
        activities.sort(key=lambda x: x.time)
        return activities[:limit]
    
    # 获取活跃用户统计
    def get_active_users(self, period: str) -> ActiveUsersStats:
        mysql_client = MysqlClient()
        today = datetime.now()
        
        if period == "daily":
            # 获取今日活跃用户数
            start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0)
            
            # 获取当日有对话的用户数量
            active_users = mysql_client.db.query(Chat_Messages.username).distinct().filter(
                Chat_Messages.timeStamp >= start_of_day
            ).count()
            
            # 获取昨日活跃用户数
            start_of_yesterday = start_of_day - timedelta(days=1)
            previous_active = mysql_client.db.query(Chat_Messages.username).distinct().filter(
                Chat_Messages.timeStamp >= start_of_yesterday,
                Chat_Messages.timeStamp < start_of_day
            ).count()
            
        elif period == "monthly":
            # 获取当月活跃用户数
            start_of_month = datetime(today.year, today.month, 1, 0, 0, 0)
            
            # 获取当月有对话的用户数量
            active_users = mysql_client.db.query(Chat_Messages.username).distinct().filter(
                Chat_Messages.timeStamp >= start_of_month
            ).count()
            
            # 获取上月活跃用户数
            if today.month == 1:
                previous_month = datetime(today.year - 1, 12, 1, 0, 0, 0)
            else:
                previous_month = datetime(today.year, today.month - 1, 1, 0, 0, 0)
                
            previous_active = mysql_client.db.query(Chat_Messages.username).distinct().filter(
                Chat_Messages.timeStamp >= previous_month,
                Chat_Messages.timeStamp < start_of_month
            ).count()
        
        # 计算增长率
        if previous_active == 0:
            growth_rate = 100.0  # 如果上期没有活跃用户，增长率为100%
        else:
            growth_rate = ((active_users - previous_active) / previous_active) * 100
        
        return ActiveUsersStats(
            active_users=active_users,
            growth_rate=round(growth_rate, 1)
        )
    
    
if __name__ == "__main__":
    admin_service = AdminService()
