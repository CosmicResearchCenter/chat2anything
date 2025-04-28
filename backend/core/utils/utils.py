import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config.config_info import settings
import jwt
import datetime
from pydantic import BaseModel
from passlib.context import CryptContext
from core.database.models import UserInfo,LLMProviderConfig,LLMVendorType,EmbeddingModelConfig,EmbeddingVendorType
from models.general_models import GenericResponse
from core.database.mysql_client import MysqlClient
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def generate_unique_filename(original_filename):
    # 获取文件扩展名
    extension = os.path.splitext(original_filename)[1]
    # 生成唯一的UUID
    unique_id = uuid.uuid4()
    # 组合唯一标识符和扩展名
    unique_filename = f"{unique_id}{extension}"
    return unique_filename

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    mysql_client = MysqlClient()
    user = mysql_client.db.query(UserInfo).filter(UserInfo.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Login")


    return username

async def get_is_admin(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    mysql_client = MysqlClient()
    user = mysql_client.db.query(UserInfo).filter(UserInfo.username == username).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not admin")
    if user.is_admin != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not admin")
    
    return GenericResponse(message="获取成功",code=200,data=[{'is_admin':user.is_admin,'username':user.username}])


def GetDeafultLLM()->LLMProviderConfig:
    db_client = MysqlClient()
    llm_config = db_client.db.query(LLMProviderConfig).filter(LLMProviderConfig.is_default == True).first()

    if llm_config is  None:
        return
    
    return llm_config

def GetDefaultEmbedding()->EmbeddingModelConfig:
    db_client = MysqlClient()

    embedding_config = db_client.db.query(EmbeddingModelConfig).filter(EmbeddingModelConfig.is_default == True).filter()

    if embedding_config is  None:
        return

    return embedding_config   