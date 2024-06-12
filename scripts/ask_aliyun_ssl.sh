#!/bin/bash

mall=$1
domain=$2

[[ -z ${domain} ]] && { echo "参数 domain 必传" && exit 1; }
[[ -z ${mall} ]] && { echo "参数 mall 必传" && exit 1; }

cd ${WORKDIR}
if [ ! -f "/auto_ssl_push_svn/letsencrypt/renewal/${domain}.conf" ];then
    cmd_args="certonly --noninteractive --agree-tos --authenticator dns-aliyun -d ${domain} -m ${mall} --dns-aliyun-credentials /data/aliyun.ini"
else
    cmd_args="renew --cert-name ${domain} --force-renewal"
fi

docker run -i --rm \
--name ali-certbot \
-v /auto_ssl_push_svn/letsencrypt:/etc/letsencrypt \
-v /auto_ssl_push_svn/credentials.ini:/data/credentials.ini \
-v /auto_ssl_push_svn/log/:/var/log/letsencrypt/ \
registry.cn-hangzhou.aliyuncs.com/buyfakett/certbot-dns-aliyun ${cmd_args}
