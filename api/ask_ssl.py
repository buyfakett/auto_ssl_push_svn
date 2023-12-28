# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/22 9:46
import logging
import os

from api.base import resp_400
from tt_util.exec_shell import exec_shell, check_file
from tt_util.ssh_util import SSHClient
from tt_util.svn_util import SVNClient
from tt_util.yaml_util import read_yaml


class SslFunction(object):
    def __init__(self, svn_user=read_yaml('svn_user', 'config'),
                 svn_passwd=read_yaml('svn_passwd', 'config'),
                 mail=read_yaml('mail', 'config')):
        self.svn_user = svn_user
        self.svn_passwd = svn_passwd
        self.mail = mail

        # 初始化申请证书服务器的信息，在ask_ssk方法入参里赋值，可以让别的方法调
        self.server_host = None
        self.server_password = None

    def ask_ssl(self, aliyun_access_key: str, aliyun_access_secret: str, domain: str):
        """
        获取ssl证书
        :param aliyun_access_key:       阿里云access_key
        :param aliyun_access_secret:    阿里云access_secret
        :param domain:                  域名
        :param server_host:             申请证书服务器的ip
        :param server_password:         申请证书服务器的密码
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
        ssh = SSHClient(host=read_yaml('server_host', 'config'), password=read_yaml('server_password', 'config'))
        ssh.execute_command('mkdir /auto_ssl_push_svn')
        ssh.upload_file(os.getcwd() + '/temp/credentials.ini', '/auto_ssl_push_svn/credentials.ini')
        ssh.upload_and_execute_script(os.getcwd() + '/temp/setup.sh', '/auto_ssl_push_svn/setup.sh')
        os.remove(os.getcwd() + '/temp/credentials.ini')
        os.remove(os.getcwd() + '/temp/setup.sh')
        # 运行申请证书容器
        exec_shell('/bin/bash /auto_ssl_push_svn/setup.sh')
        # 判断是否是泛域名，如果是泛域名生成的文件夹是不带*的
        if not domain.startswith('*'):
            if not check_file(f'/etc/letsencrypt/live/{domain}', 'cert*.pem'):
                return resp_400(message='没有成功申请证书')
        else:
            if not check_file(f'/etc/letsencrypt/live/{domain[2:]}', 'cert*.pem'):
                return resp_400(message='没有成功申请证书')

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
            exec_shell(f'cp /etc/letsencrypt/live/{domain}/cert*.pem /app/temp/svn/{hostname}/ssl/{domain}.cer')
            exec_shell(f'cp /etc/letsencrypt/live/{domain}/privkey*.pem /app/temp/svn/{hostname}/ssl/{domain}.key')
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/{domain}.key")
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/{domain}.cer")
        else:
            exec_shell(f'cp /etc/letsencrypt/live/{domain[2:]}/cert*.pem /app/temp/svn/{hostname}/ssl/_{domain[1:]}.cer')
            exec_shell(f'cp /etc/letsencrypt/live/{domain[2:]}/privkey*.pem /app/temp/svn/{hostname}/ssl/_{domain[1:]}.key')
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/_{domain[1:]}.key")
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/_{domain[1:]}.cer")

        commit_output, commit_error, commit_code = svn_client.commit(f'更新{domain}证书')
        logging.info(f'提交日志: {commit_output}')
        logging.error(f'提交错误: {commit_error}')
        logging.info(f'提交返回码: {commit_code}')

        exec_shell('rm -rf ' + os.getcwd() + '/temp/svn')
