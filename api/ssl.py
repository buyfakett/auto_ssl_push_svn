import logging

from fastapi import APIRouter
from pydantic import BaseModel
from models.ssl import Ssl
from .base import resp_200, resp_400
from typing import List, Optional
from datetime import datetime

ssl = APIRouter()


class SslModelList(BaseModel):
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


@ssl.get('/list', response_model=List[SslModelList])
async def get_ssl():
    try:
        ssls = await Ssl.all().order_by('id')
    except Exception as e:
        # 处理异常，可以打印或记录错误信息
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='查询错误')
    response_data = [SslModelList.from_orm(ssl).dict() for ssl in ssls]
    return resp_200(data=response_data)


class AddSslModel(BaseModel):
    first_domain_id: int
    server_id: int
    certificate_domain: str
    webroot: str
    status: int = 2


@ssl.put('/add')
async def add_ssl(item: AddSslModel):
    data = {
        "first_domain_id": item.first_domain_id,
        "server_id": item.server_id,
        "certificate_domain": item.certificate_domain,
        "webroot": item.webroot,
        "status": item.status,
    }
    try:
        await Ssl.create(**data)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='插入错误')
    return resp_200(message='插入成功')


@ssl.delete('/delete/{ssl_id}')
async def delete_ssl(ssl_id: int):
    try:
        await Ssl.get(id=ssl_id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这条数据')
    try:
        await Ssl.filter(id=ssl_id).delete()
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='删除错误')
    return resp_200(message='删除成功')


class EditSslModel(BaseModel):
    id: int
    first_domain_id: int
    server_id: int
    certificate_domain: str
    webroot: str
    status: int


@ssl.post('/edit')
async def edit_ssl(item: EditSslModel):
    data = {
        "id": item.id,
        "first_domain_id": item.first_domain_id,
        "server_id": item.server_id,
        "certificate_domain": item.certificate_domain,
        "webroot": item.webroot,
        "status": item.status,
    }
    try:
        old_data = await Ssl.get(id=data['id'])
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有查到该条数据')
    old_data.first_domain_id = data['first_domain_id']
    old_data.server_id = data['server_id']
    old_data.certificate_domain = data['certificate_domain']
    old_data.webroot = data['webroot']
    old_data.status = data['status']
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='修改错误')
    return resp_200(message='修改成功')
