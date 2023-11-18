import logging

from fastapi import APIRouter, Form, File, UploadFile, Request
from pydantic import BaseModel
import os, json
from models.first_domain import First_domain
from .base import resp_200, resp_400
from typing import Union, List
from fastapi.encoders import jsonable_encoder

domain = APIRouter()


class DomainModelList(BaseModel):
    id: int
    domain: str
    domain_manufacturer: str
    domain_account_key: str
    domain_account_secret: str

    class Config:
        from_orm = True
        from_attributes = True


@domain.get('/list', response_model=List[DomainModelList])
async def get_domain():
    global domains
    try:
        domains = await First_domain.filter(is_delete=False).order_by('id')
    except Exception as e:
        # 处理异常，可以打印或记录错误信息
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='查询错误')
    # 将数据库模型转换为响应模型
    response_data = [DomainModelList.from_orm(domain).dict() for domain in domains]
    return resp_200(data=response_data)


class AddDomainModel(BaseModel):
    domain: str
    domain_manufacturer: str
    domain_account_key: str
    domain_account_secret: str
    is_delete: bool = False


@domain.put('/add')
async def add_domain(item: AddDomainModel):
    data = {
        "domain": item.domain,
        "domain_manufacturer": item.domain_manufacturer,
        "domain_account_key": item.domain_account_key,
        "domain_account_secret": item.domain_account_secret,
        "is_delete": item.is_delete,
    }
    if data['domain_manufacturer'] != 'ali':
        return resp_400(401, '暂时不支持该厂商域名')
    try:
        await First_domain.create(**data)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='插入错误')
    return resp_200(message='插入成功')


@domain.delete('/delete')
async def delete_domain():
    return {}


@domain.post('/edit')
async def edit_domain():
    return {}
