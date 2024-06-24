#!/bin/bash

mall=$1
domain=$2
aws_access_key=$3
aws_access_secret=$4

[[ -z ${domain} ]] && { echo "参数 domain 必传" && exit 1; }
[[ -z ${mall} ]] && { echo "参数 mall 必传" && exit 1; }
[[ -z ${aws_access_key} ]] && { echo "参数 aws_access_key 必传" && exit 1; }
[[ -z ${aws_access_secret} ]] && { echo "参数 aws_access_secret 必传" && exit 1; }

if [ ! -f "/auto_ssl_push_svn/letsencrypt/renewal/${domain}.conf" ];then
    cmd_args="certonly --noninteractive --agree-tos --dns-route53 -d ${domain} -m ${mall}"
else
    cmd_args="renew --cert-name ${domain} --force-renewal"
fi

docker run -i --rm \
--name ali-certbot \
-v /auto_ssl_push_svn/letsencrypt:/etc/letsencrypt \
-v /auto_ssl_push_svn/log/:/var/log/letsencrypt/ \
-e AWS_ACCESS_KEY_ID=${aws_access_key} \
-e AWS_SECRET_ACCESS_KEY=${aws_access_secret} \
registry.cn-hangzhou.aliyuncs.com/buyfakett/certbot-dns-aliyun ${cmd_args}
