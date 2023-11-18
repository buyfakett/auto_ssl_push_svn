import logging

from fastapi import APIRouter, Form, File, UploadFile, Request
from pydantic import BaseModel
import os
from models.first_domain import First_domain
from .base import resp_200, resp_400
from typing import Union, List

domain = APIRouter()


class DomainModel(BaseModel):
    id: int
    domain: str
    domain_manufacturer: str
    domain_account_key: str
    domain_account_secret: str

    class Config:
        from_orm = True
        from_attributes = True


@domain.get('/list', response_model=List[DomainModel])
async def get_domain():
    global domains
    try:
        domains = await First_domain.filter(is_delete=False).order_by('id')
    except Exception as e:
        # 处理异常，可以打印或记录错误信息
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='Internal Server Error')
    # 将数据库模型转换为响应模型
    response_data = [DomainModel.from_orm(domain).dict() for domain in domains]
    return resp_200(data=response_data)


@domain.put('/add')
async def add_domain():
    return {}


@domain.delete('/delete')
async def delete_domain():
    return {}


@domain.post('/edit')
async def edit_domain():
    return {}
