from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from api import AccountRouter,ChatRouter,KnowledgeBaseRouter,AdminRouter
from core.database.mysql_client import MysqlClient
from core.database.models import Base
origins = [
    "*"
]


from fastapi.staticfiles import StaticFiles

import uvicorn

from pathlib import Path

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # 允许的域名
    allow_credentials=True,           # 允许携带凭证
    allow_methods=["*"],              # 允许的 HTTP 方法，如 GET, POST 等
    allow_headers=["*"],              # 允许的请求头
)
BASE_DIR = Path(__file__).resolve().parent
# UPLOAD_DIR = BASE_DIR / "documents_stored"

# from config.config_info import set_docs_path
# import config.config_info
# set_docs_path(UPLOAD_DIR)

router = APIRouter()
router.include_router(AccountRouter, prefix="/account", tags=["mark", "account"])
router.include_router(ChatRouter, prefix="/chat", tags=["mark", "chat"])
router.include_router(KnowledgeBaseRouter, prefix="/knowledgebase", tags=["mark", "knowledgebase"])
router.include_router(AdminRouter, prefix="/admin", tags=["mark", "admin"])

app.include_router(router, prefix="/v1/api/mark", tags=["mark"])
@app.on_event("startup")
async def startup():
    mysql_client = MysqlClient()
    # 使用同步方式创建表
    with mysql_client.engine.begin() as conn:
        conn.run_sync(Base.metadata.create_all)
if __name__ == "__main__":
  
#   print(config.config.DOCS_PATH)
  config = uvicorn.Config("main:app", host="0.0.0.0", port=9988, reload=True)
  server = uvicorn.Server(config)
  server.run()