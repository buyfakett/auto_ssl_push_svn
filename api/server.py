import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from models.server import Server
from .base import resp_200, resp_400
from typing import List

from .oauth2 import verify_token

server = APIRouter(dependencies=[Depends(verify_token)])


class ServerModelList(BaseModel):
    id: int
    webroot: str
    hostname: str

    class Config:
        from_orm = True
        from_attributes = True


@server.get('/list', response_model=List[ServerModelList], summary='获取服务器列表')
async def get_server():
    try:
        servers = await Server.all().order_by('id')
    except Exception as e:
        # 处理异常，可以打印或记录错误信息
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='查询错误')
    data_list = [ServerModelList.from_orm(server).dict() for server in servers]
    response_data = {
        'items': data_list,
        'total': len(data_list)
    }
    return resp_200(data=response_data, message='查询成功')


class AddServerModel(BaseModel):
    webroot: str
    hostname: str


@server.put('/add', summary='添加服务器')
async def add_server(item: AddServerModel):
    data = {
        "webroot": item.webroot,
        "hostname": item.hostname,
    }
    try:
        add_data = await Server.create(**data)
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='插入错误')
    resp_data = {
        'id': add_data.id,
        "webroot": add_data.webroot,
        'hostname': add_data.hostname,
    }
    return resp_200(data=resp_data, message='新增成功')


@server.delete('/delete/{server_id}', summary='删除服务器')
async def delete_server(server_id: int):
    try:
        await Server.get(id=server_id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这条数据')
    try:
        await Server.filter(id=server_id).delete()
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='删除错误')
    return resp_200(message='删除成功')


class EditServerModel(BaseModel):
    id: int
    webroot: str
    hostname: str


@server.post('/edit', summary='编辑服务器')
async def edit_server(item: EditServerModel):
    try:
        old_data = await Server.get(id=item.id)
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='没有查到该条数据')
    old_data.hostname = item.hostname
    old_data.webroot = item.webroot
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='修改错误')
    retrieved_data = await Server.get_or_none(id=item.id)  # 使用刚刚创建的数据的ID
    resp_data = {
        'id': retrieved_data.id,
        "webroot": retrieved_data.webroot,
        'hostname': retrieved_data.hostname,
    }
    return resp_200(data=resp_data, message='修改成功')
