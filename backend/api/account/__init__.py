"""
用户管理部分的路由
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
from core.utils.utils import get_current_user
from api.account.user import (LoginRequest,LoginResponse,SignUpRequest,
                              SignUpResponse,AccessToken,SignUpAdminRequest)


SECRET_KEY = settings.SECRET_KEY
ADMIN_KEY = settings.ADMIN_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

# 加密密码
def get_password_hash(password):
    return pwd_context.hash(password)
# 验证密码
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=LoginResponse)
async def login(loginRequest: LoginRequest):
    mysql_client = MysqlClient()
    try:
        username = loginRequest.username
        password = loginRequest.password

        # Workaround: Explicitly select needed columns to avoid 'status' column error
        # Ideally, ensure the UserInfo model and database schema match.
        user_data = mysql_client.db.query(
            UserInfo.username,
            UserInfo.password,
            UserInfo.delete_sign
        ).filter(UserInfo.username == username).first()

        if not user_data:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        fetched_username, hashed_password, delete_sign = user_data

        if not verify_password(password, hashed_password):
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        # Use the fetched delete_sign value
        if delete_sign == True:
            raise HTTPException(status_code=400, detail="Account disabled")

        access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        # Use the fetched username for the token
        access_token = create_access_token(
            data={"sub": fetched_username}, expires_delta=access_token_expires
        )

        return LoginResponse(code=200, data=AccessToken(access_token=access_token,token_type="bearer"), message="Login Successful")
    finally:
        mysql_client.db.close()

@router.post("/signup", response_model=SignUpResponse)
def signup(signupRequest: SignUpRequest):
    mysql_client = MysqlClient()
    try:
        username = signupRequest.username
        password = signupRequest.password
        
        user = mysql_client.db.query(UserInfo).filter(UserInfo.username == username).first()
        if user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        hashed_password = get_password_hash(password)

        new_user = UserInfo(username=username, password=hashed_password,is_admin=False,delete_sign=False,create_time=datetime.datetime.now(),update_time=datetime.datetime.now())
        mysql_client.db.add(new_user)
        mysql_client.db.commit()
        mysql_client.db.refresh(new_user)

        access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": new_user.username}, expires_delta=access_token_expires
        )

        return SignUpResponse(code=200, data=AccessToken(access_token=access_token,token_type="bearer"), message="Sign Up Successful")
    finally:
        mysql_client.db.close()

@router.post("/signup_admin", response_model=SignUpResponse)
def signup(signupRequest: SignUpAdminRequest):
    mysql_client = MysqlClient()
    try:
        username = signupRequest.username
        password = signupRequest.password
        admin_key = signupRequest.admin_key
        if admin_key != ADMIN_KEY:
            raise HTTPException(status_code=400, detail="Invalid admin key")
        
        user = mysql_client.db.query(UserInfo).filter(UserInfo.username == username).first()
        if user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        hashed_password = get_password_hash(password)

        new_user = UserInfo(username=username, password=hashed_password,is_admin=True,delete_sign=False,create_time=datetime.datetime.now(),update_time=datetime.datetime.now())
        mysql_client.db.add(new_user)
        mysql_client.db.commit()
        mysql_client.db.refresh(new_user)

        access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": new_user.username}, expires_delta=access_token_expires
        )

        return SignUpResponse(code=200, data=AccessToken(access_token=access_token,token_type="bearer"), message="Sign Up Successful")
    finally:
        mysql_client.db.close()

# 获取当前用户信息
@router.get("/me")
def read_users_me(token: str = Depends(get_current_user)):
    return token