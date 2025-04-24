"""
知识库管理部分的路由
"""

from fastapi import APIRouter,File, UploadFile,Form,BackgroundTasks,Depends
from services.knowledgebase.knowledgebase_service import KBase
from services.knowledgebase.knowledgebase_type import CreateBaseRequest,IndexStatusRequest,DocumentSplitArgs,KnowledgeBaseConfig
from models.general_models import GenericResponse
from typing import List
from core.utils.utils import get_current_user
from core.database.mysql_client import MysqlClient
from core.database.models import KnowledgeBase
from concurrent.futures import ThreadPoolExecutor


router = APIRouter()
executor = ThreadPoolExecutor(max_workers=5)

@router.post("/",tags=["创建知识库"],response_model=GenericResponse)
async def create(createBaseRequest:CreateBaseRequest,username: str = Depends(get_current_user)):
    kb = KBase()
    knowledgeBase_id = kb.create_kb(createBaseRequest.base_name,username)
    return GenericResponse(message="获取成功",code=200,data=[{'knowledgeBase_id':knowledgeBase_id}])

@router.get("/",tags=["获取知识库列表"],response_model=GenericResponse)
async def get_base_list(username: str = Depends(get_current_user)):
    kb_manager = KBase()
    knowledgeBase = kb_manager.get_all_kbs(username = username)
    
    data = []
    for kb in knowledgeBase:
        json_data = {
            "id": kb.knowledgeBaseId,
            "docs_num": kb.docs_num,
            "related_conversations": kb.related_conversations,
            "knowledgeBaseName": kb.knowledgeBaseName
        }
        data.append(json_data)

    return GenericResponse(message="获取成功",code=200,data=data)


@router.get("/{base_id}",tags=["获取知识库详情"],response_model=GenericResponse)
async def get_base_detail(base_id:str,username: str = Depends(get_current_user)):
    kb_manager = KBase()
    infos = kb_manager.get_kbinfo_by_id(base_id,username)
    infos_prased = []
    for index_info in infos:
        info = {
            'create_time':index_info.create_time,
            'doc_name':index_info.doc_name,
            'doc_id':index_info.save_id,
            'doc_size':index_info.doc_size,
        }
        infos_prased.append(info)
    return GenericResponse(message="获取成功",code=200,data=infos_prased)

@router.put("/{base_id}",tags=["更新知识库"],response_model=GenericResponse)
async def upload(
    base_id:str,
    background_tasks: BackgroundTasks,
    file:UploadFile = File(...),
    username: str = Depends(get_current_user)
    ):
    
    # 检查知识库是否是属于用户的
    mysql_client = MysqlClient()
    kb = mysql_client.db.query(KnowledgeBase).filter(KnowledgeBase.knowledgeBaseId == base_id,KnowledgeBase.created_by==username).first()
    if kb == None:
        return GenericResponse(message="知识库不存在",code=400,data=[])
    
    print("uploading file")
    if file == None:
        return GenericResponse(message="文件不能为空",code=400,data=[])
    
    if base_id == "":
        return GenericResponse(message="知识库ID不能为空",code=400,data=[])
    
    kb_manager = KBase()

    # 调用异步方法
    index_infos = await kb_manager.upload_files(base_id, username, [file], background_tasks, executor)

    index_infos_prase = []
    for index_info in index_infos:
        info = {
            'doc_id':index_info.doc_id,
            'index_status':index_info.index_status,
            'knowledgeBaseId':index_info.knowledgeBaseId
        }
        index_infos_prase.append(info)

    return GenericResponse(message="上传成功",code=200,data=index_infos_prase)

@router.post("/{base_id}/doc/{doc_id}/index",tags=["插入文档到知识库"],response_model=GenericResponse)
def insert_doc(base_id:str,doc_id:str,documentSplitArgs:DocumentSplitArgs,background_tasks: BackgroundTasks,username: str = Depends(get_current_user)):
    
    kb_manager = KBase()
    index_status = kb_manager.insert_knowledgebase(base_id,username,documentSplitArgs,doc_id,background_tasks,executor)
    return GenericResponse(message="正在建立索引",code=200,data=[index_status.to_dict()])


@router.get("/{base_id}/doc/{doc_id}/index_status", tags=["获取文档索引状态"],response_model=GenericResponse)
async def get_doc_index_status(base_id:str, doc_id:str,username: str = Depends(get_current_user)):
    
    kb_manager = KBase()
    index_status = kb_manager.get_index_status(base_id,doc_id)

    return GenericResponse(message="获取成功",code=200,data=[index_status.to_dict()])


@router.delete("/{base_id}",tags=["删除知识库"],response_model=GenericResponse)
async def delete(base_id:str,username: str = Depends(get_current_user)):

    kb_manager = KBase()
    return kb_manager.delete_kb(base_id,username)


@router.delete("/{base_id}/doc/{doc_id}",tags=["删除文档"],response_model=GenericResponse)
async def delete_doc(base_id,doc_id,username: str = Depends(get_current_user)):
    kb_manager = KBase()
    return kb_manager.delete_document(base_id,username,doc_id)

# 更新知识库配置
@router.put("/{base_id}/config",tags=["更新知识库配置"],response_model=GenericResponse)
async def update_config(base_id:str,config:KnowledgeBaseConfig,username: str = Depends(get_current_user)):
    
    kb_manager = KBase()
    return kb_manager.update_kb_config(base_id=base_id,config=config,username=username)

# 获取知识库配置
@router.get("/{base_id}/config",tags=["获取知识库配置"],response_model=GenericResponse)
async def get_config(base_id:str,username: str = Depends(get_current_user)):
    kb_manager = KBase()
    config = kb_manager.get_kb_config(base_id,username)
    return GenericResponse(message="获取成功",code=200,data=[config])

# 重命名文档名字
@router.put("/{base_id}/doc/{doc_id}/rename",tags=["重命名文档"],response_model=GenericResponse)
async def rename_doc_name(base_id:str,doc_id:str,new_name:str,username: str = Depends(get_current_user)):
    kb_manager = KBase()
    return kb_manager.rename_doc_name(base_id,username,doc_id,new_name)

# 归档文档
@router.put("/{base_id}/doc/{doc_id}/archive",tags=["归档文档"],response_model=GenericResponse)
async def archive_doc(base_id:str,doc_id:str,username: str = Depends(get_current_user)):
    kb_manager = KBase()
    return kb_manager.archive_doc(base_id,username, doc_id)