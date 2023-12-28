# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/12/28 15:09
import ast
import logging
from datetime import datetime

from tt_util.aes_util import decrypt_aes
from tt_util.yaml_util import read_yaml

from api.ask_ssl import SslFunction
from models.first_domain import first_domain
from models.server import Server
from models.ssl import Ssl


async def db_ask_ssl():
    ssl_datas = await Ssl.all()
    for ssl_data in ssl_datas:
        # 如果证书到期时间为空或者5天内过期，就续费
        ask_flag = False
        if ssl_data.exp_time is None:
            ask_flag = True
        else:
            differ_day = (ssl_data.exp_time - datetime.today().date()).days
            if differ_day < 5:
                ask_flag = True
        if ask_flag:
            first_domain_data = await first_domain.get(id=ssl_data.first_domain_id)
            ask_ssl = SslFunction()
            # 获取ssl证书
            ask_ssl.ask_ssl(aliyun_access_key=first_domain_data.domain_account_key,
                            aliyun_access_secret=first_domain_data.domain_account_secret,
                            domain=ssl_data.certificate_domain)
            list_server = ast.literal_eval(ssl_data.server_ids)
            servers = await Server.filter(id__in=list_server)
            for server in servers:
                logging.info('本次上传：' + server.hostname)
                # 分发证书
                ask_ssl.upload_svn(hostname=server.hostname,
                                   repo_url=server.webroot,
                                   domain=ssl_data.certificate_domain)
