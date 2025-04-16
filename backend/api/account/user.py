from pydantic import BaseModel
from typing import Any,List,Dict
class LoginRequest(BaseModel):
    username: str
    password: str

class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginResponse(BaseModel):
    code: int
    data:AccessToken
    message: str



class SignUpRequest(BaseModel):
    username: str
    password: str

class SignUpResponse(BaseModel):
    code: int
    data:AccessToken
    message: str

class TestResponse(BaseModel):
    code: int
    data: List[Dict[str,Any]]
    message: str