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


@test1.get('/upload1')
async def upload_ini():
    dns_aliyun_access_key = '1'
    dns_aliyun_access_key_secret = '2'
    with open('./temp/' + 'credentials.ini', encoding="utf-8", mode="a") as f:
        f.write(f'dns_aliyun_access_key = {dns_aliyun_access_key}\n')
        f.write(f'dns_aliyun_access_key_secret = {dns_aliyun_access_key_secret}')
    ssh = SSHClient(read_yaml('host', 'config'), read_yaml('password', 'config'))
    ssh.upload_file(os.getcwd() + '/temp/credentials.ini', '/root/credentials.ini')
    ssh.close()
    os.remove(os.getcwd() + '/temp/credentials.ini')
    return resp_200(message='上传配置文件成功')


@test1.get('/upload2')
async def upload_setup():
    domain = '1'
    mail = '2'
    with open('./temp/' + 'setup.sh', encoding="utf-8", mode="a") as f:
        f.write('docker run -id --rm \\\n')
        f.write('--name certbot \\\n')
        f.write('-v /etc/letsencrypt:/etc/letsencrypt \\\n')
        f.write('-v ./credentials.ini:/data/credentials.ini \\\n')
        f.write('registry.cn-hangzhou.aliyuncs.com/buyfakett/certbot-dns-aliyun \\\n')
        f.write("certonly --authenticator=dns-aliyun --dns-aliyun-credentials='/data/credentials.ini'\\\n")
        f.write(f' -d {domain} -m {mail}')
        f.write('--non-interactive \\')
        f.write('--agree-tos \\')
        f.write('--preferred-challenges dns \\')
        f.write("--manual-cleanup-hook 'aliyun-dns clean'")
    ssh = SSHClient(read_yaml('host', 'config'), read_yaml('password', 'config'))
    ssh.upload_and_execute_script(os.getcwd() + '/temp/setup.sh', '/root/setup.sh')
    ssh.close()
    os.remove(os.getcwd() + '/temp/setup.sh')
    return resp_200(message='上传配置文件成功')
    # 成功标识符：Successfully received certificate.