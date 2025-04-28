from core.llm import LLM,LLM_Manager
from core.database.mysql_client import MysqlClient
from core.database.models import Conversation,KnowledgeBase,Chat_Messages,RetrieverDoc 
from api.chat.chat_models import ChatMessageRequest,LLMConfig
from core.rag.rag_pipeline import RAG_Pipeline
from core.rag.models.knolwedge_base import ResultByDoc
from services.chat.chat_type import ChatMessageHistory,RetrieverDoc as RetrieverDocs
from core.llm.llm_manager import LLM_Manager
from config.config_info import settings
from services.knowledgebase.knowledgebase_service import KBase
from fastapi import HTTPException
import datetime
from typing import List
from core.utils.utils import GetDeafultLLM,GetDefaultEmbedding
class Chat:
    def __init__(self, conversation_id,user_id,rag:RAG_Pipeline,llm_config:LLMConfig,embedding_config):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.mysql_session = MysqlClient().SessionLocal()
        self.rag:RAG_Pipeline  = rag
        self.llm_config:LLMConfig = llm_config
        self.default_llm_config = GetDeafultLLM()
        self.default_embedding_config = GetDefaultEmbedding()
    def __del__(self):
        self.mysql_session.close()
    #创建对话
    def create_conversation(self,knowledgeBaseId:str,username)->Conversation:
        try:
            new_conversation = Conversation(num_conversation=0,knowledgeBaseId=knowledgeBaseId,username=username,conversationName="New Conversation",lastChatTime=datetime.datetime.now())                 
            self.mysql_session.add(new_conversation)
            self.mysql_session.commit()
            self.mysql_session.refresh(new_conversation)
            # print("Conversation created successfully")
            return new_conversation
        except Exception as e:
            print(e)
    
    
    #匹配对话
    def match_conversations(self, conversation_id,username)->Conversation:
        conversation = self.mysql_session.query(Conversation).filter(Conversation.id==conversation_id , Conversation.delete_sign == False,Conversation.username == username).first()
        if conversation is None:
            raise HTTPException(status_code=400, detail="Conversation not found") 
        else:
            return conversation
        
    # 匹配知识库
    def match_knowledgebase(self, conversation_id,username)->KnowledgeBase:
        try:
            conversation = self.match_conversations(conversation_id,username)
            print(conversation_id)
            print(f"knowledgeBaseId:{conversation.knowledgeBaseId}")
            knowledgebase = self.mysql_session.query(KnowledgeBase).filter(KnowledgeBase.knowledgeBaseId==conversation.knowledgeBaseId , KnowledgeBase.delete_sign==False,(KnowledgeBase.created_by == username)|(KnowledgeBase.is_public == True)).first()
            if knowledgebase is None:
                raise HTTPException(status_code=400, detail="KnowledgeBase not found")
            else:
                return knowledgebase
            
        except Exception as e:
            print(f"Erreor:{e}")
    # 生成对话标题
    def generate_conversation_title(self, conversation_id,username:str)->str:
        llm = LLM_Manager().creatLLM(mode_provider=self.default_llm_config.vendor_type,model=self.default_llm_config.model)
                
        conversation_messages = self.load_conversation(conversation_id,username=username)
        messageLogs = self.format_conversation_Log(conversation_messages)
        messageLogs_txt = ""
        limit_length = 6
        i = 0
        for item in messageLogs:
            if i >= limit_length:
                break
            i += 1
            messageLogs_txt += f"""
role: {item['role']}
content: {item['content']}
#########################
            """
        prompt = f"""
请根据以下对话内容生成一个对话标题，对话内容如下：\n
{messageLogs_txt}\n
请生成一个简洁明了的对话标题，不超过10个字,且仅需要输出标题,如果没有内容则输出:新对话
"""
            
        llm.setPrompt("你是一个对话标题生成器")
        title = llm.ChatToBot(prompt)
        print(f"生成的标题是：{title}")
        # 检查 title 是否为 None
        if title is None:
            return "新对话"  # 返回默认标题
        
        # 过滤掉可能的 <think></think> 标签及其内容
        import re
        title = re.sub(r'<think>.*?</think>', '', title, flags=re.DOTALL)
        
        return title.strip()
        
    # 获取知识库列表
    def get_knowledgebases(self,username:str):
        try:
            all_kbse = self.mysql_session.query(KnowledgeBase).filter((KnowledgeBase.created_by == username) | (KnowledgeBase.is_public == True),KnowledgeBase.delete_sign == False)
            return all_kbse
        except Exception as e:
            print(f"获取知识库失败:{e}")
    # 更改知识库
    def change_knowledgebase(self, conversation_id,knowledgeBaseId,username):
        try:
            conversation = self.match_conversations(conversation_id,username)
            conversation.knowledgeBaseId = knowledgeBaseId
            self.mysql_session.commit()
            self.mysql_session.refresh(conversation)
            return conversation
        except Exception as e:
            print(e)
    # 删除对话
    def delete_conversation(self, conversation_id,username:str)->Conversation:
        try:
            conversation = self.mysql_session.query(Conversation).filter(Conversation.id==conversation_id , Conversation.delete_sign == False , Conversation.username == username).first()
            if conversation is None:
                raise HTTPException(status_code=400, detail="Conversation not found")
            else:
                conversation.delete_sign = True
                self.mysql_session.commit()
                self.mysql_session.refresh(conversation)
                return conversation
            
        except Exception as e:
            print(e)
    # 重命名对话
    def rename_conversation(self, conversation_id,username, new_name):
        try:
            conversation = self.mysql_session.query(Conversation).filter(Conversation.id==conversation_id , Conversation.delete_sign == False , Conversation.username == username).first()
            if conversation is None:
                raise HTTPException(status_code=400, detail="Conversation not found")
            else:
                conversation.conversationName = new_name
                self.mysql_session.commit()
                self.mysql_session.refresh(conversation)


                return conversation
        except Exception as e:
            print(e)
    # 加载对话
    def load_conversation(self, conversation_id,username:str)->List[ChatMessageHistory]:
        # 检查对话是否属于用户
        conversation = self.mysql_session.query(Conversation).filter(Conversation.id==conversation_id , Conversation.delete_sign == False , Conversation.username == username).first()
        if conversation is None:
            raise HTTPException(status_code=400, detail="Conversation not found")
        # 查询对话记录
        try:
            messages = self.mysql_session.query(Chat_Messages).filter(Chat_Messages.conversationID == conversation_id).all()

            messages_history:List[ChatMessageHistory] = []

            for message in messages:
                messages_history_item = ChatMessageHistory(
                    conversation_id=message.conversationID,
                    query=message.query,
                    answer=message.answer,
                    current_knowledge_baseid=message.knowledgeBaseId,
                    retriever_docs=[]
                )
                retriever_docs = self.mysql_session.query(RetrieverDoc).filter(RetrieverDoc.messageId == message.id).all()

                for doc in retriever_docs:
                    retrieverDoc:RetrieverDocs = RetrieverDocs(
                        content=doc.content,
                        knowledge_doc_name=doc.knowledge_doc_name,
                        knowledgeBaseId=doc.knowledgeBaseId,
                    )
                    messages_history_item.retriever_docs.append(retrieverDoc)
                messages_history.append(messages_history_item)


            return messages_history
        except Exception as e:
            print(e)
    
    # 格式化对话记录
    def format_conversation_Log(self, messages:List[Chat_Messages]):
        messageLog = []
        for message in messages:
            formatted_message = {
                "role": "user",
                "content": message.query
            }
            messageLog.append(formatted_message)
            formatted_message = {
                "role": "assistant",
                "content": message.answer
            }
            messageLog.append(formatted_message)
        return messageLog

    # 保存对话
    def save_conversation(self, message:Chat_Messages):
        try:
            self.mysql_session.add(message)
            self.mysql_session.commit()
            self.mysql_session.refresh(message)
        except Exception as e:
            print(e)
    
    # 回答问题
    def answer_question(self, resultByDoc: ResultByDoc,history_message=[],streaming=False):
        # rAG_Pipeline = RAG_Pipeline()
            
        answer = self.rag.generate_answer_by_knowledgebase(resultByDoc=resultByDoc,history_messages=history_message,streaming=streaming,LLM_Model=self.llm_config.model,LLM_Provider=self.llm_config.LLM_Provider)
        if isinstance(answer, str):
            print(answer)
            print("answer")
            return answer
        else:
            for item in answer:
                yield item


    # 获取对话列表
    def get_conversation_list(self,username:str)->List[Conversation]:
        conversations = self.mysql_session.query(Conversation).filter(Conversation.delete_sign == False , Conversation.username == username ).all()
        return conversations
    # 先获取召唤文档
    def get_retrieve_documents(self, question,knowledgebase_id,rag_model:int,is_rerank:bool)->ResultByDoc:
        # rAG_Pipeline = RAG_Pipeline()
        try:
            resultByDoc:ResultByDoc =  self.rag.retrieve_documents(question=question,knowledge_base_id=knowledgebase_id,rag_model=rag_model,is_rerank=is_rerank)
            return resultByDoc
        except Exception as e:
            print(e)
    # 处理用户输入
    def run(self, chatMessageRequest: ChatMessageRequest,username, streaming=False):
        # 获取用户输入
        convseration_id = chatMessageRequest.conversation_id
        username = username
        message = chatMessageRequest.message
        # streaming = chatMessageRequest.streaming
        # 匹配对话
        try:
            conversation: Conversation = self.match_conversations(convseration_id, username)
            knowledgebase = self.match_knowledgebase(convseration_id, username)

            # 加载对话记录
            messages = self.load_conversation(conversation.id,username)
            if len(messages) < 3 and len(messages) > 0:
                title = self.generate_conversation_title(conversation_id=conversation.id,username=username)
                self.rename_conversation(conversation.id,username, title)
            messageLog = self.format_conversation_Log(messages)

            # 获取知识库配置信息
            kb_config = KBase().get_kb_config(knowledgebase.knowledgeBaseId,username)
            
            # 获取检索文档
            resultByDoc: ResultByDoc = self.get_retrieve_documents(question=message, knowledgebase_id=knowledgebase.knowledgeBaseId,rag_model=kb_config.rag_model,is_rerank=kb_config.is_rerank)

            # 保存对话记录
            new_message = Chat_Messages(
                conversationID=conversation.id,
                query=message,
                answer="",
                username=username,
                knowledgeBaseId=knowledgebase.knowledgeBaseId,
                timeStamp=datetime.datetime.now()
            )
            self.save_conversation(new_message)

            # 保存检索文档
            for doc in resultByDoc.source:
                retriever_doc = RetrieverDoc(
                    content=doc.content,
                    knowledge_doc_name=doc.knowledge_doc_name,
                    knowledgeBaseId=knowledgebase.knowledgeBaseId,
                    messageId=new_message.id
                )
                self.mysql_session.add(retriever_doc)
            self.mysql_session.commit()

            answer = ""
            # 生成回答
            if streaming:
                answer_generator  = self.answer_question(resultByDoc=resultByDoc,  history_message=messageLog, streaming=True)
                if isinstance(answer_generator, str):
                    pass
                else:
                    
                    for item in answer_generator :
                        yield item
                        answer+=item
                    # 流式输出完成后更新答案到数据库
                    new_message.answer = answer
                    self.mysql_session.commit()  # 更新数据库
                    self.mysql_session.refresh(new_message)
            else:
                answer = self.answer_question(resultByDoc=resultByDoc,  history_message=messageLog, streaming=False)
                if isinstance(answer, str):
                    
                    new_message.answer = answer
                    self.mysql_session.commit()  # 更新数据库
                    self.mysql_session.refresh(new_message)
                    
                    return answer
                else:
                    for item in answer:
                        yield item

        except Exception as e:
            print(f"Error Chat Run: {e}")

    




"""
临时梳理逻辑

前端先选择知识库，如果没有知识库则返回错误

然后再发起对会

后端对于空的对话id和选择的知识库id 还有userid，创建对话
并根据知识库回答问题

如果是已有的对话，则匹配对话，并根据知识库回答问题


所以需要有一个创建对话的接口，不能根据判断对话id是否为空来创建对话

"""