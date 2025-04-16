from typing import List,Optional
from core.rag.database import ElasticClient,MysqlClient,MilvusCollectionManager
from core.rag.embedding import EmbeddingManager,OpenAIEmbedding,DouBaoEmbedding,Embedding
from config.config_info import settings
from config.splitter_model import SplitterModel
from .utils.split_file import split_file
from .models.source_document import SourceDocument,SourceDocumentReRanked
from core.llm import LLM,LLM_Manager,RerankModel
from core.rag.models.document import Document
from langchain_core.documents import Document as LcDocument
from core.rag.database.mysql.model import KnowledgeBase
from .rerank.rerank import RerankRunner
import os

from .models.knolwedge_base import ResultByDoc

class RAG_Pipeline:
    def __init__(self):
        self.mysql_client = MysqlClient()
        self.es_client = ElasticClient()
        self.milvus_client = MilvusCollectionManager()
        pass
    #创建知识库
    def create_knowledgebase(self, knowledge_base_name: str,username:str="admin"):
        knowledge_base_id = self.mysql_client.AddKnowledgeBasesList(knowledge_base_name,username=username).knowledgeBaseId
        indexName = self.es_client.create_index(knowledge_base_id)
        self.milvus_client.create_collection(knowledgeBaseID=knowledge_base_id, knowledgeBaseName=knowledge_base_name, dim=1536)
        return knowledge_base_id
    #修改知识库名字
    def modify_knowledgebase(self, new_knowledge_base_name: str,knowledge_base_id: str):
        pass
    #删除知识库
    def delete_knowledgebase(self, knowledge_base_name: str):
        pass
    def show_knowledgebase_list(self,username:str):
        knowledgebaseList:List[KnowledgeBase] =  self.mysql_client.GetKnowledgeBasesList(username)
        return knowledgebaseList
    # 文档拆分
    def split_files(self,file_path:str,splitter_args,splitterModel:SplitterModel):
        return split_file(file_path,splitter_args=splitter_args,splitterModel=splitterModel)
    
    #文档插入知识库
    def insert_knowledgebase(self,file_path:str,docs:List[LcDocument], knowledge_base_id: str,doc_name:str):

        ### 插入数据库
        # print("插入数据库")
        #### 写入向量数据库
        print("写入向量数据库")
        emb_model = EmbeddingManager().create_embedding(settings.EMBEDDING_MODEL_PROVIDER)
        mdata = []
        knowledge_doc_name = doc_name or os.path.basename(file_path)
        for doc in docs:
            content = doc.page_content
            vector = emb_model.embed_with_str(content, "document")
            item = {
                "content": content,
                "knowledge_doc_name": knowledge_doc_name,
                "vector": vector
            }
            mdata.append(item)
        
        self.milvus_client.insert_data(mdata, knowledge_base_id)
        self.milvus_client.create_index(collection=knowledge_base_id)
        ### 写入 ElasticSearch
        print("写入 ElasticSearch")
        success,failed = self.es_client.insert_data(docs,knowledge_base_id,knowledge_doc_name)
        print(f"成功插入 {success} 条数据，失败 {len(failed)} 条数据")
        # return success,failed
    #文档召回
    def retriever_by_knowledgebase(self, question: str, knowledge_base_id: str, rag_model: int = 0):
        # 0 混合检索 1 向量检索 2 文档检索
        
        embeddingMode = EmbeddingManager().create_embedding(settings.EMBEDDING_MODEL_PROVIDER)
        vector = embeddingMode.embed_with_str(question, "query")
        
        result: List[SourceDocument] = []
        
        print("检索知识库")
         
        if rag_model == 0 or rag_model == 1:
            print("检索向量知识库")
            # 向量检索
            result_milvus = self.milvus_client.search(vector, knowledge_base_id)
            i = 0
            for item in result_milvus[0]:
                content = item.entity.content
                knowledge_doc_name = item.entity.knowledge_doc_name
                sourceDoc = SourceDocument(content=content, knowledge_doc_name=knowledge_doc_name)
                result.append(sourceDoc)
                i += 1
                if i == 5:
                    break
        
        if rag_model == 0 or rag_model == 2:
            print("检索文档知识库")
            # 文档检索
            result_elastic = self.es_client.search(question, knowledge_base_id)
            print("检索文档知识库结果：",result_elastic)
            i = 0
            for item in result_elastic:
                content = item["_source"]["content"]
                knowledge_doc_name = item["_source"]["knowledgeDocName"]
                sourceDoc = SourceDocument(content=content, knowledge_doc_name=knowledge_doc_name)
                result.append(sourceDoc)
                i += 1
                if i == 5:
                    break
        
        return result
    
    # ReRank评估
    def re_rank(self,question:str,documents: list[Document], score_threshold: Optional[float] = None,
            top_n: Optional[int] = None):
        rerank_model = RerankModel()
        rerank_runner = RerankRunner(rerank_model)
        rerank_result = rerank_runner.run(question, documents, score_threshold=score_threshold, top_n=top_n)

        
        
        return rerank_result
    # 找回文档
    def retrieve_documents(self,question:str,knowledge_base_id: str,rag_model:int=0,is_rerank:bool=False)->ResultByDoc:
        print("generate_answer_by_knowledgebase")
        # 获取文档源信息
        source_docs:List[SourceDocument] = self.retriever_by_knowledgebase(question,knowledge_base_id,rag_model)

        documents:List[Document] = []
        for source in source_docs:
            # print(source.content+"\n#####")
            documents.append(Document(
                                    page_content=source.content,
                                    metadata={
                                        "knowledge_doc_name": source.knowledge_doc_name
                                    })
                            )
        source_docs_result:List[SourceDocumentReRanked] = []
        # ReRank评估
        if is_rerank:
            rerank_result = self.re_rank(question=question,documents=documents,score_threshold=0.001,top_n=4)
            for result in rerank_result:
                # prompt_source += f"""
                # {result.page_content}\n
                # """
                source_docs_result.append(SourceDocumentReRanked(
                                    content=result.page_content,
                                    knowledge_doc_name=result.metadata['knowledge_doc_name'],
                                    socre=result.metadata['score']
                                ))
                # print(result.metadata['score'])
        else: 
            for result in source_docs:

                source_docs_result.append(SourceDocumentReRanked(
                                    content=result.content,
                                    knowledge_doc_name=result.knowledge_doc_name,
                                    socre=0.00
                                ))
                # print(result.metadata['score'])
        resultByDoc:ResultByDoc = ResultByDoc(source=source_docs_result,query=question)
        return resultByDoc

    #生成回答
    def generate_answer_by_knowledgebase(self,resultByDoc:ResultByDoc,history_messages=[],streaming=False):
        print("generate_answer_by_knowledgebase")
        print(history_messages)
        prompt_source =""
        for doc in resultByDoc.source:
            prompt_source+=f"""
            {doc.content}\n
            """


        llm = LLM_Manager().creatLLM(mode_provider=settings.LLM_PROVIDER)
        prompt_system =f"""
你是一个基于文档提供高质量回答的助手。你的任务是根据提供的文档内容，准确、清晰地回答用户的问题。请确保以下几点：

1. 基于文档：你的回答应严格基于提供的文档内容，避免编造信息。如果文档中没有相关信息，请明确告知用户。
2. 准确性：回答应尽可能准确，避免模糊或不确定的表达。如果某些部分是合理推测，请明确说明。
3. 简洁明了：尽量简洁明了地表达你的回答，不使用多余的细节。
4. 专业性：回答应保持专业性和客观性，避免使用主观或情感化的语言。

你将收到召回的文档内容以及用户的问题，请在此基础上生成回答。
""" 
        prompt = f"""
你是一个基于文档提供高质量回答的助手。你的任务是根据提供的文档内容，准确、清晰地回答用户的问题。
现在请你完成以下任务：
请根据用户问题，使用召回的知识库中的信息进行推理回答。请确保回答内容准确。
要求：
1. 使用文档中的信息来推理回答问题，并确保答案准确。
2. 如果文档中没有明确的信息，可以合理推断，但要标注推断部分。
3. 尽量简洁明了地表达。
######################################\n
用户问题:
{resultByDoc.query}
######################################\n
知识库内容:
{prompt_source}
"""
        print(prompt)

        llm.addHistory(history_messages)
        llm.setPrompt(prompt_system)
        if not streaming:
            answer = llm.ChatToBot(prompt)
            print(answer)
            return answer
        else:
            answer = llm.ChatToBotWithStream(prompt)
            for i in answer:
                if i:
                    yield i
            
if __name__ == "__main__":
    # 创建知识库
    pipelines = RAG_Pipeline()
    resultByDoc:ResultByDoc= ResultByDoc(query="hello world",source=[])
    print("resultByDoc")
    answer = pipelines.generate_answer_by_knowledgebase(resultByDoc=resultByDoc,history_messages=[],streaming=True)

    if isinstance(answer, str):
        print("Answer:", answer)
    else:
        # 遍历生成器输出以获取完整答案
        for part in answer:
            print("Streaming Answer Part:", part)