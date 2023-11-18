# -*- coding: utf-8 -*-
# @Author : buyfakett
# @Time : 2023/11/9 15:36


from fastapi import FastAPI
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM

# from api.domain import Domain

app = FastAPI()
register_tortoise(
    app=app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 如果数据库为空，自动生成对应表单，生产环境不能开
    add_exception_handlers=True,  # 调试消息，生产环境不能开
)
# app.include_router(domain, prefix='/api/domain', tags=['域名'])
# app.include_router(ssl, prefix='/api/ssl', tags=['ssl证书'])
# app.include_router(server, prefix='/api/server', tags=['服务器'])


if __name__ == "__main__":
    uvicorn.run(
        "setup:app",
        port=8000,
        reload=True,
    )
