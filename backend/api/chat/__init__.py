"""
对话部分的路由
"""

from fastapi import APIRouter,File, UploadFile,Form,BackgroundTasks,Depends
from starlette.responses import StreamingResponse
from models.chat_models import ChatMessageRequest,KnowledgeBaseSelectRequest,ChatClearResponse,KnowledgeBaseSelectResponse,ChatMessageResponse,ChatMessageHistoryResponse,ConversationCreateRequest,ConversationCreateResponse,ChatConversationResponse,ReNameRequest,ReNameResponse,DeleteConversationResponse,ConversationTitleCreateResponse,ConversationTitleCreateRequest
from core.rag.rag_pipeline import RAG_Pipeline
from services.chat.chat import Chat
from core.database.models import Chat_Messages
from models.general_models import GenericResponse
from typing import List
from core.utils.utils import get_current_user

router = APIRouter()
rag:RAG_Pipeline = RAG_Pipeline()

@router.get("/chat-history/{conversation_id}",response_model=ChatMessageHistoryResponse)
def chat_history(conversation_id: str,username: str = Depends(get_current_user)):
    chat:Chat = Chat(conversation_id,"",rag)
    chat_history = chat.load_conversation(conversation_id,username)

    return ChatMessageHistoryResponse(data=chat_history,code = 200,message="Get chat history successfully!")

@router.post("/chat-message", response_model=ChatMessageResponse)
def chat(query: ChatMessageRequest,username: str = Depends(get_current_user)):
    # 获取对话id，如果为空则生成对话id，否则使用已有的对话id加载聊天记录
    conversation_id = query.conversation_id
    if not conversation_id:
        return ChatMessageResponse(code=400,message="Conversation id is required")
    
    chat:Chat = Chat(conversation_id,username,rag)

    try:
        if query.streaming:
            return StreamingResponse(chat.run(query,username,streaming=True), media_type="text/event-stream")
        else:
            result = chat.run(query,username,streaming=False)
            if result == None:
                raise Exception("No results found.")
            del chat
            return ChatMessageResponse(data=[result],code = 200,message="Get chat message successfully!")
    except Exception as e:
        print(f"ChatMessage Error:{e}")
        return ChatMessageResponse(code=400,message="No results found.")
@router.post("/create-conversation",response_model=ConversationCreateResponse)
def create_conversation(conversationCreateRequest: ConversationCreateRequest,username: str = Depends(get_current_user)):
    chat:Chat = Chat(conversation_id="",user_id=username,rag=rag)

    try:
        print(conversationCreateRequest.knowledge_base_id)
        conversation = chat.create_conversation(
            knowledgeBaseId=conversationCreateRequest.knowledge_base_id,
            username=username
            )
        del chat
        return ConversationCreateResponse(data=conversation.to_dict(),code = 200,message="Create conversation successfully!" )
    except Exception as e:
        # print(e)
        return ConversationCreateResponse(code=400,message="Failed to create conversation")
# 获取对话列表
@router.get("/chat-message/{user_id}",response_model=ChatConversationResponse)
def chat_message(user_id: str,username: str = Depends(get_current_user)):
    chat:Chat = Chat(conversation_id="",user_id=user_id,rag=rag)
    conversations = chat.get_conversation_list(username)
    conversations_prased = [conversation.to_dict() for conversation in conversations]

    return ChatConversationResponse(data=conversations_prased,code = 200,message="Get chat message successfully!" )

# 获取知识库列表
@router.get("/knowledge_base",tags=["获取知识库列表"],response_model=GenericResponse)
def knowledge_base(username: str = Depends(get_current_user)):
    chat:Chat = Chat(conversation_id="",user_id=username,rag=rag)
    knowledgeBase = chat.get_knowledgebases(username = username)
    data = []
    print(knowledgeBase)
    for kb in knowledgeBase:
        json_data = {
            "id": kb.knowledgeBaseId,
            "knowledgeBaseName": kb.knowledgeBaseName
        }
        data.append(json_data)

    return GenericResponse(message="获取成功",code=200,data=data)

@router.post("/knowledge_base",tags=["切换知识库"] ,response_model=KnowledgeBaseSelectResponse)
def knowledge_base(knowledgeBaseSelectRequest: KnowledgeBaseSelectRequest,username: str = Depends(get_current_user)):

    chat:Chat = Chat(conversation_id="",user_id=username,rag=rag)

    try:
        result = chat.change_knowledgebase(
            conversation_id=knowledgeBaseSelectRequest.conversation_id,
            knowledgeBaseId=knowledgeBaseSelectRequest.knowledge_base_id,
            username=username
            )
        if result == None:
            raise Exception("No results found.")
        del chat



        return KnowledgeBaseSelectResponse(data=[{
            "conversation_id":result.knowledgeBaseId,
            "conversation_name":result.conversationName
        }],code = 200,message="Get chat message successfully!" )

    except Exception as e:
        print(e)
        return KnowledgeBaseSelectResponse(code=400,message="No results found.")

@router.post("/chat-clear", response_model=ChatClearResponse)
def clear():
    return {"code": 200}

@router.delete("/conversation/{user_id}/{conversation_id}",tags=["删除对话"], response_model=DeleteConversationResponse)
def delete(conversation_id: str,user_id: str,username: str = Depends(get_current_user)):
    chat:Chat = Chat(conversation_id=conversation_id,user_id=username,rag=rag)
    try:
        conversation = chat.delete_conversation(conversation_id,username)
        return DeleteConversationResponse(code = 200,message="Delete conversation successfully!",data={"conversation_id":conversation.id,"conversation_name":conversation.conversationName})
    except Exception as e:
        print(e)
        return DeleteConversationResponse(code = 400,message="Failed to delete conversation!" )


    
@router.post("/conversation-rename/",tags=["重命名对话"], response_model=ReNameResponse)
def rename(reNameRequest:ReNameRequest,username: str = Depends(get_current_user)):
    chat:Chat = Chat(conversation_id=reNameRequest.conversation_id,user_id=username,rag=rag)
    try:
        conversation = chat.rename_conversation(reNameRequest.conversation_id,username,reNameRequest.new_name)
        return ReNameResponse(code = 200,message="Delete conversation successfully!",data={"conversation_id":conversation.id,"conversation_name":conversation.conversationName})
    except Exception as e:
        print(e)
        return ReNameResponse(code = 400,message="Failed to delete conversation!" )


# 生成对话标题
@router.post("/conversation_title",tags=["创建对话"], response_model=ConversationCreateResponse)
def create(conversationTitleCreateRequest: ConversationTitleCreateRequest,username: str = Depends(get_current_user)):
    chat:Chat = Chat(conversation_id="",user_id=username,rag=rag)
    try:
        title = chat.generate_conversation_title(conversationTitleCreateRequest.conversation_id,username)
        conversation = chat.rename_conversation(conversationTitleCreateRequest.conversation_id,username,title)
        return ConversationCreateResponse(code = 200,message="Create conversation successfully!",data=[{"conversation_id":conversation.id,"conversation_name":conversation.conversationName}])
    except Exception as e:
        print(e)
        return ConversationCreateResponse(code = 400,message="Failed to create conversation!" )
 