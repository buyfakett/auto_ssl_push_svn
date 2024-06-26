import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from models.ssl import Ssl
from models.first_domain import first_domain
from models.server import Server
from pyresp.pyresp import resp_200, resp_400
from typing import List, Optional
from datetime import datetime

from util.db_ask_ssl import db_ask_ssl
from pyoauth2_util.oauth2 import verify_token

ssl = APIRouter(dependencies=[Depends(verify_token)])


class SslModelList(BaseModel):
    id: int
    first_domain_id: int
    server_ids: str
    certificate_domain: str
    register_time: Optional[datetime]
    exp_time: Optional[datetime]
    percentage: Optional[int] = Field(0, alias="percentage")
    remainder_days: Optional[str] = Field(0, alias="remainder_days")
    status: int

    class Config:
        from_orm = True
        from_attributes = True


def serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    return dt.date().strftime('%Y-%m-%d') if dt else None


@ssl.get('/list', response_model=List[SslModelList], summary='获取证书列表')
async def get_ssl():
    try:
        ssls = await Ssl.all().order_by('id')
    except Exception as e:
        # 处理异常，可以打印或记录错误信息
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='查询错误')
    data_list = []
    # 获取当前时间
    current_time = datetime.now()
    for ssl in ssls:
        ssl_dict = SslModelList.from_orm(ssl).dict()
        # 序列化 datetime 字段
        ssl_dict['register_time'] = serialize_datetime(ssl_dict['register_time'])
        ssl_dict['exp_time'] = serialize_datetime(ssl_dict['exp_time'])
        if ssl_dict['register_time'] and ssl_dict['exp_time']:
            # 解析日期
            start_datetime = datetime.strptime(ssl_dict['register_time'], "%Y-%m-%d")
            end_datetime = datetime.strptime(ssl_dict['exp_time'], "%Y-%m-%d")
            # 计算日期差
            delta_days = (end_datetime - current_time).days + 1
            # 计算百分比
            percentage = "{:.0f}".format(delta_days / (end_datetime - start_datetime).days * 100)

            ssl_dict['percentage'] = percentage
            ssl_dict['remainder_days'] = delta_days
        else:
            ssl_dict['percentage'] = None
            ssl_dict['remainder_days'] = None
        data_list.append(ssl_dict)
    response_data = {
        'items': data_list,
        'total': len(data_list)
    }
    return resp_200(data=response_data, message='查询成功')


class AddSslModel(BaseModel):
    first_domain_id: int
    server_ids: List[int]
    certificate_domain: str
    status: Optional[int] = 2


@ssl.put('/add', summary='添加证书')
async def add_ssl(item: AddSslModel):
    try:
        await first_domain.get(id=item.first_domain_id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这个一级域名')
    existing_ids = await Server.filter(id__in=item.server_ids).values_list('id', flat=True)
    if len(existing_ids) != len(item.server_ids):
        # 如果查询出来的 ID 数量和待查询的 ID 数量相等，说明所有 ID 都存在
        return resp_400(message='服务器的数组错误')
    try:
        add_data = await Ssl.create(**item.dict())
    except Exception as e:
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='插入错误')
    resp_data = {
        'id': add_data.id,
        'first_domain_id': add_data.first_domain_id,
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
    server_ids: List[int]
    certificate_domain: str


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
    existing_ids = await Server.filter(id__in=item.server_ids).values_list('id', flat=True)
    if len(existing_ids) != len(item.server_ids):
        # 如果查询出来的 ID 数量和待查询的 ID 数量相等，说明所有 ID 都存在
        return resp_400(message='服务器的数组错误')
    old_data.first_domain_id = item.first_domain_id
    old_data.certificate_domain = item.certificate_domain
    old_data.server_ids = item.server_ids
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='修改错误')
    retrieved_data = await Ssl.get_or_none(id=item.id)  # 使用刚刚创建的数据的ID
    resp_data = {
        'id': retrieved_data.id,
        'first_domain_id': retrieved_data.first_domain_id,
        'server_ids': retrieved_data.server_ids,
        'certificate_domain': retrieved_data.certificate_domain,
        'status': retrieved_data.status
    }
    return resp_200(data=resp_data, message='修改成功')


class EditSslStatusModel(BaseModel):
    id: int
    status: int


@ssl.post('/edit_status', summary='编辑证书状态')
async def edit_status(item: EditSslStatusModel):
    try:
        old_data = await Ssl.get(id=item.id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有查到该条数据')
    # 关闭检测
    if item.status == 0:
        old_data.status = 0
    # 开启检测
    elif item.status == 1:
        # 获取当前时间
        current_time = datetime.now()
        if (datetime.strptime(str(old_data.exp_time), "%Y-%m-%d") - current_time).days >= 0:
            old_data.status = 1
        else:
            old_data.status = 2
    else:
        return resp_400(message='非法传参')
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching ssl: {e}")
        return resp_400(message='修改错误')
    retrieved_data = await Ssl.get_or_none(id=item.id)  # 使用刚刚创建的数据的ID
    resp_data = {
        'id': retrieved_data.id,
        'first_domain_id': retrieved_data.first_domain_id,
        'server_ids': retrieved_data.server_ids,
        'certificate_domain': retrieved_data.certificate_domain,
        'status': retrieved_data.status
    }
    return resp_200(data=resp_data, message='修改成功')


@ssl.post('/refresh', summary='刷新证书')
async def refresh_ssl():
    await db_ask_ssl()
    return resp_200(message='调用成功')


@ssl.post('/refresh/{ssl_id}', summary='刷新单个证书')
async def refresh_ssl(ssl_id: int):
    await db_ask_ssl(ssl_id)
    return resp_200(message='调用成功')
