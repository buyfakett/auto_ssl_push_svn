import logging

from fastapi import APIRouter
from pydantic import BaseModel
from models.ssl import Ssl
from models.first_domain import First_domain
from models.server import Server
from .base import resp_200, resp_400
from typing import List, Optional
from datetime import datetime

ssl = APIRouter()


class SslModelList(BaseModel):
    id: int
    first_domain_id: int
    server_id: int
    certificate_domain: str
    webroot: str
    register_time: Optional[datetime]
    exp_time: Optional[datetime]
    status: int

    class Config:
        from_orm = True
        from_attributes = True


@ssl.get('/list', response_model=List[SslModelList], summary='获取证书列表')
async def get_ssl():
    try:
        ssls = await Ssl.all().order_by('id')
    except Exception as e:
        # 处理异常，可以打印或记录错误信息
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='查询错误')
    response_data = [SslModelList.from_orm(ssl).dict() for ssl in ssls]
    return resp_200(data=response_data)


class AddSslModel(BaseModel):
    first_domain_id: int
    server_id: int
    certificate_domain: str
    webroot: str
    status: int = 2


@ssl.put('/add', summary='添加证书')
async def add_ssl(item: AddSslModel):
    data = {
        "first_domain_id": item.first_domain_id,
        "server_id": item.server_id,
        "certificate_domain": item.certificate_domain,
        "webroot": item.webroot,
        "status": item.status,
    }
    try:
        await First_domain.get(id=data['first_domain'])
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这个一级域名')
    try:
        await Server.get(id=data['server_id'])
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='没有这个服务器')
    try:
        await Ssl.create(**data)
    except Exception as e:
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='插入错误')
    return resp_200(message='插入成功')


@ssl.delete('/delete/{ssl_id}', summary='删除证书')
async def delete_ssl(ssl_id: int):
    try:
        await Ssl.get(id=ssl_id)
    except Exception as e:
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='没有这条数据')
    try:
        await Ssl.filter(id=ssl_id).delete()
    except Exception as e:
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='删除错误')
    return resp_200(message='删除成功')


class EditSslModel(BaseModel):
    id: int
    first_domain_id: Optional[int]
    server_id: Optional[int]
    certificate_domain: Optional[str]
    webroot: Optional[str]
    status: Optional[int]


@ssl.post('/edit', summary='编辑证书')
async def edit_ssl(item: EditSslModel):
    try:
        old_data = await Ssl.get(id=item.id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有查到该条数据')
    old_data.first_domain_id = item.first_domain_id
    old_data.server_id = item.server_id
    old_data.certificate_domain = item.certificate_domain
    old_data.webroot = item.webroot
    old_data.status = item.status
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='修改错误')
    return resp_200(message='修改成功')
