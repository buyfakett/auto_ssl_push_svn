# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/20 17:12
import logging
import os

from fastapi import APIRouter
from util.yaml_util import read_yaml
from api.base import resp_200, resp_400
from util.ssh import SSHClient

test1 = APIRouter()


@test1.get('/test')
async def test():
    dns_aliyun_access_key = 123
    dns_aliyun_access_key_secret = 456
    with open('./temp/' + 'credentials.ini', encoding="utf-8", mode="a") as f:
        f.write(f'dns_aliyun_access_key = {dns_aliyun_access_key}\n')
        f.write(f'dns_aliyun_access_key_secret = {dns_aliyun_access_key_secret}')
    ssh = SSHClient(read_yaml('host', 'config'), read_yaml('password', 'config'))
    ssh.upload_file(os.getcwd() + '/temp/credentials.ini', '/root/credentials.ini')
    ssh.close()
    logging.info('123')
    os.remove(os.getcwd() + '/temp/credentials.ini')
    return resp_200(message='上传配置文件成功')
