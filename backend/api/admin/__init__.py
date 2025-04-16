"""
后台管理员部分的路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
import hashlib
import jwt
import datetime
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config.config_info import settings
from core.database.mysql_client import MysqlClient
from core.database.models import UserInfo
from core.utils.utils import get_is_admin

from services.admin.admin_service  import AdminService
from .admin import (ResponseGenral,
                    DeleteUserConversationRequest,
                    DeleteUserKnowledgeBaseRequest,
                    DeleteUserRequest,
                    GrantAdminRequest,
                    RevokeAdminRequest
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

# 获取用户
@router.get("/users", response_model=ResponseGenral)
async def get_users_conversation(username: str = Depends(get_is_admin)):
    admin_service = AdminService()
    users = admin_service.get_all_users()
    return ResponseGenral(
        code=200,
        message="返回用户对话信息",
        data=[users]
    )

# 根据用户名获取对话列表
@router.get("/user_conversation/{username}", response_model=ResponseGenral)
async def get_user_conversation(username: str, s_username: str = Depends(get_is_admin)):
    admin_service = AdminService()
    user_conversation = admin_service.get_user_conversation(username,s_username)
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
    user_knowledge_base = admin_service.get_user_knowledge_base(username,s_username)
    return ResponseGenral(
        code=200,
        message="返回用户知识库信息",
        data=[user_knowledge_base]
    )
@router.get("/user_knowledge_base/{username}/{knowledge_base_id}", response_model=ResponseGenral)
async def get_knowledge_base(username:str,knowledge_base_id: str, username_s: str = Depends(get_is_admin)):
    admin_service = AdminService()
    knowledge_base = admin_service.get_knowledge_base(username,knowledge_base_id,username_s)
    return ResponseGenral(
        code=200,
        message="返回用户知识库信息",
        data=[knowledge_base]
    )
    
# 删除用户
@router.delete("/user/{username}", response_model=ResponseGenral)
async def delete_user(username:str, username_s: str = Depends(get_is_admin)):
    admin_service = AdminService()
    status =  admin_service.delete_user(username,username_s)
    if status == False:
        return ResponseGenral(
            code=400,
            message="删除用户失败,权限不够",
            data=[]
        )
    return ResponseGenral(
        code=200,
        message="删除用户成功",
        data=[]
    )
    
# 删除用户对话
@router.delete("/user_conversation/{username}/{conversation_id}", response_model=ResponseGenral)
async def delete_user_conversation(username:str,conversation_id:str, username_s: str = Depends(get_is_admin)):
    admin_service = AdminService()
    status =  admin_service.delete_user_conversation(username,conversation_id,username_s)
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
    admin_service = AdminService()
    status = admin_service.delete_user_knowledge_base(username,knowledge_base_id,username_s)
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


