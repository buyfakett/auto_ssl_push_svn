# -*- coding: utf-8 -*-
# @Author : buyfakett
# @Time : 2023/11/9 15:36
import logging
import os

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pyresp.pyresp import resp_200
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from api.db_ask_ssl import db_ask_ssl
from api.domain import domain
from api.event_startup import event_startup
from api.server import server
from api.ssl import ssl
from api.user import user
from settings import TORTOISE_ORM

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

# 初始化文件夹
for init_dir in ['web/static', 'web/admin']:
    if not os.path.exists(init_dir):
        os.makedirs(init_dir)

with open(os.getcwd() + '/version.py', encoding="utf-8") as f:
    version_var = {}
    exec(f.read(), version_var)
    VERSION = version_var['VERSION']

logging.info(f'当前服务端版本为：v{VERSION}')

app = FastAPI(
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    title="auto_ssl_push_svn",
    version=VERSION,
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

app.include_router(user, prefix='/api/user', tags=['用户'])
app.include_router(domain, prefix='/api/domain', tags=['域名'])
app.include_router(server, prefix='/api/server', tags=['服务器'])
app.include_router(ssl, prefix='/api/ssl', tags=['ssl证书'])
app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/admin", StaticFiles(directory="web/admin"), name="admin")

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 首页跳转
@app.get('/')
async def main():
    return RedirectResponse('/admin/index.html')


@app.get('/api/getServerVersion')
async def get_server_version():
    return resp_200(data={'version': VERSION})


@app.middleware("http")
def add_process_time_header(request: Request, call_next):
    uri = request.url.path
    if 'api' in uri:
        method = request.method
        url = request.base_url
        logging.info(
            f'\n请求方式：{method}\n请求地址：{url}\n请求接口：{uri}\n请求头：{request.headers}\n请求入参：{request.json() if method == "POST" else None}\n请求参数：{request.query_params}')
    response = call_next(request)
    return response


scheduler = AsyncIOScheduler()


# 添加任务到定时调度器
@scheduler.scheduled_job('cron', hour=11, minute=0)
async def cron_job():
    await db_ask_ssl()


@app.on_event("startup")
async def startup_event():
    await event_startup()
    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


if __name__ == "__main__":
    uvicorn.run(
        "setup:app",
        port=8000,
        reload=True,
    )
