# -*- coding: utf-8 -*-            
# @Author : buyfakett
# @Time : 2023/12/28 15:09
import ast
import logging
from datetime import datetime
from typing import Optional

from util.ask_ssl import SslFunction
from models.first_domain import first_domain
from models.server import Server
from models.ssl import Ssl
from settings import setting


async def db_ask_ssl(ssl_id: Optional[int] = None):
    today = datetime.today().date()
    if ssl_id is None:
        # 查询所有证书
        ssl_datas = await Ssl.all()
        for ssl_data in ssl_datas:
            # 如果证书到期时间为空或者配置的天内过期，就续费
            ask_flag = False
            if ssl_data.exp_time is None:
                logging.info(f"证书到期时间为空，开始续费")
                ask_flag = True
            else:
                differ_day = (ssl_data.exp_time - today).days
                if differ_day <= int(setting.CONFIG_DIFFER_DAY):
                    logging.info(f"证书到期时间小于{setting.CONFIG_DIFFER_DAY}，开始续费")
                    ask_flag = True
            # 判断是否不进行续费
            if ssl_data.status == 0:
                ask_ssl = False
            if ask_flag:
                first_domain_data = await first_domain.get(id=ssl_data.first_domain_id)
                if first_domain_data.domain_manufacturer == 'ali':
                    ask_ssl = SslFunction()
                    # 获取ssl证书
                    if await ask_ssl.ask_aliyun_ssl(aliyun_access_key=first_domain_data.domain_account_key,
                                       aliyun_access_secret=first_domain_data.domain_account_secret,
                                       domain=ssl_data.certificate_domain,
                                       ssl_id=ssl_data.id):
                        list_server = ast.literal_eval(ssl_data.server_ids)
                        servers = await Server.filter(id__in=list_server)
                        for server in servers:
                            logging.info('本次上传：' + server.hostname)
                            # 分发证书
                            ask_ssl.upload_svn(hostname=server.hostname,
                                               repo_url=server.webroot,
                                               domain=ssl_data.certificate_domain)
                else:
                    logging.error('域名厂商暂时不支持')
    else:
        ssl_data = await Ssl.get(id=ssl_id)
        # 如果证书到期时间为空或者配置的天内过期，就续费
        ask_flag = False
        if ssl_data.exp_time is None:
            logging.info(f"证书到期时间为空，开始续费")
            ask_flag = True
        else:
            differ_day = (ssl_data.exp_time - today).days
            if differ_day <= int(setting.CONFIG_DIFFER_DAY):
                logging.info(f"证书到期时间小于{setting.CONFIG_DIFFER_DAY}，开始续费")
                ask_flag = True
        # 判断是否不进行续费
        if ssl_data.status == 0:
            ask_ssl = False
        if ask_flag:
            first_domain_data = await first_domain.get(id=ssl_data.first_domain_id)
            if first_domain_data.domain_manufacturer == 'ali':
                ask_ssl = SslFunction()
                # 获取ssl证书
                if await ask_ssl.ask_aliyun_ssl(aliyun_access_key=first_domain_data.domain_account_key,
                                   aliyun_access_secret=first_domain_data.domain_account_secret,
                                   domain=ssl_data.certificate_domain,
                                   ssl_id=ssl_data.id):
                    list_server = ast.literal_eval(ssl_data.server_ids)
                    servers = await Server.filter(id__in=list_server)
                    for server in servers:
                        logging.info('本次上传：' + server.hostname)
                        # 分发证书
                        ask_ssl.upload_svn(hostname=server.hostname,
                                           repo_url=server.webroot,
                                           domain=ssl_data.certificate_domain)
            else:
                logging.error('域名厂商暂时不支持')
