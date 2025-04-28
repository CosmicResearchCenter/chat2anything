from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from core.database.mysql_client import MysqlClient
from core.database.models import Base
from config.config_info import settings
import uvicorn
from pathlib import Path

app = FastAPI()

# 添加CORS中间件（移到这里）
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 先创建表
@app.on_event("startup")
async def startup():
    try:
        user = settings.MYSQL_USER
        password = settings.MYSQL_PASSWORD
        ip = settings.MYSQL_IP
        port = settings.MYSQL_PORT
        basename = settings.MYSQL_BASE

        # 数据库设置
        DATABASE_URL = f"mysql+pymysql://{user}:{password}@{ip}:{port}/{basename}"
        mysql_client = MysqlClient(database_url=DATABASE_URL)
        Base.metadata.create_all(mysql_client.engine)
        print("数据库表创建成功")
    except Exception as e:
        print(f"数据库表创建失败: {e}")

# 延迟导入API路由
@app.on_event("startup")
async def setup_routes():
    from api import AccountRouter, ChatRouter, KnowledgeBaseRouter, AdminRouter
    
    router = APIRouter()
    router.include_router(AccountRouter, prefix="/account", tags=["mark", "account"])
    router.include_router(ChatRouter, prefix="/chat", tags=["mark", "chat"])
    router.include_router(KnowledgeBaseRouter, prefix="/knowledgebase", tags=["mark", "knowledgebase"])
    router.include_router(AdminRouter, prefix="/admin", tags=["mark", "admin"])
    
    app.include_router(router, prefix="/v1/api/mark", tags=["mark"])

if __name__ == "__main__":
    config = uvicorn.Config("main:app", host="0.0.0.0", port=9988, reload=True)
    server = uvicorn.Server(config)
    server.run()