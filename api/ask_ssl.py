# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/22 9:46
import logging
import os

from api.base import resp_400
from util.exec_shell import exec_shell
from util.ssh import SSHClient
from util.svn import SVNClient
from util.yaml_util import read_yaml


def ask_ssl(aliyun_access_key: str, aliyun_access_secret: str, domain: str, hostname: str):
    mail = read_yaml('mail', 'config')
    # 上传配置文件
    with open('./temp/' + 'credentials.ini', encoding="utf-8", mode="a") as f:
        f.write(f'dns_aliyun_access_key = {aliyun_access_key}\n')
        f.write(f'dns_aliyun_access_key_secret = {aliyun_access_secret}')
    ssh = SSHClient(host=read_yaml('server_host', 'config'), password=read_yaml('server_password', 'config'),
                    port=read_yaml('server_port', 'config'), username=read_yaml('server_user', 'config'))
    try:
        ssh.execute_command('mkdir /auto_ssl_push_svn')
        ssh.upload_file(os.getcwd() + '/temp/credentials.ini', '/auto_ssl_push_svn/credentials.ini')
    except Exception as e:
        logging.error(e)
        return resp_400(message='上传配置文件失败')
    os.remove(os.getcwd() + '/temp/credentials.ini')
    logging.info('上传配置文件成功')
    # 申请证书成功
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
    try:
        ssh.upload_and_execute_script(os.getcwd() + '/temp/setup.sh', '/auto_ssl_push_svn/setup.sh')
    except Exception as e:
        logging.error(e)
        return resp_400(message='上传/执行失败')
    ssh.close()
    os.remove(os.getcwd() + '/temp/setup.sh')
    # 上传至svn
    svn_client = SVNClient(repo_url=read_yaml('svn_url', 'config'), working_copy_path=os.getcwd() + '/temp/svn',
                           username=read_yaml('svn_user', 'config'),
                           password=read_yaml('svn_passwd', 'config'))
    checkout_output, checkout_error, checkout_code = svn_client.checkout()
    logging.info(f'检出日志: {checkout_output}')
    logging.error(f'检出错误: {checkout_error}')
    logging.info(f'检出返回码: {checkout_code}')

    ssh = SSHClient(host=read_yaml('server_host', 'config'), password=read_yaml('server_password', 'config'),
                    port=read_yaml('server_port', 'config'), username=read_yaml('server_user', 'config'))
    if not domain.startswith('*'):
        if not ssh.wait_for_file(f'/etc/letsencrypt/live/{domain}/cert.pem'):
            # 在文件存在时执行你的代码
            return resp_400(message='申请证书失败')
        ssh.download_file(f'/etc/letsencrypt/live/{domain}/cert.pem',
                          os.getcwd() + f'/temp/svn/{hostname}/ssl/{domain}.cer')
        ssh.download_file(f'/etc/letsencrypt/live/{domain}/privkey.pem',
                          os.getcwd() + f'/temp/svn/{hostname}/ssl/{domain}.key')
        ssh.execute_command('rm -rf /auto_ssl_push_svn')
        ssh.close()

        svn_client.add(f"/app/temp/svn/{hostname}/ssl/{domain}.key")
        svn_client.add(f"/app/temp/svn/{hostname}/ssl/{domain}.cer")
    else:
        if not ssh.wait_for_file(f'/etc/letsencrypt/live/{domain[2:]}*/cert.pem'):
            # 在文件存在时执行你的代码
            return resp_400(message='申请证书失败')
        ssh.download_file(f'/etc/letsencrypt/live/{domain}*/cert.pem',
                          os.getcwd() + f'/temp/svn/{hostname}/ssl/{domain}.cer')
        ssh.download_file(f'/etc/letsencrypt/live/{domain}*/privkey.pem',
                          os.getcwd() + f'/temp/svn/{hostname}/ssl/{domain}.key')
        ssh.execute_command('rm -rf /auto_ssl_push_svn')
        ssh.close()

        svn_client.add(f"/app/temp/svn/{hostname}/ssl/_{domain[1:]}.key")
        svn_client.add(f"/app/temp/svn/{hostname}/ssl/_{domain[1:]}.cer")

    commit_output, commit_error, commit_code = svn_client.commit('Committing changes')
    logging.info(f'提交日志: {commit_output}')
    logging.error(f'提交错误: {commit_error}')
    logging.info(f'提交返回码: {commit_code}')

    delete_svn_temp = 'rm -rf ' + os.getcwd() + '/temp/svn'

    exec_shell(delete_svn_temp)
    logging.info('上传成功')
