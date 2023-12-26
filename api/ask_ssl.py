# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/11/22 9:46
import logging
import os

from api.base import resp_400
from tt_util.exec_shell import exec_shell
from tt_util.ssh_util import SSHClient
from tt_util.svn_util import SVNClient
from tt_util.yaml_util import read_yaml


class SslFunction(object):
    def __init__(self, aliyun_access_key=read_yaml('aliyun_access_key', 'config'),
                 aliyun_access_secret=read_yaml('aliyun_access_secret', 'config'),
                 repo_url=read_yaml('repo_url', 'config'),):
        self.aliyun_access_key = aliyun_access_key
        self.aliyun_access_secret = aliyun_access_secret
        self.repo_url = repo_url

    def ask_ssl(self, domain: str, hostname: str, server_host: str, server_password: str):
        """
        获取ssl证书并上传到svn
        :param domain:                  域名
        :param hostname:                hostname
        :param server_host:             ip
        :param server_password:         密码
        :return:
        """
        mail = read_yaml('mail', 'config')
        # 上传配置文件
        with open('./temp/' + 'credentials.ini', encoding="utf-8", mode="a") as f:
            f.write(f'dns_aliyun_access_key = {self.aliyun_access_key}\n')
            f.write(f'dns_aliyun_access_key_secret = {self.aliyun_access_secret}')
        ssh = SSHClient(host=server_host, password=server_password)
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
            f.write('-v /auto_ssl_push_svn/credentials.ini:/data/credentials.ini \\\n')
            f.write('-v /auto_ssl_push_svn/log/:/var/log/letsencrypt/ \\\n')
            f.write('registry.cn-hangzhou.aliyuncs.com/buyfakett/certbot-dns-aliyun \\\n')
            f.write("certonly --authenticator=dns-aliyun --dns-aliyun-credentials='/data/credentials.ini' \\\n")
            f.write(f' -d {domain} -m {mail} \\\n')
            f.write('--non-interactive \\\n')
            f.write('--agree-tos \\\n')
            f.write('--preferred-challenges dns \\\n')
            f.write("--manual-cleanup-hook 'aliyun-dns clean'")
        try:
            ssh.upload_and_execute_script(os.getcwd() + '/temp/setup.sh', '/auto_ssl_push_svn/setup.sh')
        except Exception as e:
            logging.error(e)
            return resp_400(message='上传/执行失败')
        ssh.close()
        os.remove(os.getcwd() + '/temp/setup.sh')
        # 上传至svn
        svn_client = SVNClient(repo_url=self.repo_url, working_copy_path=os.getcwd() + '/temp/svn',
                               username=read_yaml('svn_user', 'config'),
                               password=read_yaml('svn_passwd', 'config'))
        checkout_output, checkout_error, checkout_code = svn_client.checkout()
        logging.info(f'检出日志: {checkout_output}')
        logging.error(f'检出错误: {checkout_error}')
        logging.info(f'检出返回码: {checkout_code}')
        delete_svn_temp = 'rm -rf ' + os.getcwd() + '/temp/svn'

        ssh = SSHClient(host=server_host, password=server_password)
        if not domain.startswith('*'):
            if not ssh.wait_for_file(f'/etc/letsencrypt/live/{domain}/cert.pem'):
                # 在文件存在时执行你的代码
                exec_shell(delete_svn_temp)
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
            if not ssh.wait_for_file(f'/etc/letsencrypt/live/{domain[2:]}/cert.pem'):
                # 在文件存在时执行你的代码
                exec_shell(delete_svn_temp)
                return resp_400(message='申请证书失败')
            ssh.download_file(f'/etc/letsencrypt/live/{domain[2:]}/cert.pem',
                              os.getcwd() + f'/temp/svn/{hostname}/ssl/_{domain[1:]}.cer')
            ssh.download_file(f'/etc/letsencrypt/live/{domain[2:]}/privkey.pem',
                              os.getcwd() + f'/temp/svn/{hostname}/ssl/_{domain[1:]}.key')
            ssh.execute_command('rm -rf /auto_ssl_push_svn')
            ssh.close()

            svn_client.add(f"/app/temp/svn/{hostname}/ssl/_{domain[1:]}.key")
            svn_client.add(f"/app/temp/svn/{hostname}/ssl/_{domain[1:]}.cer")

        commit_output, commit_error, commit_code = svn_client.commit('Committing changes')
        logging.info(f'提交日志: {commit_output}')
        logging.error(f'提交错误: {commit_error}')
        logging.info(f'提交返回码: {commit_code}')

        exec_shell(delete_svn_temp)
        logging.info('上传成功')
