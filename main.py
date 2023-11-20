# -*- coding: utf-8 -*-
# @Author : buyfakett
# @Time : 2023/11/9 15:36


from fastapi import FastAPI
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from settings import TORTOISE_ORM
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

from api.domain import domain
from api.server import server
from api.ssl import ssl

app = FastAPI()
register_tortoise(
    app=app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 如果数据库为空，自动生成对应表单，生产环境不能开
    add_exception_handlers=True,  # 调试消息，生产环境不能开
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="auto_ssl_push_svn",
        version="0.1.0",
        description="自动获取ssl证书，并推送到svn",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/api/docs")
async def get_documentation():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="auto_ssl_push_svn")


@app.get("/api/openapi.json")
async def get_open_api_endpoint():
    return app.openapi()


app.include_router(domain, prefix='/api/domain', tags=['域名'])
app.include_router(server, prefix='/api/server', tags=['服务器'])
app.include_router(ssl, prefix='/api/ssl', tags=['ssl证书'])

if __name__ == "__main__":
    uvicorn.run(
        "setup:app",
        port=8000,
        reload=True,
    )
