# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/12/29 15:59
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.base import resp_200, resp_400
from api.oauth2 import create_token, verify_token
from models.user import User
from tt_util.aes_util import md5

user = APIRouter()


class LoginModel(BaseModel):
    user: str
    password: str


@user.post('/login', summary='登录')
async def login(item: LoginModel):
    user_data = await User.get()
    if item.user != user_data.user:
        return resp_400(message='账号错误')
    if md5(item.password) != user_data.password:
        return resp_400(message='密码错误')
    token = create_token(user_data.id)
    return resp_200(message='登录成功', data={
        'token': token
    })


class ChangeUserModel(BaseModel):
    old_user: str
    old_password: str
    user: str
    password: str


@user.post('/change', summary='修改账号')
async def change_user(item: ChangeUserModel, token: str = Depends(verify_token)):
    user_data = await User.get()
    if item.old_user != user_data.user:
        return resp_400(message='账号错误')
    if md5(item.old_password) != user_data.password:
        return resp_400(message='密码错误')
    user_data.user = item.user
    user_data.password = md5(item.password)
    try:
        await user_data.save()
    except Exception as e:
        logging.error(f"Error fetching user: {e}")
        return resp_400(message='修改错误')
    token_data = create_token(user_data.id)
    return resp_200(message='修改成功', data={
        'token': token_data
    })
