from  pydantic import BaseModel
class SourceDocument(BaseModel):
    content: str
    knowledge_doc_name: str

class SourceDocumentReRanked(BaseModel):
    content: str
    knowledge_doc_name: str   
    socre: float
#     def __init__(self, content:str, knowledge_doc_name: str):
#         self.content = content
#         self.knowledge_doc_name = knowledge_doc_name

# class SourceDocument:
#     content: str
#     knowledge_doc_name: str
    
#     def __init__(self, content:str, knowledge_doc_name: str):
#         self.content = content
#         self.knowledge_doc_name = knowledge_doc_name