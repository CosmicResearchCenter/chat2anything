from pydantic import BaseModel
from typing import Any,List,Dict,Optional
class LoginRequest(BaseModel):
    username: str
    password: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    code: int
    message: str
    data: AccessToken



class SignUpRequest(BaseModel):
    username: str
    password: str
    invite_code: str  # 添加邀请码字段
    email: Optional[str] = None

class SignUpAdminRequest(BaseModel):
    username: str
    password: str
    admin_key: str


class SignUpResponse(BaseModel):
    code: int
    message: str
    data: AccessToken

class TestResponse(BaseModel):
    code: int
    data: List[Dict[str,Any]]
    message: str