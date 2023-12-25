import logging

from fastapi import APIRouter
from pydantic import BaseModel
from models.first_domain import First_domain
from .base import resp_200, resp_400
from typing import List, Optional

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


@domain.get('/list', response_model=List[DomainModelList], summary='获取域名列表')
async def get_domain():
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
    is_delete: Optional[bool] = False


@domain.put('/add', summary='添加域名')
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


@domain.delete('/delete/{domain_id}', summary='删除域名')
async def delete_domain(domain_id: int):
    try:
        await First_domain.get(id=domain_id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这条数据')
    try:
        await First_domain.filter(id=domain_id).delete()
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='删除错误')
    return resp_200(message='删除成功')


class EditDomainModel(BaseModel):
    id: int
    domain: Optional[str]
    domain_manufacturer: Optional[str]
    domain_account_key: Optional[str]
    domain_account_secret: Optional[str]
    is_delete: Optional[bool]


@domain.post('/edit', summary='编辑域名')
async def edit_domain(item: EditDomainModel):
    try:
        old_data = await First_domain.get(id=item.id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有查到该条数据')
    old_data.domain = item.domain
    old_data.domain_manufacturer = item.domain_manufacturer
    old_data.domain_account_key = item.domain_account_key
    old_data.domain_account_secret = item.domain_account_secret
    old_data.is_delete = item.is_delete
    try:
        await old_data.save()
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='修改错误')
    return resp_200(message='修改成功')
