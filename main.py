# -*- coding: utf-8 -*-
# @Author : buyfakett
# @Time : 2023/11/9 15:36


import logging
import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from api.domain import domain
from api.event_startup import event_startup
from api.server import server
from api.ssl import ssl
from settings import TORTOISE_ORM
from test.test import test1

# 日志记录器
logger = logging.getLogger()

# 设置日志级别，只有大于等于这个级别的日志才能输出
logger.setLevel(logging.INFO)

# 设置日志格式
formatter = logging.Formatter(
    "[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]    %(message)s"
)

# 输出到控制台
to_console = logging.StreamHandler()
to_console.setFormatter(formatter)
logger.addHandler(to_console)

app = FastAPI(
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    title="auto_ssl_push_svn",
    version="0.1.0",
    description="自动获取ssl证书，并推送到svn",
    contact={
        "name": "buyfakett",
        "url": "https://github.com/buyfakett",
        "email": "buyfakett@vip.qq.com",
    }
)

register_tortoise(
    app=app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 如果数据库为空，自动生成对应表单，生产环境不能开
    add_exception_handlers=True,  # 调试消息，生产环境不能开
)

# app.include_router(test1, prefix='/api/test', tags=['测试接口'])
app.include_router(domain, prefix='/api/domain', tags=['域名'])
app.include_router(server, prefix='/api/server', tags=['服务器'])
app.include_router(ssl, prefix='/api/ssl', tags=['ssl证书'])


@app.on_event("startup")
async def startup_event():
    event_startup()


if __name__ == "__main__":
    uvicorn.run(
        "setup:app",
        port=8000,
        reload=True,
    )
