# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/20 17:12
import ast
import logging
import os, subprocess
from datetime import datetime, timedelta

import dns.resolver

from fastapi import APIRouter, Depends

from api.ask_ssl import SslFunction
from tt_util.svn_util import SVNClient
from tt_util.exec_shell import exec_shell
from tt_util.yaml_util import read_yaml
from pyresp.pyresp import resp_200, resp_400
from tt_util.ssh_util import SSHClient

from tt_util.check_domain import check_domain

from pyoauth2_util.oauth2 import verify_token, create_token
from models.server import Server

test1 = APIRouter()


@test1.get('/test111')
def test111(token_data: str = Depends(verify_token)):
    logging.info(f'调用成功,token={token_data}')
    return resp_200(message=f'调用成功,token={token_data}')

@test1.get('/test222')
def test222():
    token_data = create_token(1)
    return resp_200(message=f'{token_data}')

@test1.get('/2')
async def t2():
    date = datetime.today().date() + timedelta(days=90)
    print(date)
    return resp_200()


@test1.get('/1')
async def database():
    data = '[10]'
    q = ast.literal_eval(data)
    servers = await Server.filter(id__in=q)
    for server in servers:
        print(server.ip)


@test1.get('/domain')
async def test_domain(domain):
    if not check_domain(domain):
        return resp_400()
    else:
        return resp_200()


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


@test1.get('/upload3')
async def upload_svn():
    svn_client = SVNClient(repo_url=read_yaml('svn_url', 'config'), working_copy_path='/app/temp/svn',
                           username=read_yaml('svn_user', 'config'),
                           password=read_yaml('svn_passwd', 'config'))
    checkout_output, checkout_error, checkout_code = svn_client.checkout()
    logging.info(f'检出日志: {checkout_output}')
    logging.error(f'检出错误: {checkout_error}')
    logging.info(f'检出返回码: {checkout_code}')

    command = 'cp /app/main.py /app/temp/svn/main2.py'

    exec_shell(command)

    add_output, add_error, add_code = svn_client.add("/app/temp/svn/main2.py")
    logging.info(f'增加日志: {add_output}')
    logging.error(f'增加错误: {add_error}')
    logging.info(f'增加返回码: {add_code}')

    commit_output, commit_error, commit_code = svn_client.commit('Committing changes')
    logging.info(f'提交日志: {commit_output}')
    logging.error(f'提交错误: {commit_error}')
    logging.info(f'提交返回码: {commit_code}')

    command2 = 'rm -rf /app/temp/svn'
    exec_shell(command2)


@test1.get('/ask_ssl')
async def test_ask_ssl(aliyun_access_key: str, aliyun_access_secret: str, domain: str, hostname: str):
    ask_ssl = SslFunction()
    ask_ssl.ask_ssl(aliyun_access_key, aliyun_access_secret, domain, hostname)
    return resp_200()
