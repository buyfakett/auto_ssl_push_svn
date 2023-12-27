import logging

from fastapi import APIRouter
from pydantic import BaseModel
from models.ssl import Ssl
from models.first_domain import first_domain
from models.server import Server
from .base import resp_200, resp_400
from typing import List, Optional
from datetime import datetime

ssl = APIRouter()


class SslModelList(BaseModel):
    id: int
    first_domain_id: int
    server_id: int
    server_ids: List[int]
    certificate_domain: str
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
    data_list = [SslModelList.from_orm(ssl).dict() for ssl in ssls]
    response_data = {
        'items': data_list,
        'total': len(data_list)
    }
    return resp_200(data=response_data, message='查询成功')


class AddSslModel(BaseModel):
    first_domain_id: int
    server_id: int
    server_ids: List[int]
    certificate_domain: str
    status: Optional[int] = 2


@ssl.put('/add', summary='添加证书')
async def add_ssl(item: AddSslModel):
    data = {
        "first_domain_id": item.first_domain_id,
        "server_id": item.server_id,
        "server_ids": item.server_ids,
        "certificate_domain": item.certificate_domain,
        "status": item.status,
    }
    try:
        await first_domain.get(id=item.first_domain_id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这个一级域名')
    try:
        await Server.get(id=item.server_id)
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='没有这个服务器')
    existing_ids = await Server.filter(id__in=item.server_ids).values_list('id', flat=True)
    if len(existing_ids) != len(item.server_ids):
        # 如果查询出来的 ID 数量和待查询的 ID 数量相等，说明所有 ID 都存在
        return resp_400(message='服务器的数组错误')
    else:
        try:
            add_data = await Ssl.create(**data)
        except Exception as e:
            logging.error(f"Error fetching ssl: {e}")
            return resp_400(message='插入错误')
        resp_data = {
            'id': add_data.id,
            'first_domain_id': add_data.first_domain_id,
            'server_id': add_data.server_id,
            'server_ids': add_data.server_ids,
            'certificate_domain': add_data.certificate_domain,
            'status': add_data.status,
        }
        return resp_200(data=resp_data, message='新增成功')


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
    first_domain_id: int
    server_id: int
    server_ids: List[int]
    certificate_domain: str
    status: int


@ssl.post('/edit', summary='编辑证书')
async def edit_ssl(item: EditSslModel):
    try:
        old_data = await Ssl.get(id=item.id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有查到该条数据')
    try:
        await first_domain.get(id=item.first_domain_id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这个一级域名')
    try:
        await Server.get(id=item.server_id)
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='没有这个服务器')
    old_data.first_domain_id = item.first_domain_id
    old_data.server_id = item.server_id
    old_data.certificate_domain = item.certificate_domain
    old_data.server_ids = item.server_ids
    old_data.status = item.status
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='修改错误')
    retrieved_data = await Ssl.get_or_none(id=item.id)  # 使用刚刚创建的数据的ID
    resp_data = {
        'id': retrieved_data.id,
        'first_domain_id': retrieved_data.first_domain_id,
        'server_id': retrieved_data.server_id,
        'server_ids': retrieved_data.server_ids,
        'certificate_domain': retrieved_data.certificate_domain,
        'status': retrieved_data.status
    }
    return resp_200(data=resp_data, message='修改成功')
