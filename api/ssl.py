import logging

from fastapi import APIRouter
from pydantic import BaseModel
from models.first_domain import First_domain
from .base import resp_200, resp_400
from typing import List

ssl = APIRouter()


@ssl.get('/list')
async def get_ssl():
    return resp_200()


@ssl.put('/add')
async def add_ssl():
    return resp_200()


@ssl.delete('/delete/{ssl_id}')
async def delete_ssl():
    return resp_200()


@ssl.post('/edit')
async def edit_ssl():
    return resp_200()
