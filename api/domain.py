import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from models.first_domain import first_domain
from pyresp.pyresp import resp_200, resp_400
from typing import List, Optional

from pyoauth2_util.oauth2 import verify_token

domain = APIRouter(dependencies=[Depends(verify_token)])


class DomainModelList(BaseModel):
    id: int
    domain: str
    domain_manufacturer: str
    domain_account_key: str
    domain_account_secret: str

    class Config:
        from_orm = True
        from_attributes = True

    @classmethod
    def mask_sensitive_data(cls, value: str) -> str:
        if len(value) >= 4:
            return value[:2] + '*' * (len(value) - 4) + value[-2:]
        else:
            return '*' * len(value)


@domain.get('/list', response_model=List[DomainModelList], summary='获取域名列表')
async def get_domain():
    try:
        domains = await first_domain.filter(is_delete=False).order_by('id')
    except Exception as e:
        # 处理异常，可以打印或记录错误信息
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='查询错误')
    data_list = []
    for domain in domains:
        domain_dict = DomainModelList.from_orm(domain).dict()
        # 序列化 datetime 字段
        domain_dict['domain_account_key'] = DomainModelList.mask_sensitive_data(domain_dict['domain_account_key'])
        domain_dict['domain_account_secret'] = DomainModelList.mask_sensitive_data(domain_dict['domain_account_secret'])
        data_list.append(domain_dict)
    response_data = {
        'items': data_list,
        'total': len(data_list)
    }
    return resp_200(data=response_data, message='查询成功')


class AddDomainModel(BaseModel):
    domain: str
    domain_manufacturer: str
    domain_account_key: str
    domain_account_secret: str
    is_delete: Optional[bool] = False


@domain.put('/add', summary='添加域名')
async def add_domain(item: AddDomainModel):
    if item.domain_manufacturer != 'ali':
        return resp_400(401, '暂时不支持该厂商域名')
    try:
        add_data = await first_domain.create(**item.dict())
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='插入错误')
    resp_data = {
        'id': add_data.id,
        'domain': add_data.domain,
        'domain_manufacturer': add_data.domain_manufacturer,
        "domain_account_key": item.domain_account_key,
        'domain_account_secret': add_data.domain_account_secret,
        'is_delete': add_data.is_delete,
    }
    return resp_200(data=resp_data, message='新增成功')


@domain.delete('/delete/{domain_id}', summary='删除域名')
async def delete_domain(domain_id: int):
    try:
        await first_domain.get(id=domain_id)
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='没有这条数据')
    try:
        await first_domain.filter(id=domain_id).delete()
    except Exception as e:
        logging.error(f"Error fetching domains: {e}")
        return resp_400(message='删除错误')
    return resp_200(message='删除成功')


class EditDomainModel(BaseModel):
    id: int
    domain: str
    domain_manufacturer: str
    domain_account_key: str
    domain_account_secret: str
    is_delete: Optional[bool] = False


@domain.post('/edit', summary='编辑域名')
async def edit_domain(item: EditDomainModel):
    if item.domain_manufacturer != 'ali':
        return resp_400(401, '暂时不支持该厂商域名')
    try:
        old_data = await first_domain.get(id=item.id)
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
    retrieved_data = await first_domain.get_or_none(id=item.id)  # 使用刚刚创建的数据的ID
    resp_data = {
        'id': retrieved_data.id,
        'domain': retrieved_data.domain,
        'domain_manufacturer': retrieved_data.domain_manufacturer,
        'domain_account_key': retrieved_data.domain_account_key,
        'domain_account_secret': retrieved_data.domain_account_secret,
        'is_delete': retrieved_data.is_delete
    }
    return resp_200(data=resp_data, message='修改成功')
