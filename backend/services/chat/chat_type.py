from pydantic import BaseModel
from typing import List

class RetrieverDoc(BaseModel):
    content : str
    knowledge_doc_name: str
    knowledgeBaseId : str
    

class ChatMessageHistory(BaseModel):
    conversation_id: str
    query: str
    answer: str
    retriever_docs: List[RetrieverDoc]
    current_knowledge_baseid:str



