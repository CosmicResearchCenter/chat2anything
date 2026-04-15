from pydantic import BaseModel, field_validator
from typing import Any,List,Dict
import re

class UsernameValidator(BaseModel):
    username: str
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v:
            raise ValueError('用户名不能为空')
        if len(v) < 3 or len(v) > 20:
            raise ValueError('用户名长度必须在3-20个字符之间')
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v

class LoginRequest(UsernameValidator):
    password: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    code: int
    data:AccessToken
    message: str



class SignUpRequest(UsernameValidator):
    password: str

class SignUpAdminRequest(UsernameValidator):
    password: str
    admin_key: str


class SignUpResponse(BaseModel):
    code: int
    data:AccessToken
    message: str

class TestResponse(BaseModel):
    code: int
    data: List[Dict[str,Any]]
    message: str