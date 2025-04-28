"""
后台管理员部分的路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Path
import hashlib
import jwt
import datetime
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config.config_info import settings
from core.database.mysql_client import MysqlClient
from core.database.models import UserInfo
from core.utils.utils import get_is_admin
from typing import Optional, List, Dict, Any
from services.admin.admin_service  import AdminService
from .admin import (ResponseGenral,
                    DeleteUserConversationRequest,
                    DeleteUserKnowledgeBaseRequest,
                    DeleteUserRequest,
                    GrantAdminRequest,
                    RevokeAdminRequest,
                    UserGrowthRequest,
                    ConversationTrendRequest,
                    RecentActivitiesRequest,
                    ActiveUsersRequest,
                    UserListResponse,      # 导入
                    UserDetailsResponse,   # 导入
                    UpdateUserStatusRequest, # 导入
                    # 新增配置相关模型
                    LLMConfigCreate,
                    LLMConfigUpdate,
                    LLMConfigResponse,
                    LLMConfigListResponse,
                    EmbeddingConfigCreate,
                    EmbeddingConfigUpdate,
                    EmbeddingConfigResponse,
                    EmbeddingConfigListResponse
                    )
router = APIRouter()

# 获取系统基本信息
@router.get("/system_info", response_model=ResponseGenral)
async def get_system_info(username: str = Depends(get_is_admin)):
    admin_service = AdminService()
    system_info = admin_service.get_system_info()
   
    return ResponseGenral(
        code=200,
        message="返回系统基本信息",
        data=[system_info]
    ) 

# 获取用户 (旧接口，保留或移除)
# @router.get("/users_old", response_model=ResponseGenral)
# async def get_users_conversation(username: str = Depends(get_is_admin)):
#     admin_service = AdminService()
#     users = admin_service.get_all_users()
#     return ResponseGenral(
#         code=200,
#         message="返回用户对话信息",
#         data=[users] # 注意旧接口返回格式
#     )

# 获取用户列表（增强版）
@router.get("/users", response_model=UserListResponse)
async def get_users_paginated(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100), # 添加最大值限制
    search: Optional[str] = Query(None),
    type: str = Query('all', enum=['all', 'admin', 'user']),
    sortBy: Optional[str] = Query(None, description="Sort by field like 'username', 'create_time'"),
    sortOrder: str = Query('desc', enum=['asc', 'desc']),
    username: str = Depends(get_is_admin) # 权限验证
):
    admin_service = AdminService()
    users, total = admin_service.get_users_paginated(
        page=page,
        pageSize=pageSize,
        search=search,
        user_type=type,
        sortBy=sortBy,
        sortOrder=sortOrder
    )
    return UserListResponse(
        code=200,
        message="获取用户列表成功",
        data={"users": users, "total": total}
    )

# 获取用户详细信息及统计
@router.get("/user/{target_username}/details", response_model=UserDetailsResponse)
async def get_user_details(target_username: str, username: str = Depends(get_is_admin)):
    admin_service = AdminService()
    details = admin_service.get_user_details(target_username)
    if not details:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDetailsResponse(
        code=200,
        message="获取用户详情成功",
        data=details
    )

# 更新用户状态
@router.put("/user/{target_username}/status", response_model=ResponseGenral)
async def update_user_status(
    target_username: str,
    request: UpdateUserStatusRequest,
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    self_username = username.data[0]['username'] # 从 Depends 获取操作者用户名
    success = admin_service.update_user_status(target_username, request.status, self_username)
    if not success:
        # 根据失败原因返回更具体的错误信息
        user_info = MysqlClient().db.query(UserInfo).filter(UserInfo.username == target_username).first()
        if not user_info:
             raise HTTPException(status_code=404, detail="User not found")
        if target_username == 'admin' and request.status == 'disabled':
             raise HTTPException(status_code=400, detail="Cannot disable the admin user")
        if user_info.is_admin and self_username != 'admin':
             raise HTTPException(status_code=403, detail="Permission denied to modify admin status")
        if request.status not in ['active', 'disabled']:
             raise HTTPException(status_code=400, detail="Invalid status value")

        raise HTTPException(status_code=500, detail="Failed to update user status") # 其他未知错误

    return ResponseGenral(
        code=200,
        message="用户状态更新成功",
        data={}
    )

# 根据用户名获取对话列表
@router.get("/user_conversation/{username}", response_model=ResponseGenral)
async def get_user_conversation(username: str, s_username = Depends(get_is_admin)):
    self_username = s_username.data[0]['username']
    admin_service = AdminService()
    user_conversation = admin_service.get_user_conversation(username,self_username)
    return ResponseGenral(
        code=200,
        message="返回用户对话信息",
        data=[user_conversation]
    )
# 根据对话id获取对话信息
@router.get("/conversation/{conversation_id}", response_model=ResponseGenral)
async def get_conversation(conversation_id: str, username: str = Depends(get_is_admin)):
    
    admin_service = AdminService()
    conversation = admin_service.get_conversation_content(conversation_id,username)
    return ResponseGenral(
        code=200,
        message="返回对话信息",
        data=[conversation]
    )

# 获取用户知识库信息
@router.get("/user_knowledge_base/{username}", response_model=ResponseGenral)
async def get_user_knowledge_base(username: str, s_username: str = Depends(get_is_admin)):
    admin_service = AdminService()
    self_username = s_username.data[0]['username']
    user_knowledge_base = admin_service.get_user_knowledge_base(username,self_username)
    return ResponseGenral(
        code=200,
        message="返回用户知识库信息",
        data=[user_knowledge_base]
    )
@router.get("/user_knowledge_base/{username}/{knowledge_base_id}", response_model=ResponseGenral)
async def get_knowledge_base(username:str,knowledge_base_id: str, username_s: str = Depends(get_is_admin)):
    self_username = username_s.data[0]['username']
    admin_service = AdminService()
    knowledge_base = admin_service.get_knowledge_base(username,knowledge_base_id,self_username)
    return ResponseGenral(
        code=200,
        message="返回用户知识库信息",
        data=[knowledge_base]
    )
    
# 删除用户 (路径保持一致，使用服务层更新后的逻辑)
@router.delete("/user/{target_username}", response_model=ResponseGenral)
async def delete_user(target_username:str, username_s: str = Depends(get_is_admin)):
    self_username = username_s.data[0]['username']
    admin_service = AdminService()
    status =  admin_service.delete_user(target_username, self_username)
    if status == False:
        # 根据失败原因返回更具体的错误信息
        if target_username == 'admin':
            raise HTTPException(status_code=403, detail="Cannot delete the admin user")
        user_info = MysqlClient().db.query(UserInfo).filter(UserInfo.username == target_username).first()
        if user_info and user_info.is_admin and self_username != 'admin':
             raise HTTPException(status_code=403, detail="Permission denied to delete another admin")
        if not user_info:
             raise HTTPException(status_code=404, detail="User not found")

        raise HTTPException(status_code=400, detail="删除用户失败") # 其他原因
    return ResponseGenral(
        code=200,
        message="删除用户成功",
        data={} # 返回空 data
    )
    
# 删除用户对话
@router.delete("/user_conversation/{username}/{conversation_id}", response_model=ResponseGenral)
async def delete_user_conversation(username:str,conversation_id:str, username_s: str = Depends(get_is_admin)):
    self_username = username_s.data[0]['username']
    admin_service = AdminService()
    status =  admin_service.delete_user_conversation(username,conversation_id,self_username)
    if status == False:
        return ResponseGenral(
            code=400,
            message="删除用户对话失败,权限不够",
            data=[]
        )
    return ResponseGenral(
        code=200,
        message="删除用户对话成功",
        data=[]
    )
    
# 删除用户知识库
@router.delete("/user_knowledge_base/{username}/{knowledge_base_id}", response_model=ResponseGenral)
async def delete_user_knowledge_base(username:str,knowledge_base_id:str, username_s: str = Depends(get_is_admin)):
    self_username = username_s.data[0]['username']
    admin_service = AdminService()
    status = admin_service.delete_user_knowledge_base(username,knowledge_base_id,self_username)
    if status == False:
        return ResponseGenral(
            code=400,
            message="删除用户知识库失败,权限不够",
            data=[]
        )
    return ResponseGenral(
        code=200,
        message="删除用户知识库成功",
        data=[]
    )
    
# 授予用户管理员权限
@router.post("/grant_admin/{username}", response_model=ResponseGenral)
async def grant_admin(username:str,user: str = Depends(get_is_admin)):
    admin_service = AdminService()
    status = admin_service.grant_user_admin(username,user)
    if status == False:
        return ResponseGenral(
            code=400,
            message="授予用户管理员权限失败,权限不够",
            data=[]
        )
        
    return ResponseGenral(
        code=200,
        message="授予用户管理员权限成功",
        data=[]
    )
    
# 撤销用户管理员权限
@router.post("/revoke_admin/{username}", response_model=ResponseGenral)
async def revoke_admin(username:str,user: str = Depends(get_is_admin)):
    admin_service = AdminService()
    status = admin_service.revoke_user_admin(username,user)
    if status == False:
        return ResponseGenral(
            code=400,
            message="撤销用户管理员权限失败,权限不够",
            data=[]
        )
    return ResponseGenral(
        code=200,
        message="撤销用户管理员权限成功",
        data=[]
    )

@router.get("/me")
def read_users_me(token: str = Depends(get_is_admin)):
    return token

# 获取系统资源使用情况
@router.get("/system_resources", response_model=ResponseGenral)
async def get_system_resources(username: str = Depends(get_is_admin)):
    admin_service = AdminService()
    resources = admin_service.get_system_resources()
    return ResponseGenral(
        code=200,
        message="获取系统资源使用情况成功",
        data=[resources]
    )

# 获取用户增长趋势
@router.get("/user_growth", response_model=ResponseGenral)
async def get_user_growth(
    period: str = Query("month", description="时间段，如'month'或'day'"), 
    count: int = Query(7, description="返回数据点数量"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    growth_data = admin_service.get_user_growth(period, count)
    return ResponseGenral(
        code=200,
        message="获取用户增长趋势成功",
        data=[growth_data]
    )

# 获取对话量趋势
@router.get("/conversation_trend", response_model=ResponseGenral)
async def get_conversation_trend(
    period: str = Query("month", description="时间段，如'month'或'day'"), 
    count: int = Query(7, description="返回数据点数量"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    trend_data = admin_service.get_conversation_trend(period, count)
    return ResponseGenral(
        code=200,
        message="获取对话量趋势成功",
        data=[trend_data]
    )

# 获取系统最近活动
@router.get("/recent_activities", response_model=ResponseGenral)
async def get_recent_activities(
    limit: int = Query(5, description="返回的活动条数"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    activities = admin_service.get_recent_activities(limit)
    return ResponseGenral(
        code=200,
        message="获取系统最近活动成功",
        data=[activities]
    )

# 获取活跃用户统计
@router.get("/active_users", response_model=ResponseGenral)
async def get_active_users(
    period: str = Query("daily", description="活跃周期，如'daily'或'monthly'"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    active_users = admin_service.get_active_users(period)
    return ResponseGenral(
        code=200,
        message="获取活跃用户统计成功",
        data=[active_users]
    )

# ----------- LLM配置管理接口 -----------

# 获取所有LLM配置
@router.get("/llm_configs", response_model=LLMConfigListResponse)
async def get_llm_configs(username: str = Depends(get_is_admin)):
    admin_service = AdminService()
    configs = admin_service.get_llm_configs()
    return LLMConfigListResponse(
        code=200,
        message="获取LLM配置列表成功",
        data=configs
    )

# 获取单个LLM配置
@router.get("/llm_configs/{config_id}", response_model=ResponseGenral)
async def get_llm_config(
    config_id: int = Path(..., description="配置ID"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    config = admin_service.get_llm_config(config_id)
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="找不到指定的LLM配置"
        )
        
    return ResponseGenral(
        code=200,
        message="获取LLM配置成功",
        data=[config]
    )

# 创建LLM配置
@router.post("/llm_configs", response_model=ResponseGenral)
async def create_llm_config(
    config_data: LLMConfigCreate = Body(...),
    username: str = Depends(get_is_admin)
):
    try:
        admin_service = AdminService()
        config = admin_service.create_llm_config(config_data.dict())
        
        return ResponseGenral(
            code=200,
            message="创建LLM配置成功",
            data=[config]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建LLM配置失败: {str(e)}"
        )

# 更新LLM配置
@router.put("/llm_configs/{config_id}", response_model=ResponseGenral)
async def update_llm_config(
    config_id: int = Path(..., description="配置ID"),
    config_data: LLMConfigUpdate = Body(...),
    username: str = Depends(get_is_admin)
):
    try:
        admin_service = AdminService()
        config = admin_service.update_llm_config(config_id, config_data.dict())
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="找不到指定的LLM配置"
            )
            
        return ResponseGenral(
            code=200,
            message="更新LLM配置成功",
            data=[config]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新LLM配置失败: {str(e)}"
        )

# 删除LLM配置
@router.delete("/llm_configs/{config_id}", response_model=ResponseGenral)
async def delete_llm_config(
    config_id: int = Path(..., description="配置ID"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    success = admin_service.delete_llm_config(config_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="找不到指定的LLM配置"
        )
        
    return ResponseGenral(
        code=200,
        message="删除LLM配置成功",
        data={}
    )

# ----------- Embedding模型配置管理接口 -----------

# 获取所有Embedding配置
@router.get("/embedding_configs", response_model=EmbeddingConfigListResponse)
async def get_embedding_configs(username: str = Depends(get_is_admin)):
    admin_service = AdminService()
    configs = admin_service.get_embedding_configs()
    return EmbeddingConfigListResponse(
        code=200,
        message="获取Embedding配置列表成功",
        data=configs
    )

# 获取单个Embedding配置
@router.get("/embedding_configs/{config_id}", response_model=ResponseGenral)
async def get_embedding_config(
    config_id: int = Path(..., description="配置ID"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    config = admin_service.get_embedding_config(config_id)
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="找不到指定的Embedding配置"
        )
        
    return ResponseGenral(
        code=200,
        message="获取Embedding配置成功",
        data=[config]
    )

# 创建Embedding配置
@router.post("/embedding_configs", response_model=ResponseGenral)
async def create_embedding_config(
    config_data: EmbeddingConfigCreate = Body(...),
    username: str = Depends(get_is_admin)
):
    try:
        admin_service = AdminService()
        config = admin_service.create_embedding_config(config_data.dict())
        
        return ResponseGenral(
            code=200,
            message="创建Embedding配置成功",
            data=[config]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建Embedding配置失败: {str(e)}"
        )

# 更新Embedding配置
@router.put("/embedding_configs/{config_id}", response_model=ResponseGenral)
async def update_embedding_config(
    config_id: int = Path(..., description="配置ID"),
    config_data: EmbeddingConfigUpdate = Body(...),
    username: str = Depends(get_is_admin)
):
    try:
        admin_service = AdminService()
        config = admin_service.update_embedding_config(config_id, config_data.dict(exclude_unset=True))
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail="找不到指定的Embedding配置"
            )
            
        return ResponseGenral(
            code=200,
            message="更新Embedding配置成功",
            data=[config]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"更新Embedding配置失败: {str(e)}"
        )

# 删除Embedding配置
@router.delete("/embedding_configs/{config_id}", response_model=ResponseGenral)
async def delete_embedding_config(
    config_id: int = Path(..., description="配置ID"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    success = admin_service.delete_embedding_config(config_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="找不到指定的Embedding配置"
        )
        
    return ResponseGenral(
        code=200,
        message="删除Embedding配置成功",
        data={}
    )

# ---------- 默认模型配置管理接口 ----------

# 设置默认LLM模型配置
@router.post("/llm_configs/{config_id}/set_default_chat", response_model=ResponseGenral)
async def set_default_llm_config(
    config_id: int = Path(..., description="配置ID"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    config = admin_service.set_default_llm_chat_config(config_id)
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="找不到指定的LLM配置"
        )
        
    return ResponseGenral(
        code=200,
        message="设置默认LLM配置成功",
        data=[config]
    )

@router.post("/llm_configs/{config_id}/set_default_splitter", response_model=ResponseGenral)
async def set_default_llm_config(
    config_id: int = Path(..., description="配置ID"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    config = admin_service.set_default_llm_splitter_config(config_id)
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="找不到指定的LLM配置"
        )
        
    return ResponseGenral(
        code=200,
        message="设置默认LLM配置成功",
        data=[config]
    )

# 设置默认Embedding模型配置
@router.post("/embedding_configs/{config_id}/set_default", response_model=ResponseGenral)
async def set_default_embedding_config(
    config_id: int = Path(..., description="配置ID"),
    username: str = Depends(get_is_admin)
):
    admin_service = AdminService()
    config = admin_service.set_default_embedding_config(config_id)
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="找不到指定的Embedding配置"
        )
        
    return ResponseGenral(
        code=200,
        message="设置默认Embedding配置成功",
        data=[config]
    )

# 获取指定供应商的默认LLM配置
@router.get("/llm_configs/default/{vendor_type}", response_model=ResponseGenral)
async def get_default_llm_config(
    vendor_type: str = Path(..., description="供应商类型"),
    username: str = Depends(get_is_admin)
):
    try:
        admin_service = AdminService()
        config = admin_service.get_default_llm_config(vendor_type)
        
        if not config:
            return ResponseGenral(
                code=404,
                message=f"未找到{vendor_type}的默认LLM配置",
                data=[]
            )
            
        return ResponseGenral(
            code=200,
            message="获取默认LLM配置成功",
            data=[config]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# 获取指定供应商的默认Embedding配置
@router.get("/embedding_configs/default/{vendor_type}", response_model=ResponseGenral)
async def get_default_embedding_config(
    vendor_type: str = Path(..., description="供应商类型"),
    username: str = Depends(get_is_admin)
):
    try:
        admin_service = AdminService()
        config = admin_service.get_default_embedding_config(vendor_type)
        
        if not config:
            return ResponseGenral(
                code=404,
                message=f"未找到{vendor_type}的默认Embedding配置",
                data=[]
            )
            
        return ResponseGenral(
            code=200,
            message="获取默认Embedding配置成功",
            data=[config]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
