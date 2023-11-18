import logging, hashlib

from fastapi import APIRouter
from pydantic import BaseModel
from models.server import Server
from util.aes import encrypt_aes, decrypt_aes
from util.yaml_util import read_yaml
from .base import resp_200, resp_400
from typing import List

server = APIRouter()


class ServerModelList(BaseModel):
    hostname: str
    ip: str
    password: str

    class Config:
        from_orm = True
        from_attributes = True


@server.get('/list', response_model=List[ServerModelList])
async def get_server():
    try:
        servers = await Server.all().order_by('id')
    except Exception as e:
        # 处理异常，可以打印或记录错误信息
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='查询错误')
    response_data = [ServerModelList.from_orm(server).dict() for server in servers]
    return resp_200(data=response_data)


class AddServerModel(BaseModel):
    hostname: str
    ip: str
    password: str


@server.put('/add')
async def add_server(item: AddServerModel):
    data = {
        "hostname": item.hostname,
        "ip": item.ip,
        "password": item.password,
    }
    data["password"] = encrypt_aes(data["password"], str(read_yaml('aes_key', 'config')))
    try:
        await Server.create(**data)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='插入错误')
    return resp_200(message='插入成功')


@server.delete('/delete/{server_id}')
async def delete_server(server_id: int):
    try:
        await Server.get(id=server_id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这条数据')
    try:
        await Server.filter(id=server_id).delete()
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='删除错误')
    return resp_200(message='删除成功')


class EditServerModel(BaseModel):
    id: int
    hostname: str
    ip: str
    password: str


@server.post('/edit')
async def edit_server(item: EditServerModel):
    data = {
        "id": item.id,
        "hostname": item.hostname,
        "ip": item.ip,
        "password": item.password,
    }
    try:
        old_data = await Server.get(id=data['id'])
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有查到该条数据')
    old_data.hostname = data['hostname']
    old_data.password = encrypt_aes(data["password"], str(read_yaml('aes_key', 'config')))
    old_data.ip = data['ip']
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='修改错误')
    return resp_200(message='修改成功')