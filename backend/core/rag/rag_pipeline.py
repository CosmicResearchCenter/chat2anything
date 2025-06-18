from typing import List,Optional
from core.rag.database import ElasticClient,MysqlClient,MilvusCollectionManager
from core.rag.embedding import EmbeddingManager,OpenAIEmbedding,DouBaoEmbedding,Embedding
from config.config_info import settings
from config.splitter_model import SplitterModel
from .utils.split_file import split_file
from .models.source_document import SourceDocument,SourceDocumentReRanked
from core.llm import LLM,LLM_Manager
from core.rag.models.document import Document
from langchain_core.documents import Document as LcDocument
from core.rag.database.mysql.model import KnowledgeBase
from .rerank.rerank import RerankRunner
import os
from .prompt_template.prompt_template import PromptTemplate
from .prompt_template.prompts import INSTRUCTIONS,SYSTEM,PROMPT_TEMPLATE,RESOLVE_PRONOUNS
from .models.knolwedge_base import ResultByDoc
from .utils.embedding_config import EmbeddingConfig
import time
from core.utils.utils import GetDeafultLLM_Chat,GetDefaultEmbedding
class RAG_Pipeline:
    def __init__(self):#,LLM_Provider:str,LLM_Model:str,Embedding_Provider:str,Embedding_Model:str):
        self.mysql_client = MysqlClient()
        self.es_client = ElasticClient()
        self.milvus_client = MilvusCollectionManager()
        # self.LLM_Provider:str = LLM_Provider
        # self.LLM_Model:str = LLM_Model
        # self.Embedding_Provider:str = Embedding_Provider
        # self.Embedding_Model:str = Embedding_Model
        # self.default_llm_config = GetDeafultLLM_Chat()
        # self.default_embedding_config = GetDefaultEmbedding()

    def _get_default_llm_config(self):
        return GetDeafultLLM_Chat()
    def _get_default_embedding_config(self):
        return GetDefaultEmbedding()

    #创建知识库
    def create_knowledgebase(self, knowledge_base_name: str,username:str="admin"):
        knowledge_base_id = self.mysql_client.AddKnowledgeBasesList(knowledge_base_name,username=username).knowledgeBaseId
        indexName = self.es_client.create_index(knowledge_base_id)
        dim = EmbeddingConfig().get_dim()
        print(f"dim:{dim}")
        self.milvus_client.create_collection(knowledgeBaseID=knowledge_base_id, knowledgeBaseName=knowledge_base_name, dim=dim)
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
    def split_files(self,file_path:str,splitter_args,splitterModel:SplitterModel,split_LLM_PROVIDER:str,split_llm:str):
        return split_file(file_path,splitter_args=splitter_args,splitterModel=splitterModel,split_LLM_PROVIDER=split_LLM_PROVIDER,split_llm=split_llm)
    
    #文档插入知识库
    def insert_knowledgebase(self,file_path:str,docs:List[LcDocument], knowledge_base_id: str,doc_name:str,knowledge_doc_id:str,Embedding_Provider:str,Embedding_Model:str):

        ### 插入数据库
        # print("插入数据库")
        #### 写入向量数据库
        print("写入向量数据库")
        emb_model = EmbeddingManager().create_embedding(Embedding_Provider,Embedding_Model)
        mdata = []
        knowledge_doc_name = doc_name or os.path.basename(file_path)
        for doc in docs:
            content = doc.page_content
            vector = emb_model.embed_with_str(content, "document")
            item = {
                "content": content,
                "knowledge_doc_name": knowledge_doc_name,
                "vector": vector,
                "knowledge_doc_id":knowledge_doc_id
            }
            mdata.append(item)
        
        self.milvus_client.insert_data(mdata, knowledge_base_id)
        self.milvus_client.create_index(collection=knowledge_base_id)
        ### 写入 ElasticSearch
        print("写入 ElasticSearch")
        success,failed = self.es_client.insert_data(docs,knowledge_base_id,knowledge_doc_name,knowledge_doc_id)
        print(f"成功插入 {success} 条数据，失败 {len(failed)} 条数据")
        # return success,failed
    #文档召回
    def retriever_by_knowledgebase(self, question: str, knowledge_base_id: str,rag_model: int = 0):
        # 0 混合检索 1 向量检索 2 文档检索
        default_embedding_config = self._get_default_embedding_config()
        print(default_embedding_config.vendor_type)

        embeddingMode = EmbeddingManager().create_embedding(embedding_provider=default_embedding_config.vendor_type,model=default_embedding_config.model)
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
                if i == 3:
                    break
        
        if rag_model == 0 or rag_model == 2:
            print("检索文档知识库")
            # 文档检索
            result_elastic = self.es_client.search(question, knowledge_base_id)
            print("检索文档知识库结果：",result_elastic)
            i = 0
            for item in result_elastic:
                content = item["_source"]["content"]
                knowledge_doc_name = item["_source"]["knowledge_doc_name"]
                sourceDoc = SourceDocument(content=content, knowledge_doc_name=knowledge_doc_name)
                result.append(sourceDoc)
                i += 1
                if i == 3:
                    break
        
        return result
    
    # ReRank评估
    def re_rank(self,question:str,documents: list[Document], score_threshold: Optional[float] = None,
            top_n: Optional[int] = None):
        rerank_runner = RerankRunner()
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
            rerank_result = self.re_rank(question=question,documents=documents,score_threshold=0.01,top_n=4)
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
    def generate_answer_by_knowledgebase(self,resultByDoc:ResultByDoc,LLM_Provider:str,LLM_Model:str,history_messages=[],streaming=False):
        print("generate_answer_by_knowledgebase")
        print(history_messages)
        prompt_source =""
        for doc in resultByDoc.source:
            prompt_source+=f"""
            {doc.content}\n
            """


        llm = LLM_Manager().creatLLM(mode_provider=LLM_Provider,model=LLM_Model)

        prompt_system = PromptTemplate(
            template=SYSTEM,
            input_variables=['today_date', 'current_time']
        )
        today_date = time.strftime("%Y-%m-%d", time.localtime())
        current_time = time.strftime("%H:%M:%S", time.localtime())
        prompt_system = prompt_system.render(
            today_date=today_date,
            current_time=current_time
        )
        print(f"prompt_system:{prompt_system}") 
        instructions = PromptTemplate(
            template=INSTRUCTIONS,
            input_variables=['question']
        )
        instructions = instructions.render(
            question=resultByDoc.query
        )

        prompt = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=['instructions', 'context']
        )
        prompt = prompt.render(
            instructions=instructions,
            context=prompt_source
        )

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