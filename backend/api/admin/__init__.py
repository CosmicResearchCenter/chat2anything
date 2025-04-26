"""
后台管理员部分的路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
import hashlib
import jwt
import datetime
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config.config_info import settings
from core.database.mysql_client import MysqlClient
from core.database.models import UserInfo
from core.utils.utils import get_is_admin
from typing import Optional
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
                    UpdateUserStatusRequest # 导入
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
