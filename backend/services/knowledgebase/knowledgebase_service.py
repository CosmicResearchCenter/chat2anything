from core.rag.database.mysql.model import KnowledgeBase
from core.database.models import DocInfo,DocIndexStatus,KnowledgeConfig
from core.database.mysql_client import MysqlClient
from fastapi import HTTPException
from models.general_models import GenericResponse
from core.rag.database.milvus.milvus_client import MilvusCollectionManager
from core.rag.database.elasticsearch.elastic_client import ElasticClient
from core.rag.rag_pipeline import RAG_Pipeline
from .knowledgebase_type import CreateBaseRequest,IndexStatusRequest,DocumentSplitArgs,KnowledgeBaseConfig
from fastapi import UploadFile,BackgroundTasks
from config.splitter_model import SplitterModel
from typing import List,Callable
import os
import shutil
import time
from pathlib import Path
import uuid
import asyncio
import threading
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'docx','doc','md','excel','xlsx','xls'}

def check_kb_owner_decorator(method: Callable):
    """
    装饰器，用于检查知识库是否是用户创建的。
    """
    @wraps(method)
    def wrapper(self, base_id: int, username: str, *args, **kwargs):
        # 检查知识库是否是用户创建的
        print(f'check_kb_owner_decorator base_id: {base_id}, username: {username}')
        kb = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.knowledgeBaseId == base_id,
            (KnowledgeBase.created_by == username) |(KnowledgeBase.is_public == True),
        ).first()
        
        if not kb:
            raise HTTPException(status_code=404, detail="KnowledgeBase not found 404 !")
        return method(self, base_id, username, *args, **kwargs)
    return wrapper


class KBase(MysqlClient):
    def __init__(self):
        super().__init__()
        self.index_status = False
    def __del__(self):
        super().__del__()
    # 创建知识库
    def create_kb(self, kb_name:str,username:str)->KnowledgeBase:
        rAG_Pipeline:RAG_Pipeline = RAG_Pipeline()
        
        # 设置默认配置
        rag_model = 0
        is_rerank = False
        try:
            kb_id = rAG_Pipeline.create_knowledgebase(kb_name,username=username)
            print(f'create_kb kb_id: {kb_id}')
            config = KnowledgeConfig(knowledgeBaseId=kb_id,rag_model=rag_model,is_rerank=is_rerank,create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            self.db.add(config)
            self.db.commit()
            return kb_id
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 
     
    # 获取所有知识库
    def get_all_kbs(self,username:str)->List[KnowledgeBase]:
        
        # all_kbs = self.db.query(KnowledgeBase).all()
        rAG_Pipeline:RAG_Pipeline = RAG_Pipeline()
        try:
            all_kbs = rAG_Pipeline.show_knowledgebase_list(username)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return all_kbs
    
    # 根据id获取知识库
    @check_kb_owner_decorator
    def get_kbinfo_by_id(self, base_id:int,username:str)->List[DocInfo]:

        # # 判断知识库是否是用户创建的
        # self.check_kb_owner(kb_id,username)
        kb_info = self.db.query(DocInfo).filter(DocInfo.knowledgeBaseId == base_id,DocInfo.delete_sign==False).all()
        return kb_info
    
    # 删除知识库
    @check_kb_owner_decorator
    def delete_kb(self, base_id:int,username:str)->GenericResponse:
        # 删除表
        kb = self.db.query(KnowledgeBase).filter(KnowledgeBase.knowledgeBaseId == base_id).first()
        if not kb:
            return GenericResponse(message="KnowledgeBase not found", code=404,data=[])
        self.db.delete(kb)
        self.db.commit()
        # 删除ElasticSearch数据
        try:
            elastic_client = ElasticClient()
            elastic_client.delete_index(base_id)
        except Exception as e:
            print("Error deleting index from ElasticSearch: ", e)
            return GenericResponse(message="KnowledgeBase not found", code=404,data=[])
        # 删除Milvus数据
        try:
            milvus_manager = MilvusCollectionManager()
            milvus_manager.drop_collection(f'{base_id}')
        except Exception as e:
            print("Error dropping collection from Milvus: ", e)
            return GenericResponse(message="KnowledgeBase not found", code=404,data=[])
        
        return GenericResponse(message="KnowledgeBase deleted successfully", code=200,data=[])
    # 删除文档
    @check_kb_owner_decorator
    def delete_document(self,base_id:str,username:str, doc_id:str)->GenericResponse:
        doc = self.db.query(DocInfo).filter(DocInfo.save_id == doc_id).first()
        if not doc:
            return GenericResponse(message="Document not found", code=404,data=[])
        doc.delete_sign = True
        
        milvus_client = MilvusCollectionManager()
        milvus_client.delete_by_knowledge_doc_id(base_id,doc_id)

        es_client = ElasticClient()
        es_client.delete_by_knowledge_doc_id(base_id,doc_id)

        self.db.commit()
        self.db.refresh(doc)
        
        return GenericResponse(message="Document deleted successfully", code=200,data=[])
    def _get_docs_save_path(self, base_id:int)->Path:
        from config.config_info import settings
        save_path_p = Path(settings.DOCS_PATH)/ base_id
        if not os.path.exists(save_path_p):
            os.makedirs(save_path_p)
        return save_path_p
    # 更新知识库
    # 为每个文档生成一个信息字典，包括文档id、文档名称、文档类型等信息，保存到数据库中
    @check_kb_owner_decorator
    async def upload_files(self, base_id:int, username:str, files:List[UploadFile], 
                           background_tasks:BackgroundTasks, executor:ThreadPoolExecutor) -> List[DocIndexStatus]:
        from config.config_info import settings
        save_path_p = self._get_docs_save_path(base_id)
        docs:List[DocInfo] = []
        docs_status:List[DocIndexStatus] = []
        
        for file in files:
            doc_name = file.filename
            extension = file.filename.split('.')[-1]
            if extension not in ALLOWED_EXTENSIONS:
                raise HTTPException(status_code=400, detail=f"Invalid file extension: {extension}")

            create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            doc_size = file.size
            save_id = str(uuid.uuid4())
            doc_newname = f'{save_id}.{extension}'
            save_path = Path(save_path_p) / doc_newname

            # 异步保存文件到本地
            contents = await file.read()
            async with aiofiles.open(save_path, "wb") as buffer:
                await buffer.write(contents)
                
            doc = DocInfo(doc_name=doc_name, doc_type=extension, doc_size=doc_size, 
                          create_time=create_time, knowledgeBaseId=base_id, save_id=save_id)
            
            self.db.add(doc)
            self.db.commit()
            docs.append(doc)

            index_status = DocIndexStatus(index_status=0, knowledgeBaseId=base_id, doc_id=save_id)
            self.db.add(index_status)
            self.db.commit()
            docs_status.append(index_status)

        print(f'{len(files)} files saved successfully')
        return docs_status
    @check_kb_owner_decorator
    def insert_knowledgebase(self,base_id,username,documentSplitArgs:DocumentSplitArgs,doc_id,background_tasks:BackgroundTasks,executor:ThreadPoolExecutor)->DocIndexStatus:
        
        
        index_status = DocIndexStatus(index_status=0,knowledgeBaseId=base_id,doc_id=doc_id)
        self.db.add(index_status)
        self.db.commit()

        doc = self.db.query(DocInfo).filter(DocInfo.save_id == doc_id).first()
        print(f'insert_knowledgebase document {doc.doc_name}')
        # 获取分割参数
        splitter_model = documentSplitArgs.splitter_model
        splitter_args = documentSplitArgs.splitter_args
        print(f'insert_knowledgebase document {doc.doc_name}, splitter_model: {splitter_model}, splitter_args: {splitter_args}')
        if splitter_model == 0:
            splitter_args["window_size"] = int(splitter_args["window_size"])
            splitter_args["step_size"] = int(splitter_args["step_size"])
            background_tasks.add_task(executor.submit, self._insert_knowledgebase, base_id, doc,splitter_args, SplitterModel.LLMSplitter)

        elif splitter_model == 1:
            splitter_args["chunk_size"] = int(splitter_args["chunk_size"])
            splitter_args["chunk_overlap"] = int(splitter_args["chunk_overlap"])
            background_tasks.add_task(executor.submit, self._insert_knowledgebase, base_id, doc,splitter_args, SplitterModel.TextSplitter)
        
        return index_status
    # 解析文档
    def _insert_knowledgebase(self, base_id:int, doc:DocInfo, splitter_args, splitterModel:SplitterModel):
        print(f'开始处理文档: {doc.doc_name}')
        rAG_Pipeline:RAG_Pipeline = RAG_Pipeline()

        save_path_p = self._get_docs_save_path(base_id)

        doc_newname = f'{doc.save_id}.{doc.doc_type}'
        doc_path = Path(save_path_p)/ doc_newname
        
        try:
            print(f'开始拆分文档: {doc_path}，使用模型: {splitterModel}')
            docs = rAG_Pipeline.split_files(str(doc_path), splitter_args, splitterModel)
            print(f'文档拆分完成: {doc.doc_name}, 共拆分为 {len(docs)} 个段落')
            
            print(f'开始插入知识库: {base_id}')
            rAG_Pipeline.insert_knowledgebase(file_path=str(doc_path), docs=docs, knowledge_base_id=base_id, doc_name=doc.doc_name, knowledge_doc_id=doc.save_id)
            print(f'成功插入知识库: {doc.doc_name}')
        except Exception as e:
            print(f"处理文档时发生错误 {doc.doc_name}: {str(e)}")
            # 可以考虑更新状态为失败
            index_status = self.db.query(DocIndexStatus).filter(DocIndexStatus.knowledgeBaseId == base_id, DocIndexStatus.doc_id==doc.save_id).first()
            if index_status:
                index_status.index_status = 2  # 2 表示失败
                self.db.commit()
                return

        # 更新索引状态
        index_status = self.db.query(DocIndexStatus).filter(DocIndexStatus.knowledgeBaseId == base_id, DocIndexStatus.doc_id==doc.save_id).first()
        if index_status:
            index_status.index_status = 1
            self.db.commit()
            self.db.refresh(index_status)

    def get_index_status(self, base_id:str,doc_id:str)->DocIndexStatus:
        index_status = self.db.query(DocIndexStatus).filter(DocIndexStatus.knowledgeBaseId == base_id,DocIndexStatus.doc_id==doc_id).first()
        if not index_status:
            raise HTTPException(status_code=404, detail="Index status not found")
        return index_status
    
    # 获取知识库配置信息
    @check_kb_owner_decorator
    def get_kb_config(self, base_id:str,username:str)->KnowledgeBaseConfig:
         
        knowledgeBase = self.db.query(KnowledgeBase).filter(KnowledgeBase.knowledgeBaseId == base_id).first()
        if not knowledgeBase:
            raise HTTPException(status_code=404, detail="KnowledgeBase not found")
        knowledgeBaseName = knowledgeBase.knowledgeBaseName
        config = self.db.query(KnowledgeConfig).filter(KnowledgeConfig.knowledgeBaseId == base_id).first()
        if not config:
            raise HTTPException(status_code=404, detail="KnowledgeBase config not found")
        
        return KnowledgeBaseConfig(knowledgeBaseId=base_id,knowledgeBaseName=knowledgeBaseName,rag_model=config.rag_model,is_rerank=config.is_rerank)
    # 更新知识库配置信息
    @check_kb_owner_decorator
    def update_kb_config(self, base_id:str,username:str,config:KnowledgeBaseConfig)->GenericResponse:
        knowledgeBase = self.db.query(KnowledgeBase).filter(KnowledgeBase.knowledgeBaseId == base_id).first()
        if not knowledgeBase:
            raise HTTPException(status_code=404, detail="KnowledgeBase not found")
        
        knowledgeBase.knowledgeBaseName = config.knowledgeBaseName
        self.db.commit()
        self.db.refresh(knowledgeBase)
        
        config_db = self.db.query(KnowledgeConfig).filter(KnowledgeConfig.knowledgeBaseId == base_id).first()
        if not config_db:
            raise HTTPException(status_code=404, detail="KnowledgeBase config not found")
        config_db.rag_model = config.rag_model
        config_db.is_rerank = config.is_rerank
        config_db.update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.db.commit()
        self.db.refresh(config_db)
        
        return GenericResponse(message="KnowledgeBase config updated successfully", code=200,data=[])
    
    # 重命名文档名字
    @check_kb_owner_decorator
    def rename_doc_name(self,base_id:str,username:str, doc_id:int,new_name:str)->GenericResponse:
        doc = self.db.query(DocInfo).filter(DocInfo.save_id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc.doc_name = new_name
        self.db.commit()
        self.db.refresh(doc)
        return GenericResponse(message="Document name updated successfully", code=200,data=[])
    
    # 归档文档
    @check_kb_owner_decorator
    def archive_doc(self,base_id:str,username:str, doc_id:int)->GenericResponse:
        doc = self.db.query(DocInfo).filter(DocInfo.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        doc.delete_sign = True
        self.db.commit()
        self.db.refresh(doc)
        return GenericResponse(message="Document archived successfully", code=200,data=[])