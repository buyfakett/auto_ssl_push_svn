# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/22 9:46
import json
import logging
import os

import requests
from pyexec_shell.exec_shell import exec_shell, check_file
from pyssh_util.ssh_util import SSHClient
from pysvn_util.svn_util import SVNClient

from models.ssl import Ssl
from settings import setting
from pycheck_domain.check_domain import check_ssl


class SslFunction(object):
    def __init__(self, svn_user=str(setting.SVN_USER),
                 svn_passwd=str(setting.SVN_PASSWD),
                 mail=str(setting.SVN_MAIL),
                 server_host=str(setting.SERVER_HOST),
                 server_passwd=str(setting.SERVER_PASSWORD)):
        self.svn_user = svn_user
        self.svn_passwd = svn_passwd
        self.mail = mail
        self.server_host = server_host
        self.server_passwd = server_passwd

    def ask_ssl(self, aliyun_access_key: str, aliyun_access_secret: str, domain: str, ssl_id: int):
        """
        获取ssl证书
        :param aliyun_access_key:       阿里云access_key
        :param aliyun_access_secret:    阿里云access_secret
        :param domain:                  域名
        """
        with open('./temp/' + 'credentials.ini', encoding="utf-8", mode="a") as f:
            f.write(f'dns_aliyun_access_key = {aliyun_access_key}\n')
            f.write(f'dns_aliyun_access_key_secret = {aliyun_access_secret}')
        with open('./temp/' + 'setup.sh', encoding="utf-8", mode="a") as f:
            f.write('docker run -id --rm \\\n')
            f.write('--name certbot \\\n')
            f.write('-v /etc/letsencrypt:/etc/letsencrypt \\\n')
            f.write('-v /auto_ssl_push_svn/credentials.ini:/data/credentials.ini \\\n')
            f.write('-v /auto_ssl_push_svn/log/:/var/log/letsencrypt/ \\\n')
            f.write('registry.cn-hangzhou.aliyuncs.com/buyfakett/certbot-dns-aliyun \\\n')
            f.write("certonly --authenticator=dns-aliyun --dns-aliyun-credentials='/data/credentials.ini' \\\n")
            f.write(f' -d {domain} -m {self.mail} \\\n')
            f.write('--non-interactive \\\n')
            f.write('--agree-tos \\\n')
            f.write('--preferred-challenges dns \\\n')
            f.write("--manual-cleanup-hook 'aliyun-dns clean'")
        # 复制配置文件到运行目录
        ssh = SSHClient(host=self.server_host, password=self.server_passwd)
        ssh.execute_command('mkdir /auto_ssl_push_svn')
        ssh.upload_file(os.getcwd() + '/temp/credentials.ini', '/auto_ssl_push_svn/credentials.ini')
        ssh.upload_and_execute_script(os.getcwd() + '/temp/setup.sh', '/auto_ssl_push_svn/setup.sh')
        os.remove(os.getcwd() + '/temp/credentials.ini')
        os.remove(os.getcwd() + '/temp/setup.sh')
        # 运行申请证书容器
        exec_shell('/bin/bash /auto_ssl_push_svn/setup.sh')
        # 判断是否是泛域名，如果是泛域名生成的文件夹是不带*的
        if not domain.startswith('*'):
            ssl_path = f'/etc/letsencrypt/live/{domain}'
        else:
            ssl_path = f'/etc/letsencrypt/live/{domain[2:]}'
        if not check_file(ssl_path, 'cert*.pem'):
            logging.error(f'没有成功申请证书 {domain}，原因未知')
            return False
        try:
            ssl_data = Ssl.get(id=ssl_id)
        except Exception as e:
            # 处理异常，可以打印或记录错误信息
            logging.error(f"Error fetching server: {e}")
            return False
        start_time, end_time = check_ssl(f'/etc/letsencrypt/live/{domain}')
        if end_time - ssl_data.exp_time <= int(setting.CONFIG_DIFFER_DAY):
            logging.error(f'没有成功申请证书 {domain}，证书到期时间比设定时间更短')
            return False
        # 更新证书的到期时间
        ssl_data.status = 1
        ssl_data.register_time = start_time
        ssl_data.exp_time = end_time
        try:
            ssl_data.save()
        except Exception as e:
            logging.error(f"Error fetching ssl: {e}")
            return False
        return True

    def upload_svn(self, hostname: str, repo_url: str, domain: str):
        """
        下载证书并上传到svn
        :param hostname:            hostname
        :param repo_url:            svn克隆地址
        :param domain:              域名

        """
        exec_shell('mkdir -p ' + os.getcwd() + '/temp/svn')
        # 上传至svn
        svn_client = SVNClient(repo_url=repo_url, working_copy_path=os.getcwd() + '/temp/svn',
                               username=self.svn_user, password=self.svn_passwd)
        checkout_output, checkout_error, checkout_code = svn_client.checkout()
        logging.info(f'检出日志: {checkout_output}')
        logging.error(f'检出错误: {checkout_error}')
        logging.info(f'检出返回码: {checkout_code}')

        # 判断是否是泛域名，如果是泛域名生成的文件夹是不带*的
        if not domain.startswith('*'):
            exec_shell(f'cp -f /etc/letsencrypt/live/{domain}/cert*.pem /app/temp/svn/{hostname}/ssl/{domain}.cer')
            exec_shell(f'cp -f /etc/letsencrypt/live/{domain}/privkey*.pem /app/temp/svn/{hostname}/ssl/{domain}.key')
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/{domain}.key")
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/{domain}.cer")
        else:
            exec_shell(f'cp -f /etc/letsencrypt/live/{domain[2:]}/cert*.pem /app/temp/svn/{hostname}/ssl/_{domain[1:]}.cer')
            exec_shell(f'cp -f /etc/letsencrypt/live/{domain[2:]}/privkey*.pem /app/temp/svn/{hostname}/ssl/_{domain[1:]}.key')
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/_{domain[1:]}.key")
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/_{domain[1:]}.cer")

        commit_output, commit_error, commit_code = svn_client.commit(f'更新{domain}证书')
        logging.info(f'提交日志: {commit_output}')
        logging.error(f'提交错误: {commit_error}')
        logging.info(f'提交返回码: {commit_code}')

        message = f' {domain} 证书更新成功，已推送至 {repo_url} ！！！'
        if setting.PUSH_TYPE == 'ding':
            push_data = {
                'msgtype': 'text',
                'text': {
                    'content': message
                }
            }
            push_url = "https://oapi.dingtalk.com/robot/send?access_token=" + setting.PUSH_DING_ACCESS_TOKEN
            response = requests.post(push_url, json=push_data)
            if json.loads(response.text)['errcode'] == 0:
                logging.info("推送钉钉：" + json.loads(response.text)['errmsg'])
            else:
                logging.error('推送错误')

        exec_shell('rm -rf ' + os.getcwd() + '/temp/svn')
