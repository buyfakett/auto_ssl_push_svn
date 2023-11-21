# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/20 17:12
import logging
import os, subprocess

from fastapi import APIRouter

from util.svn import SVNClient
from util.exec_shell import exec_shell
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


@test1.get('/upload3')
async def upload_svn():
    svn_client = SVNClient(repo_url=read_yaml('svn_url', 'config'), working_copy_path='/app/temp/svn',
                           username=read_yaml('svn_user', 'config'),
                           password=read_yaml('svn_passwd', 'config'))
    checkout_output, checkout_error, checkout_code = svn_client.checkout()
    logging.info(f'检出日志: {checkout_output}')
    logging.error(f'Checkout Error: {checkout_error}')
    logging.info(f'Checkout Return Code: {checkout_code}')

    command = 'cp /app/main.py /app/temp/svn/main2.py'

    # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # output, error = process.communicate()
    # print(output.decode('utf-8'), error.decode('utf-8'), process.returncode)
    exec_shell(command)

    update_output, update_error, update_code = svn_client.add("/app/temp/svn/main2.py")
    logging.info(f'Update Output: {update_output}')
    logging.error(f'Update Error: {update_error}')
    logging.info(f'Update Return Code: {update_code}')

    commit_output, commit_error, commit_code = svn_client.commit('Committing changes')
    logging.info(f'Commit Output: {commit_output}')
    logging.error(f'Commit Error: {commit_error}')
    logging.info(f'Commit Return Code: {commit_code}')

    command2 = 'rm -rf /app/temp/svn'
    exec_shell(command2)
