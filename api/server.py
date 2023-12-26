import logging

from fastapi import APIRouter
from pydantic import BaseModel
from models.server import Server
from tt_util.aes_util import encrypt_aes, decrypt_aes
from tt_util.yaml_util import read_yaml
from .base import resp_200, resp_400
from typing import List, Optional

server = APIRouter()


class ServerModelList(BaseModel):
    id: int
    ssl_id: Optional[str]
    hostname: str
    ip: str
    password: str

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
    data_list = []
    for server in servers:
        server_dict = ServerModelList.from_orm(server).dict()
        # 在这里修改字段
        server_dict['password'] = decrypt_aes(server_dict["password"], str(read_yaml('aes_key', 'config')))
        data_list.append(server_dict)
    response_data = {
        'items': data_list,
        'total': len(data_list)
    }
    return resp_200(data=response_data, message='查询成功')


class AddServerModel(BaseModel):
    hostname: str
    ip: str
    password: str


@server.put('/add', summary='添加服务器')
async def add_server(item: AddServerModel):
    data = {
        "ssl_id": item.ssl_id,
        "hostname": item.hostname,
        "ip": item.ip,
        "password": item.password,
    }
    data["password"] = encrypt_aes(data["password"], str(read_yaml('aes_key', 'config')))
    try:
        add_data = await Server.create(**data)
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='插入错误')
    resp_data = {
        'id': add_data.id,
        "ssl_id": add_data.ssl_id,
        'hostname': add_data.hostname,
        'ip': add_data.ip,
        'password': item.password,
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
    hostname: Optional[str]
    ip: Optional[str]
    password: Optional[str]


@server.post('/edit', summary='编辑服务器')
async def edit_server(item: EditServerModel):
    try:
        old_data = await Server.get(id=item.id)
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='没有查到该条数据')
    old_data.hostname = item.hostname
    old_data.ip = item.ip
    old_data.ssl_id = item.ssl_id
    old_data.password = encrypt_aes(item.password, str(read_yaml('aes_key', 'config')))
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching server: {e}")
        return resp_400(message='修改错误')
    retrieved_data = await Server.get_or_none(id=item.id)  # 使用刚刚创建的数据的ID
    resp_data = {
        'id': retrieved_data.id,
        "ssl_id": retrieved_data.ssl_id,
        'hostname': retrieved_data.hostname,
        'ip': retrieved_data.ip,
        'password': item.password,
    }
    return resp_200(data=resp_data, message='修改成功')
