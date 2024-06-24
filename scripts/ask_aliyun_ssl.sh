#!/bin/bash

mall=$1
domain=$2
aliyun_access_key=$3
aliyun_access_secret=$4

[[ -z ${domain} ]] && { echo "参数 domain 必传" && exit 1; }
[[ -z ${mall} ]] && { echo "参数 mall 必传" && exit 1; }
[[ -z ${aliyun_access_key} ]] && { echo "参数 aliyun_access_key 必传" && exit 1; }
[[ -z ${aliyun_access_secret} ]] && { echo "参数 aliyun_access_secret 必传" && exit 1; }

cat << EOF > /auto_ssl_push_svn/aliyun.ini
dns_aliyun_access_key = ${aliyun_access_key}
dns_aliyun_access_key_secret = ${aliyun_access_secret}
EOF

chmod 600 /auto_ssl_push_svn/aliyun.ini

if [ ! -f "/auto_ssl_push_svn/letsencrypt/renewal/${domain}.conf" ];then
    cmd_args="certonly --noninteractive --agree-tos --authenticator dns-aliyun -d ${domain} -m ${mall} --dns-aliyun-credentials /data/aliyun.ini"
else
    cmd_args="renew --cert-name ${domain} --force-renewal"
fi

docker run -i --rm \
--name ali-certbot \
-v /auto_ssl_push_svn/letsencrypt:/etc/letsencrypt \
-v /auto_ssl_push_svn/aliyun.ini:/data/aliyun.ini \
-v /auto_ssl_push_svn/log/:/var/log/letsencrypt/ \
registry.cn-hangzhou.aliyuncs.com/buyfakett/certbot-dns-aliyun ${cmd_args}
